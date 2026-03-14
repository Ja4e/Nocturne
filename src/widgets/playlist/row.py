# row.py

from gi.repository import Gtk, Adw, GLib, Gdk
from ...navidrome import get_current_integration
from ..containers import ContextContainer
import threading

@Gtk.Template(resource_path='/com/jeffser/Nocturne/playlist/row.ui')
class PlaylistRow(Adw.ActionRow):
    __gtype_name__ = 'NocturnePlaylistRow'

    cover_el = Gtk.Template.Child()

    def __init__(self, id:str):
        self.id = id
        integration = get_current_integration()
        integration.verifyPlaylist(self.id)
        super().__init__()
        self.set_action_target_value(GLib.Variant.new_string(self.id))

        integration.connect_to_model(self.id, 'name', self.update_name)
        integration.connect_to_model(self.id, 'songCount', self.update_song_count)
        integration.connect_to_model(self.id, 'coverArt', self.update_cover)

    def generate_context_menu(self) -> ContextContainer:
        context_dict = {
            _("Play"): {
                "icon-name": "media-playback-start-symbolic",
                "action-name": "app.play_playlist"
            },
            _("Shuffle"): {
                "icon-name": "media-playlist-shuffle-symbolic",
                "action-name": "app.play_playlist_shuffle"
            },
            _("Play Next"): {
                "icon-name": "list-high-priority-symbolic",
                "action-name": "app.play_playlist_next"
            },
            _("Play Later"): {
                "icon-name": "list-low-priority-symbolic",
                "action-name": "app.play_playlist_later"
            },
            _("Edit"): {
                "icon-name": "document-edit-symbolic",
                "action-name": "app.update_playlist"
            },
            _("Delete"): {
                "css": ["error"],
                "icon-name": "user-trash-symbolic",
                "action-name": "app.delete_playlist"
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

    def update_song_count(self, songCount:int):
        if songCount == 1:
            self.set_subtitle(_("1 Song"))
        else:
            self.set_subtitle(_("{} Songs").format(songCount))

    @Gtk.Template.Callback()
    def on_context_button_active(self, button, gparam):
        button.get_popover().set_child(self.generate_context_menu())
