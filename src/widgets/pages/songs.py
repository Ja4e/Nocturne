# songs.py

from gi.repository import Gtk, Adw, GLib, GObject, Gio
from ...integrations import get_current_integration, models
from ..song import SongRow, SongSmallRow
import threading

@Gtk.Template(resource_path='/com/jeffser/Nocturne/pages/songs.ui')
class SongsPage(Adw.NavigationPage):
    __gtype_name__ = 'NocturneSongsPage'

    search_entry = Gtk.Template.Child()
    main_stack = Gtk.Template.Child()
    list_el = Gtk.Template.Child()
    wrapbox_el = Gtk.Template.Child()
    end_stack = Gtk.Template.Child()
    scrolledwindow = Gtk.Template.Child()
    offset = 0
    searching = False

    def reload(self):
        if len(list(self.list_el.list_el)) + len(list(self.wrapbox_el)) == 0:
            GLib.idle_add(self.on_search, self.search_entry)

    def search(self, count=30):
        if self.searching:
            return
        self.searching = True
        query = self.search_entry.get_text()
        integration = get_current_integration()
        search_results = integration.search(
            query=query,
            songCount=count,
            songOffset=self.offset
        )
        for song_id in search_results.get('song'):
            results_list = [row for row in list(self.list_el.list_el) if row.id == song_id]
            if len(results_list) > 0:
                GLib.idle_add(results_list[0].set_visible, True)
            else:
                row = SongRow(song_id)
                GLib.idle_add(self.list_el.list_el.append, row)

            results_wrapbox = [button for button in list(self.wrapbox_el) if button.id == song_id]
            if len(results_wrapbox) > 0:
                GLib.idle_add(results_wrapbox[0].set_visible, True)
            else:
                button = SongSmallRow(song_id)
                GLib.idle_add(self.wrapbox_el.append, button)

        GLib.idle_add(self.end_stack.set_visible_child_name, 'end' if len(search_results.get('song')) < count else 'loading')
        self.offset += count
        self.searching = False
        GLib.idle_add(self.update_visibility)

    @Gtk.Template.Callback()
    def on_search(self, search_entry):
        self.offset = 0
        for row in list(self.list_el.list_el) + list(self.wrapbox_el):
            row.set_visible(False)
        threading.Thread(target=self.search).start()

    @Gtk.Template.Callback()
    def scroll_edge_reached(self, scrolledwindow, pos):
        if pos == Gtk.PositionType.BOTTOM and self.end_stack.get_visible_child_name() == 'loading':
            threading.Thread(target=self.search).start()

    @Gtk.Template.Callback()
    def toggle_view_changed(self, toggle_group, ud):
        def check_scrollbar():
            va = self.scrolledwindow.get_vadjustment()
            if va.get_upper() <= va.get_page_size():
                threading.Thread(target=self.search, args=(60,)).start()

        if toggle_group.get_active_name() == "grid":
            GLib.timeout_add(1000, check_scrollbar)

    def update_visibility(self):
        for row in list(self.list_el.list_el) + list(self.wrapbox_el):
            if row.get_visible():
                self.main_stack.set_visible_child_name('content')
                return
        self.main_stack.set_visible_child_name('no-content')
