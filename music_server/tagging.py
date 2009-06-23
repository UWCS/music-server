from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from os import popen

def get_name(file):
    try:
        info = get_info(file)
        return "%s -- %s -- %s" % (info['artist'][0],info['album'][0],info['title'][0])
    except ValueError:
        return ""
    except KeyError:
        return ""

def get_info(file):
    if file.endswith('mp3'):
        return MP3(file,ID3=EasyID3)
    elif file.endswith('flac'):
        return FLAC(file)
    elif file.endswith('ogg'):
        return OggVorbis(file)
    else:
        raise ValueError

def spotify_name(uri):
    p = popen('/home/music-server/music-server/music_server/name.sh '+uri)
    name = p.read()
    p.close()
    return name

