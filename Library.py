#!/usr/bin/env python

# Use native plist if available, it is much faster
try:
  from Foundation import NSDictionary
  def _readlib(path):
    return NSDictionary.dictionaryWithContentsOfFile_(path)
except ImportError:
  import plistlib
  def _readlib(path):
    return plistlib.readPlist(path)

import urllib

class Library(object):
  """
  This class abstracts access to iTunes Music Library which is just a xml plist
  """
  def __init__(self, libraryxml='./iTunes Music Library.xml'):
    super(Library, self).__init__()
    self._library = _readlib(libraryxml)

  def playlists(self):
    """
    Returns the name of each playlist in the library
    """
    playlistnames = []
    playlists = self._library['Playlists']
    for playlist in playlists:
      playlistnames.append(playlist['Name'])

    return playlistnames

  def get_track(self, trackid):
      return self._library['Tracks'][trackid]

  def get_playlist(self, name, filterfunc=None):
    """
    Return the specified playlist. Each item in the returned list is a 
    2-tuple consisting of (track-id, track-file-path)
    """
    if not filterfunc:
      filterfunc = lambda x: True

    playlists = self._library['Playlists']
    trackdicts = []
    exists = False
    for playlist in playlists:
      if playlist['Name'] == name:
        trackdicts = playlist['Playlist Items']
        exists = True
        break

    if not exists:
      return None

    trackids = []
    for track in trackdicts:
      trackids.append(str(track['Track ID']))

    tracktuples = []
    for trackid in trackids:
      trackdict = self.get_track(trackid)
      if filterfunc(trackdict):
        tracklocation = trackdict['Location'] 
        tracklocation = tracklocation.replace('file://localhost','')
        tracklocation = urllib.unquote(tracklocation)

        tracktuples.append((trackid, tracklocation))

    return tracktuples
