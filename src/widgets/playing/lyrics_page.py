# lyrics_page.py

from gi.repository import Gtk, Adw, GObject, GLib, Gio, Pango, Gst
from ..song import SongRow
from ...integrations import models, get_current_integration
from ..lyrics.helpers import get_lyrics
from ...constants import DATA_DIR
import threading, os

class LyricRow(Gtk.ListBoxRow):
    __gtype_name__ = 'NocturneLyricRow'

    ms = GObject.Property(type=int)

    def __init__(self, content, ms):
        super().__init__(
            ms=ms,
            child=Gtk.Label(
                wrap=True,
                wrap_mode=Pango.WrapMode.WORD_CHAR,
                justify=Gtk.Justification.CENTER,
                halign=Gtk.Align.CENTER,
                valign=Gtk.Align.CENTER,
                label=content or "🎶"
            )
        )

@Gtk.Template(resource_path='/com/jeffser/Nocturne/playing/lyrics_page.ui')
class PlayingLyricsPage(Gtk.Stack):
    __gtype_name__ = 'NocturnePlayingLyricsPage'

    plain_label_el = Gtk.Template.Child()
    lrc_list_el = Gtk.Template.Child()
    scrolledwindow = Gtk.Template.Child()
    code_is_selecting = False # used so that `on_lrc_selection` is only executed when manually selecting

    def setup(self):
        # Called after login
        integration = get_current_integration()
        integration.connect_to_model('currentSong', 'songId', self.song_changed)
        integration.connect_to_model('currentSong', 'positionSeconds', self.position_changed)

    def song_changed(self, song_id:str, lrclib_download:bool=False):
        GLib.idle_add(self.set_visible_child_name, 'loading')
        def update_lyrics():
            lyrics = get_lyrics(song_id, lrclib_download)
            GLib.idle_add(self.set_visible_child_name, lyrics.get('type'))

            if lyrics.get('type') == 'plain':
                GLib.idle_add(self.plain_label_el.set_label, lyrics.get('content'))
            elif lyrics.get('type') == 'lrc':
                GLib.idle_add(self.lrc_list_el.remove_all)
                if lyrics.get('content')[0].get('content'):
                    lyrics['content'].insert(0, {'content': '', 'ms': 0})
                for line in lyrics.get('content'):
                    row = LyricRow(
                        ms=line.get('ms'),
                        content=line.get('content', '')
                    )
                    GLib.idle_add(self.lrc_list_el.append, row)

        threading.Thread(target=update_lyrics).start()

    def position_changed(self, position_seconds:float):
        if self.get_visible_child_name() == 'lrc':
            ms = int(position_seconds * 1000)+100
            best_match = None
            for row in list(self.lrc_list_el):
                if row.ms <= ms:
                    best_match = row
                else:
                    break
            if best_match and best_match != self.lrc_list_el.get_selected_row():
                self.code_is_selecting = True
                self.lrc_list_el.select_row(best_match)
                self.code_is_selecting = False

    @Gtk.Template.Callback()
    def on_lrc_selection(self, list_el, position):
        row = list_el.get_selected_row()
        if row:
            if not self.code_is_selecting:
                self.get_root().playing_page.player.gst.seek_simple(
                    Gst.Format.TIME,
                    Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                    int(row.ms/1000 * Gst.SECOND)
                )
            def do_scroll():
                vadj = self.scrolledwindow.get_vadjustment()
                row_alloc = row.get_allocation()
                viewport_height = self.scrolledwindow.get_height()
                row_y = row_alloc.y
                row_height = row_alloc.height
                target = row_y - (viewport_height / 2) + (row_height / 2)
                lower = vadj.get_lower()
                upper = vadj.get_upper() - vadj.get_page_size()
                target = max(lower, min(target, upper))
                vadj.set_value(target)

            GLib.idle_add(do_scroll)

    @Gtk.Template.Callback()
    def lyric_download_requested(self, button):
        integration = get_current_integration()
        self.song_changed(integration.loaded_models.get('currentSong').get_property('songId'), True)

    def copy_lyrics_lrc(self, dialog, task, model):
        if model:
            if source_file := dialog.open_finish(task):
                lyrics_dir = os.path.join(DATA_DIR, 'lyrics')
                os.makedirs(lyrics_dir, exist_ok=True)
                file_name_without_ext = '{}|{}|{}|{}'.format(
                    model.get_property('title'),
                    model.get_property('artist'),
                    model.get_property('album') or model.get_property('title'),
                    model.get_property('duration')
                )
                lrc_path = os.path.join(lyrics_dir, file_name_without_ext+'.lrc')
                destination_file = Gio.File.new_for_path(lrc_path)

                source_file.copy_async(
                    destination_file,
                    Gio.FileCopyFlags.OVERWRITE,
                    GLib.PRIORITY_DEFAULT,
                    None,
                    None,
                    lambda *_: self.song_changed(model.get_property('id'), False)
                )


    @Gtk.Template.Callback()
    def lyric_load_requested(self, button):
        integration = get_current_integration()
        if model := integration.loaded_models.get(integration.loaded_models.get('currentSong').get_property('songId')):
            file_filter = Gtk.FileFilter(
                name=_("LRC File")
            )
            file_filter.add_mime_type('text/x-lrc')
            file_filter.add_mime_type('application/x-lrc')
            file_filter.add_suffix('lrc')
            file_filter_list = Gio.ListStore.new(Gtk.FileFilter)
            file_filter_list.append(file_filter)

            Gtk.FileDialog(
                filters=file_filter_list
            ).open(self.get_root(), None, self.copy_lyrics_lrc, model)

    @Gtk.Template.Callback()
    def go_to_main(self, button):
        self.set_visible_child_name('not-found-locally')
