# actions.py

from . import navidrome
import random
from datetime import datetime, UTC
from . import widgets as Widgets

# -- MISC --

def toggle_star(window, model_id:str):
    integration = navidrome.get_current_integration()
    if model_id in integration.loaded_models:
        model = integration.loaded_models[model_id]
        if model.starred:
            if integration.unstar(model.id):
                model.starred = None
        else:
            if integration.star(model.id):
                model.starred = datetime.now(UTC).isoformat(timespec='microseconds').replace('+00:00', 'Z')

# -- SONG --

def play_song(window, model_id:str):
    queue_page = window.playing_navigationview.find_page('queue')
    if model_id in queue_page.song_list_el.get_all_ids():
        integration = navidrome.get_current_integration()
        integration.loaded_models.get('currentSong').songId = model_id
    else:
        queue_page.replace_queue([model_id])

def play_song_next(window, model_id:str):
    queue_page = window.playing_navigationview.find_page('queue')
    queue_page.play_next([model_id])

def play_song_later(window, model_id:str):
    queue_page = window.playing_navigationview.find_page('queue')
    queue_page.play_later([model_id])

# -- ALBUM --

def show_album(window, model_id:str):
    window.main_navigationview.push(Widgets.AlbumPage(model_id))

def play_album(window, model_id:str):
    integration = navidrome.get_current_integration()
    album = integration.loaded_models.get(model_id)

    if album:
        integration.verifyAlbum(album.id, force_update=True, use_threading=False)
        queue_page = window.playing_navigationview.find_page('queue')
        queue_page.replace_queue([s.get('id') for s in album.song])

def play_album_next(window, model_id:str):
    integration = navidrome.get_current_integration()
    album = integration.loaded_models.get(model_id)

    if album:
        integration.verifyAlbum(album.id, force_update=True, use_threading=False)
        queue_page = window.playing_navigationview.find_page('queue')
        queue_page.play_next([s.get('id') for s in album.song])

def play_album_later(window, model_id:str):
    integration = navidrome.get_current_integration()
    album = integration.loaded_models.get(model_id)

    if album:
        integration.verifyAlbum(album.id, force_update=True, use_threading=False)
        queue_page = window.playing_navigationview.find_page('queue')
        queue_page.play_later([s.get('id') for s in album.song])

def play_album_shuffle(window, model_id:str):
    integration = navidrome.get_current_integration()
    album = integration.loaded_models.get(model_id)

    if album:
        integration.verifyAlbum(album.id, force_update=True, use_threading=False)
        queue_page = window.playing_navigationview.find_page('queue')
        song_list = [s.get('id') for s in album.song]
        random.shuffle(song_list)
        queue_page.replace_queue(song_list)

# -- PLAYLIST --

def show_playlist(window, model_id:str):
    window.main_navigationview.push(Widgets.PlaylistPage(model_id))

def play_playlist(window, model_id:str):
    integration = navidrome.get_current_integration()
    playlist = integration.loaded_models.get(model_id)

    if playlist:
        integration.verifyPlaylist(playlist.id, force_update=True, use_threading=False)
        queue_page = window.playing_navigationview.find_page('queue')
        queue_page.replace_queue([s.get('id') for s in playlist.entry])

def play_playlist_next(window, model_id:str):
    integration = navidrome.get_current_integration()
    playlist = integration.loaded_models.get(model_id)

    if playlist:
        integration.verifyPlaylist(playlist.id, force_update=True, use_threading=False)
        queue_page = window.playing_navigationview.find_page('queue')
        queue_page.play_next([s.get('id') for s in playlist.entry])

def play_playlist_later(window, model_id:str):
    integration = navidrome.get_current_integration()
    playlist = integration.loaded_models.get(model_id)

    if playlist:
        integration.verifyPlaylist(playlist.id, force_update=True, use_threading=False)
        queue_page = window.playing_navigationview.find_page('queue')
        queue_page.play_later([s.get('id') for s in playlist.entry])

def play_playlist_shuffle(window, model_id:str):
    integration = navidrome.get_current_integration()
    playlist = integration.loaded_models.get(model_id)

    if playlist:
        integration.verifyPlaylist(playlist.id, force_update=True, use_threading=False)
        queue_page = window.playing_navigationview.find_page('queue')
        song_list = [s.get('id') for s in playlist.entry]
        random.shuffle(song_list)
        queue_page.replace_queue(song_list)

# -- ARTIST --

def show_artist(window, model_id:str):
    window.main_navigationview.push(Widgets.ArtistPage(model_id))
