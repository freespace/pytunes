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
        {'skip-artists':'Comma separated list of artists to skip, using shell-style case-insensitive matching',
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
    self._skip_artists = [x.strip() for x in skipArtistsOption.split(',')]

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
    def _filter(track):
      artist = track.get('Artist')
      skip = False
      if artist:
        for skippattern in self._skip_artists:
          if fnmatch.fnmatch(artist.lower(),skippattern.lower()):
            skip = True
            break

      return not skip

    pl=self._lib.get_playlist(playlistname, _filter)
    if not pl:
      print 'No such playlist (%s) or empty playlist'%(playlistname)
      return -1
    else:
      if unique:
        pl = set(pl)
        pl = list(pl)
      while True:
        if shuffle:
          print 'Shuffling playlist %s...'%(playlistname)
          random.shuffle(pl)

        for idx,ttuple in enumerate(pl):
          trackid = ttuple[0]
          trackpath = ttuple[1]

          track = self._lib.get_track(trackid)

          print '[%3d/%3d] %-24s %s'%(idx+1, len(pl), track['Artist'][0:24], track['Name'])
          call(MUSIC_PLAYER+[trackpath])

        if not repeat:
          break
    return 0


if __name__ == '__main__':
  import sys
  app = pytunes()
  sys.exit(app.process(sys.argv))
