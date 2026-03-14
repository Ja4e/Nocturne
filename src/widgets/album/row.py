# row.py

from gi.repository import Gtk, Adw, GLib, Gdk
from ...navidrome import get_current_integration
from ..containers import ContextContainer
import threading

@Gtk.Template(resource_path='/com/jeffser/Nocturne/album/row.ui')
class AlbumRow(Adw.ActionRow):
    __gtype_name__ = 'NocturneAlbumRow'

    cover_el = Gtk.Template.Child()

    def __init__(self, id:str):
        self.id = id
        integration = get_current_integration()
        integration.verifyAlbum(self.id)
        super().__init__()
        self.set_action_target_value(GLib.Variant.new_string(self.id))

        integration.connect_to_model(self.id, 'name', self.update_name)
        integration.connect_to_model(self.id, 'artist', self.update_artist)
        integration.connect_to_model(self.id, 'coverArt', self.update_cover)

    def generate_context_menu(self) -> ContextContainer:
        context_dict = {
            _("Play"): {
                "icon-name": "media-playback-start-symbolic",
                "action-name": "app.play_album"
            },
            _("Shuffle"): {
                "icon-name": "playlist-shuffle-symbolic",
                "action-name": "app.play_album_shuffle"
            },
            _("Play Next"): {
                "icon-name": "list-high-priority-symbolic",
                "action-name": "app.play_album_next"
            },
            _("Play Later"): {
                "icon-name": "list-low-priority-symbolic",
                "action-name": "app.play_album_later"
            },
            _("Add To Playlist"): {
                "icon-name": "playlist-symbolic",
                "action-name": "app.add_album_to_playlist"
            }
        }
        return ContextContainer(context_dict, self.id)

    def update_cover(self, coverArt:str=None):
        def update():
            integration = get_current_integration()
            paintable = integration.getCoverArt(self.id, 480)
            if isinstance(paintable, Gdk.MemoryTexture):
                GLib.idle_add(self.cover_el.set_from_paintable, paintable)
            else:
                GLib.idle_add(self.cover_el.set_from_paintable, None)
        threading.Thread(target=update).start()

    def update_name(self, name:str):
        self.set_title(GLib.markup_escape_text(name))
        self.set_name(GLib.markup_escape_text(name))

    def update_artist(self, artist:str):
        self.set_subtitle(artist)

    @Gtk.Template.Callback()
    def on_context_button_active(self, button, gparam):
        button.get_popover().set_child(self.generate_context_menu())

