#!/usr/bin/env python

import plistlib
import urllib

class Library(object):
  """
  This class abstracts access to iTunes Music Library which is just a xml plist
  """
  def __init__(self, libraryxml='./iTunes Music Library.xml'):
    super(Library, self).__init__()

    self._library = plistlib.readPlist(libraryxml)

  def playlists(self):
    """
    Returns the name of each playlist in the library
    """
    playlistnames = []
    playlists = self._library['Playlists']
    for playlist in playlists:
      playlistnames.append(playlist['Name'])

    return playlistnames

  def get_playlist(self, name):
    """
    Return the specified playlist. Each item in the returned list is a path to
    a file in the playlist
    """
    playlists = self._library['Playlists']
    trackdicts = []
    for playlist in playlists:
      if playlist['Name'] == name:
        trackdicts = playlist['Playlist Items']
        break

    trackids = []
    for track in trackdicts:
      trackids.append(str(track['Track ID']))

    trackfilepaths = []
    for trackid in trackids:
      trackdict = self._library['Tracks'][trackid]
      tracklocation = trackdict['Location'] 
      tracklocation = tracklocation.replace('file://localhost','')
      tracklocation = urllib.unquote(tracklocation)
      trackfilepaths.append(tracklocation)

    return trackfilepaths
