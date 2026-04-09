# queue_page.py

from gi.repository import Gtk, Adw, GObject, GLib, Gio
from ..song import SongRow
from ...integrations import models, get_current_integration
import threading

@Gtk.Template(resource_path='/com/jeffser/Nocturne/playing/queue_page.ui')
class PlayingQueuePage(Gtk.ScrolledWindow):
    __gtype_name__ = 'NocturnePlayingQueuePage'

    song_list_el = Gtk.Template.Child()
    autoplay_row_el = Gtk.Template.Child()
    autoplay_spinner_el = Gtk.Template.Child()
    list_bin_el = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        Gio.Settings(schema_id="com.jeffser.Nocturne").bind(
            'auto-play',
            self.autoplay_row_el,
            'active',
            Gio.SettingsBindFlags.DEFAULT
        )

    def setup(self):
        integration = get_current_integration()
        self.song_list_el.list_el.bind_model(
            integration.loaded_models.get('currentSong').get_property('queueModel'),
            lambda song_id: SongRow(
                song_id.get_string(),
                draggable=True,
                removable=True
            )
        )
        integration.connect_to_model('currentSong', 'generatingQueue', self.autoplay_spinner_el.set_visible)

