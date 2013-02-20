#!/usr/bin/env python -u

from optmatch import OptionMatcher, optmatcher, optset
from Library import Library
from random import shuffle
from subprocess import call
from os.path import expandvars, expanduser, basename

class pytunes(OptionMatcher):
  """
  Right now this only plays the one playlist which I actually use. In the future
  we should add an options like -playlist which by itself prints all the available
  playlist. If a playlist name is given, then that playlist is played. 

  Additional options may include -shuffle and -repeat.
  """
  @optmatcher
  def main(self, 
      libraryOption="~/Music/iTunes/iTunes Music Library.xml", 
      playlistOption='list'):
    libpath = expanduser(libraryOption)
    libpath = expandvars(libpath)

    self._lib = Library(libpath)

    if playlistOption == 'list':
      return self.print_playlists()
    else:
      return self.play_playlist(playlistOption)

  def print_playlists(self):
    playlists = self._lib.playlists()
    print 'Playlists:'
    for pl in playlists:
      print '\t',pl

  def play_playlist(self, playlistname):
    pl=self._lib.get_playlist(playlistname)
    if not pl:
      print 'No such playlist (%s) or empty playlist'%(playlistname)
      return -1
    else:
      while True:
        print 'Shuffling playlist %s...'%(playlistname)
        shuffle(pl)
        for idx,track in enumerate(pl):
          print '[%d/%d] %s'%(idx+1, len(pl), basename(track))
          call(['mplayer', '-vo', 'none', '-really-quiet', track])


if __name__ == '__main__':
  import sys
  app = pytunes()
  sys.exit(app.process(sys.argv))

