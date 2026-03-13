# row.py

from gi.repository import Gtk, Adw, GLib, Gdk
from ...navidrome import get_current_integration
import threading

@Gtk.Template(resource_path='/com/jeffser/Nocturne/playlist/row.ui')
class PlaylistRow(Adw.ActionRow):
    __gtype_name__ = 'NocturnePlaylistRow'

    cover_el = Gtk.Template.Child()
    play_el = Gtk.Template.Child()
    play_shuffle_el = Gtk.Template.Child()
    play_next_el = Gtk.Template.Child()
    play_later_el = Gtk.Template.Child()

    def __init__(self, id:str):
        self.id = id
        integration = get_current_integration()
        integration.verifyPlaylist(self.id)
        super().__init__()
        self.set_action_target_value(GLib.Variant.new_string(self.id))
        self.play_el.set_action_target_value(GLib.Variant.new_string(self.id))
        self.play_shuffle_el.set_action_target_value(GLib.Variant.new_string(self.id))
        self.play_next_el.set_action_target_value(GLib.Variant.new_string(self.id))
        self.play_later_el.set_action_target_value(GLib.Variant.new_string(self.id))

        integration.connect_to_model(self.id, 'name', self.update_name)
        integration.connect_to_model(self.id, 'songCount', self.update_song_count)
        integration.connect_to_model(self.id, 'coverArt', self.update_cover)

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
    def option_selected(self, button):
        button.get_ancestor(Gtk.MenuButton).popdown()

