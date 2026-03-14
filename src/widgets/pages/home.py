# home.py

from gi.repository import Gtk, Adw, GLib, Gst
from ...navidrome import get_current_integration
from ..album import AlbumButton
from ..artist import ArtistButton
from ..playlist import PlaylistButton
from ..song import SongSmallRow

@Gtk.Template(resource_path='/com/jeffser/Nocturne/pages/home.ui')
class HomePage(Adw.NavigationPage):
    __gtype_name__ = 'NocturneHomePage'

    song_wrapbox = Gtk.Template.Child()
    album_carousel = Gtk.Template.Child()
    artist_carousel = Gtk.Template.Child()
    playlist_carousel = Gtk.Template.Child()

    def reload(self):
        # call in different thread
        self.song_wrapbox.set_header(
            label=_("Songs"),
            icon_name="music-note-symbolic",
            page_tag="songs"
        )
        self.song_wrapbox.list_el.set_margin_start(10)
        self.song_wrapbox.list_el.set_margin_end(10)
        self.song_wrapbox.list_el.set_justify(Adw.JustifyMode.FILL)
        self.song_wrapbox.list_el.set_justify_last_line(True)
        self.song_wrapbox.list_el.set_child_spacing(5)
        self.song_wrapbox.list_el.set_line_spacing(5)
        self.update_song_list()

        self.album_carousel.set_header(
            label=_("Albums"),
            icon_name="music-queue-symbolic",
            page_tag="albums-all"
        )
        self.update_album_list()

        self.artist_carousel.set_header(
            label=_("Artists"),
            icon_name="music-artist-symbolic",
            page_tag="artists"
        )
        self.update_artist_list()

        self.playlist_carousel.set_header(
            label=_("Playlists"),
            icon_name="playlist-symbolic",
            page_tag="playlists"
        )
        self.update_playlist_list()

    def update_song_list(self):
        integration = get_current_integration()
        songs = integration.getRandomSongs(size=12)
        GLib.idle_add(self.song_wrapbox.set_widgets, [SongSmallRow(id) for id in songs])

    def update_album_list(self):
        integration = get_current_integration()
        albums = integration.getAlbumList(size=12)
        GLib.idle_add(self.album_carousel.set_widgets, [AlbumButton(id) for id in albums])

    def update_artist_list(self):
        integration = get_current_integration()
        artists = integration.getArtists(size=12)
        GLib.idle_add(self.artist_carousel.set_widgets, [ArtistButton(id) for id in artists])

    def update_playlist_list(self):
        integration = get_current_integration()
        playlists = integration.getPlaylists()
        GLib.idle_add(self.playlist_carousel.set_widgets, [PlaylistButton(id) for id in playlists])
