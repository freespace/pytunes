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
  def main(self, libraryOption="~/Music/iTunes/iTunes Music Library.xml"):
    libpath = expanduser(libraryOption)
    libpath = expandvars(libpath)

    lib = Library(libpath)

    print 'Loading library...'
    lush = lib.get_playlist('lush')
    while True:
      print 'Shuffling...'
      shuffle(lush)
      for track in lush:
        print '>',basename(track)
        call(['mplayer', '-vo', 'none', '-really-quiet', track])

    return 0

if __name__ == '__main__':
  import sys
  sys.exit(pytunes().process(sys.argv))

