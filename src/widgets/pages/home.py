# home.py

from gi.repository import Gtk, Adw, GLib, Gst
from ...navidrome import get_current_integration
from ..album import AlbumButton
from ..artist import ArtistButton
from ..playlist import PlaylistButton

@Gtk.Template(resource_path='/com/jeffser/Nocturne/pages/home.ui')
class HomePage(Adw.NavigationPage):
    __gtype_name__ = 'NocturneHomePage'

    album_carousel = Gtk.Template.Child()
    artist_carousel = Gtk.Template.Child()
    playlist_carousel = Gtk.Template.Child()

    def reload(self):
        # call in different thread
        self.album_carousel.set_header(
            label=_("Albums"),
            icon_name="music-queue-symbolic",
            page_tag="albums"
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

    def update_album_list(self):
        integration = get_current_integration()
        albums = integration.getAlbumList()
        GLib.idle_add(self.album_carousel.set_widgets, [AlbumButton(id) for id in albums])

    def update_artist_list(self):
        integration = get_current_integration()
        artists = integration.getArtists()
        GLib.idle_add(self.artist_carousel.set_widgets, [ArtistButton(id) for id in artists])

    def update_playlist_list(self):
        integration = get_current_integration()
        playlists = integration.getPlaylists()
        GLib.idle_add(self.playlist_carousel.set_widgets, [PlaylistButton(id) for id in playlists])
