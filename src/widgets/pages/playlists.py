# playlists.py

from gi.repository import Gtk, Adw, GLib, GObject, Gio
from ...navidrome import get_current_integration, models
from ..playlist import PlaylistRow
import re

@Gtk.Template(resource_path='/com/jeffser/Nocturne/pages/playlists.ui')
class PlaylistsPage(Adw.NavigationPage):
    __gtype_name__ = 'NocturnePlaylistsPage'

    list_el = Gtk.Template.Child()

    def reload(self):
        # call in different thread
        integration = get_current_integration()
        playlists = integration.getPlaylists()
        for row in list(self.list_el):
            GLib.idle_add(self.list_el.remove, row)
        for id in playlists:
            GLib.idle_add(self.list_el.append, PlaylistRow(id))

    @Gtk.Template.Callback()
    def on_search(self, search_entry):
        query = search_entry.get_text()
        for child in list(self.list_el.list_el):
            child.set_visible(child.get_name() != 'GtkListBoxRow' and re.search(query, child.get_name(), re.IGNORECASE))
