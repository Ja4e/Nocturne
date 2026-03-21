# local.py

from gi.repository import Gtk, GLib, GObject, Gdk, Gio, GdkPixbuf
from . import secret, models
import requests, random, threading, favicon, io, pathlib, re
from PIL import Image
from mutagen import File
from ..constants import MUSIC_DIR

class Local(GObject.Object):
    __gtype_name__ = 'NocturneIntegrationLocal'

    music_dir = GObject.Property(type=str, default=MUSIC_DIR)
    supported_extensions = ('.mp3', '.flac', '.m4a', '.ogg', '.wav')

    def __init__(self):
        self.loaded_models = {
            'currentSong': models.CurrentSong()
        }
        self.update_loaded_models()

    def update_loaded_models(self):
        # Goes through the whole directory retrieving all the metadata
        audio_data_list = []
        path_obj = pathlib.Path(self.music_dir)

        for file_path in path_obj.rglob("*"):
            if file_path.suffix.lower() in self.supported_extensions:
                try:
                    audio = File(file_path)
                    if audio is None:
                        continue

                    # Making Song Model
                    song = {
                        'id': "SONG:{}".format(file_path),
                        'path': file_path,
                        'duration': audio.info.length if hasattr(audio, 'info') else 0,
                        'title': "",
                        'album': "",
                        'artist': "",
                        'artists': []
                    }

                    if file_path.suffix.lower() == '.mp3':
                        # ID3 Mapping
                        song['title'] = str(audio.get('TIT2', file_path.name.removesuffix(file_path.suffix)))
                        song['album'] = str(audio.get('TALB'))
                        artists = [artist.strip() for artist in str(audio.get('TPE1')).split(';')]
                        if len(artists) > 0:
                            song['artist'] = artists[0]
                            for artist in artists:
                                song['artists'].append({
                                    'id': "ARTIST:{}".format(artist),
                                    'name': artist
                                })
                    else:
                        # Vorbis/FLAC/MP4 Mapping
                        song["title"] = audio.get('title', [file_path.name.removesuffix(file_path.suffix)])[0]
                        song["album"] = audio.get('album', [""])[0]
                        artists = [artist.strip() for artist in audio.get('artist', [])[1:] + (audio.get('artist')[0].split(';') if len(audio.get('artist', [])) > 0 else [])]
                        if len(artists) > 0:
                            song['artist'] = artists[0]
                            for artist in artists:
                                song['artists'].append({
                                    'id': "ARTIST:{}".format(artist),
                                    'name': artist
                                })

                    song["artistId"] = "ARTIST:{}".format(song.get("artist")) if song.get('artist') else ""
                    song["albumId"] = "ALBUM:{}".format(song.get("album")) if song.get('album') else ""

                    self.loaded_models[song.get('id')] = models.Song(**song)

                    # Making Album Model
                    if song.get('albumId'):
                        if song.get('albumId') in self.loaded_models:
                            self.loaded_models.get(song.get('albumId')).song.append({'id': song.get('id')})
                        else:
                            album = {
                                'id': song.get('albumId'),
                                'path': song.get('path'),
                                'name': song.get('album'),
                                'artist': song.get('artist'),
                                'artistId': song.get('artistId'),
                                'song': [{'id': song.get('id')}]
                            }
                            self.loaded_models[album.get('id')] = models.Album(**album)

                    # Making Artist Model
                    for a_dict in song.get('artists', []):
                        if a_dict.get('id'):
                            if a_dict.get('id') not in self.loaded_models:
                                artist = {
                                    'id': a_dict.get('id'),
                                    'path': song.get('path'),
                                    'name': a_dict.get('name'),
                                    'album': [],
                                    'albumCount': 0
                                }
                                self.loaded_models[artist.get('id')] = models.Artist(**artist)

                            # Add album
                            album_list = self.loaded_models.get(a_dict.get('id')).album
                            if not any([album.get('id') == song.get('albumId') for album in album_list]):
                                self.loaded_models.get(a_dict.get('id')).album.append({'id': song.get('albumId')})
                                self.loaded_models.get(a_dict.get('id')).albumCount += 1

                except Exception as e:
                    print('Error loading items:', e)

    # ----------- #

    def connect_to_model(self, id:str, parameter:str, callback:callable, use_gtk_thread:bool=True) -> str:
        # returns connection id so it can be disconnected if needed, mostly used by currentSong
        connection_id = ""
        if id in self.loaded_models:
            if use_gtk_thread:
                connection_id = self.loaded_models[id].connect(
                    'notify::{}'.format(parameter),
                    lambda *_, parameter=parameter, id=id: GLib.idle_add(callback, self.loaded_models[id].get_property(parameter))
                )
                GLib.idle_add(callback, self.loaded_models[id].get_property(parameter))
            else:
                connection_id = self.loaded_models[id].connect(
                    'notify::{}'.format(parameter),
                    lambda *_, parameter=parameter, id=id: callback(self.loaded_models[id].get_property(parameter))
                )
                callback(self.loaded_models[id].get_property(parameter))

        if parameter == "coverArt":
            self.getCoverArt(id)
        return connection_id

    def get_stream_url(self, song_id:str) -> str:
        model = self.loaded_models.get(song_id)
        if model.isRadio:
            return model.streamUrl
        return 'file://{}'.format(model.path)

    def getRadioCoverArtWithBytes(self, id:str=None) -> tuple:
        # returns bytes, Gdk.Paintable or None, None
        if id:
            if model := self.loaded_models.get(id):
                homepage_url = ""
                if model.gdkPaintable:
                    return model.gdkPaintableBytes, model.gdkPaintable
                if model.homePageUrl:
                    icons = favicon.get(model.homePageUrl)
                    if len(icons) > 0:
                        try:
                            response = requests.get(icons[0].url, timeout=5)
                            response.raise_for_status()
                            response_bytes = response.content
                            stream = io.BytesIO(response_bytes)
                            png_bytes = b''
                            with Image.open(stream) as img:
                                img = img.convert("RGBA")
                                png_buffer = io.BytesIO()
                                img.save(png_buffer, format="PNG")
                                png_bytes = png_buffer.getvalue()
                            texture = Gdk.Texture.new_from_bytes(GLib.Bytes.new(png_bytes))
                            model.set_property('gdkPaintableBytes', png_bytes)
                            model.set_property('gdkPaintable', texture)
                            return model.get_property('gdkPaintableBytes'), model.get_property('gdkPaintable')
                        except Exception as e:
                            pass

        return None, None

    def getCoverArtWithBytes(self, id:str=None) -> tuple:
        # returns bytes, Gdk.Paintable or None, None
        if id:
            if model := self.loaded_models.get(id):
                if isinstance(model, models.Song) and model.isRadio:
                    return self.getRadioCoverArtWithBytes(id)
                if model.gdkPaintable:
                    return model.gdkPaintableBytes, model.gdkPaintable

                if not model.get_property('coverArt'):
                    model.set_property('coverArt', random.randint(0,1000))

                audio_file = File(model.path)
                if audio_file is None:
                    return None, None

                raw_data = None
                if 'APIC:' in audio_file:
                    raw_data = audio_file.get('APIC:').data
                elif hasattr(audio_file, 'pictures') and audio_file.pictures:
                    raw_data = audio_file.pictures[0].data
                elif 'covr' in audio_file:
                    raw_data = audio_file.get('covr')[0]

                if not raw_data:
                    return None, None

                try:
                    gbytes = GLib.Bytes.new(raw_data)
                    texture = Gdk.Texture.new_from_bytes(gbytes)
                    model.set_property('gdkPaintableBytes', raw_data)
                    model.set_property('gdkPaintable', texture)
                    return model.get_property('gdkPaintableBytes'), model.get_property('gdkPaintable')
                except Exception as e:
                    pass
        return None, None

    def getCoverArt(self, id:str=None) -> Gdk.Paintable:
        # Returns a paintable at the specified size, should be used directly in GTK without modifications
        return self.getCoverArtWithBytes(id)[1]

    def ping(self) -> bool:
        # Implemented from Navidrome, just a check
        return True

    def getAlbumList(self, list_type:str="recent", size:int=10, offset:int=0) -> list:
        # list_type and offset are not implemented yet
        album_list = [id for id in list(self.loaded_models) if id.startswith('ALBUM:')]
        if list_type == "random":
            random.shuffle(album_list)
        return album_list[offset:size]

    def getArtists(self, size:int=10) -> list:
        return [id for id in list(self.loaded_models) if id.startswith('ARTIST:')][:size]

    def getPlaylists(self) -> list:
        # not implemented
        return []

    def verifyArtist(self, id:str, force_update:bool=False, use_threading:bool=True):
        # no need
        return

    def verifyAlbum(self, id:str, force_update:bool=False, use_threading:bool=True):
        # no need
        return

    def verifyPlaylist(self, id:str, force_update:bool=False, use_threading:bool=True):
        # not implemented
        return

    def verifySong(self, id:str, force_update:bool=False, use_threading:bool=True):
        # no need
        return

    def start(self, id:str) -> bool:
        # not implemented
        return False

    def unstart(self, id:str) -> bool:
        # not implemented
        return False

    def getPlayQueue(self) -> tuple:
        # not implemented
        return None, []

    def savePlayQueue(self, id_list:list, current:str, position:int) -> bool:
        # not implemented
        return False

    def getSimilarSongs(self, id:str, count:int=20) -> list:
        # not implemented
        return []

    def getRandomSongs(self, size:int=20) -> list:
        songs = [id for id in list(self.loaded_models) if id.startswith('SONG:')]
        return random.sample(songs, k=min(size, len(songs)))

    def getLyrics(self, track_name:str, artist_name:str, album_name:str, duration:int) -> dict:
        # This uses the LRCLIB public API
        # Duration is in seconds
        response = requests.get('https://lrclib.net/api/get', params={
            'track_name': track_name,
            'artist_name': artist_name,
            'album_name': album_name,
            'duration': duration
        })
        return response.json()

    def search(self, query:str, artistCount:int=0, artistOffset:int=0, albumCount:int=0, albumOffset:int=0, songCount:int=0, songOffset:int=0) -> dict:
        all_artists = [model for id, model in self.loaded_models.items() if id.startswith('ARTIST:')]
        all_albums = [model for id, model in self.loaded_models.items() if id.startswith('ALBUM:')]
        all_songs = [model for id, model in self.loaded_models.items() if id.startswith('SONG:')]

        return {
            'artist': [model.id for model in all_artists if re.search(query, model.name, re.IGNORECASE)][artistOffset:artistCount],
            'album': [model.id for model in all_albums if re.search(query, model.name, re.IGNORECASE) or re.search(query, model.artist, re.IGNORECASE)][albumOffset:albumCount],
            'song': [model.id for model in all_songs if re.search(query, model.title, re.IGNORECASE) or re.search(query, model.album, re.IGNORECASE) or re.search(query, model.artist, re.IGNORECASE)][songOffset:songCount]
        }

    def getInternetRadioStations(self) -> list:
        # not implemented
        return []

    def createInternetRadioStation(self, name:str, streamUrl:str, homepageUrl:str) -> bool:
        # not implemented
        return False

    def updateInternetRadioStation(self, id:str, name:str, streamUrl:str, homepageUrl:str) -> bool:
        # not implemented
        return False

    def deleteInternetRadioStation(self, id:str) -> bool:
        # not implemented
        return False

    def createPlaylist(self, name:str=None, playlistId:str=None, songId:list=[]) -> str:
        # not implemented
        return ""

    def updatePlaylist(self, playlistId:str, songIdToAdd:list=[], songIndexToRemove:list=[]) -> bool:
        # not implemented
        return False

    def deletePlaylist(self, id:str) -> bool:
        # not implemented
        return False

    def scrobble(self, id:str):
        # not implemented
        pass
