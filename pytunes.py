#!/usr/bin/env python -u

from optmatch import OptionMatcher, optmatcher, optset
from Library import Library
from subprocess import call
from os.path import expandvars, expanduser, basename

import random
import fnmatch

MUSIC_PLAYER='mplayer -vo none -really-quiet'.split(' ')

class pytunes(OptionMatcher):
  def __init__(self):
    super(pytunes,self).__init__()
    self.setAliases({
      'r':'repeat',
      's':'shuffle',
      'u':'unique',
      'k':'skip-artists'
    })

    self.setUsageInfo(
        {'skip-artists':"""
          Comma separated list of artists to skip, using shell-style 
          case-insensitive matching. Adding a suffix of :n where n=0...10 will 
          skip the artist with n out of 10 times. e.g. *Sarah*:5 will skip
          artists who match *Sarah* 5 times out of 10""".strip().replace('\n','').replace('  ',''),
        'unique':'If given, duplicate entries in playlists will be removed'},
        None)

  @optmatcher
  def main(self,
      libraryOption="~/Music/iTunes/iTunes Music Library.xml",
      playlist='',
      shuffleFlag=False,
      repeatFlag=False,
      skipArtistsOption='',
      uniqueFlag=False):
    libpath = expanduser(libraryOption)
    libpath = expandvars(libpath)

    self._lib = Library(libpath)

    self._skip_weights = {}
    if skipArtistsOption:
      t = [x.strip() for x in skipArtistsOption.split(',')]

      for skippattern in t:
        if ':' in skippattern:
          newskippattern,skipweight = skippattern.rsplit(':')
          self._skip_weights[newskippattern] = int(skipweight)
        else:
          # default to skipping 10 times out of 10, i.e. always
          self._skip_weights[skippattern] = 10
      #print self._skip_weights

    if playlist == '':
      self.print_playlists()
      return 0
    else:
      return self.play_playlist(playlist, shuffleFlag, repeatFlag, uniqueFlag)

  def print_playlists(self):
    playlists = self._lib.playlists()
    print 'Playlists:'
    for pl in playlists:
      print '\t',pl

  def play_playlist(self, playlistname, shuffle, repeat, unique):
    def _filter(track, det=False):
      """
      det stands for deterministic. When it is true, all tracks that match are
      skipped. Otherwise skip weight is used to randomly determine if a track
      should be skipped
      """
      artist = track.get('Artist')
      if not artist:
        artist = ''
      skip = False
      for skippattern in self._skip_weights.keys():
        if fnmatch.fnmatch(artist.lower(),skippattern.lower()):
          if det:
            skip = True
          else:
            skipweight = self._skip_weights[skippattern]
            if skipweight and random.random()*10<skipweight: 
              skip = True
          break

      return not skip

    def _filterdet(track):
      return _filter(track, True)

    pl = self._lib.get_playlist(playlistname)
    if not pl:
      print 'No such playlist (%s) or empty playlist'%(playlistname)
      return -1
    else:
      # check whether the user has filtered out all tracks
      pl = self._lib.get_playlist(playlistname, _filterdet)

      # if pl is empty, then all tracks match something. At this point we need
      # to make sure SOME weights are smaller than 10
      if not pl:
        if min(self._skip_weights.values()) >= 10:
          print 'All tracks in playlist are to be skipped'
          return -2

      while True:
        # otherwise, we either have some songs that will never be skipped, or
        # some song have a probability of not being skipped. Iterate until we
        # have a non-empty playlist
        pl = []
        while not pl:
          pl=self._lib.get_playlist(playlistname, _filter)

        if unique:
          pl = set(pl)
          pl = list(pl)

        if shuffle:
          print 'Shuffling playlist %s...'%(playlistname)
          random.shuffle(pl)

        for idx,ttuple in enumerate(pl):
          trackid = ttuple[0]
          trackpath = ttuple[1]

          track = self._lib.get_track(trackid)
          artist = track.get('Artist')
          if artist:
            artist = artist[0:24]
          else:
            artist = 'Unknown'

          print '[%3d/%3d] %-24s %s'%(idx+1, len(pl), artist, track['Name'])
          call(MUSIC_PLAYER+[trackpath])

        if not repeat:
          break
    return 0


if __name__ == '__main__':
  import sys
  app = pytunes()
  sys.exit(app.process(sys.argv))
