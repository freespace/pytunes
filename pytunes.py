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
      's':'shuffle'
    })

    self.setUsageInfo(
        {'skip-artists':'Comma separated list of artists to skip, using shell-style case-insensitive matching'},

        None)

  """
  Right now this only plays the one playlist which I actually use. In the future
  we should add an options like -playlist which by itself prints all the available
  playlist. If a playlist name is given, then that playlist is played. 

  Additional options may include -shuffle and -repeat.
  """
  @optmatcher
  def main(self, 
      libraryOption="~/Music/iTunes/iTunes Music Library.xml", 
      playlist='',
      shuffleFlag=False,
      repeatFlag=False,
      skipArtistsOption=''):
    libpath = expanduser(libraryOption)
    libpath = expandvars(libpath)

    self._lib = Library(libpath)
    self._skip_artists = [x.strip() for x in skipArtistsOption.split(',')]

    if playlist == '':
      self.print_playlists()
      return 0
    else:
      return self.play_playlist(playlist, shuffleFlag, repeatFlag)

  def print_playlists(self):
    playlists = self._lib.playlists()
    print 'Playlists:'
    for pl in playlists:
      print '\t',pl

  def play_playlist(self, playlistname, shuffle, repeat):
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
      while True:
        if shuffle:
          print 'Shuffling playlist %s...'%(playlistname)
          random.shuffle(pl)

        for idx,track in enumerate(pl):
          print '[%d/%d] %s'%(idx+1, len(pl), basename(track))
          call(MUSIC_PLAYER+[track])

        if not repeat:
          break
    return 0


if __name__ == '__main__':
  import sys
  app = pytunes()
  sys.exit(app.process(sys.argv))

