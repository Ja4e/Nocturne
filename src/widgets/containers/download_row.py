# download_row.py

from gi.repository import Gtk, Adw, Gio
from ...integrations import get_current_integration

@Gtk.Template(resource_path='/com/jeffser/Nocturne/containers/download_row.ui')
class DownloadRow(Gtk.ListBoxRow):
    __gtype_name__ = 'NocturneDownloadRow'

    title_label = Gtk.Template.Child()
    progressbar = Gtk.Template.Child()

    def __init__(self, id:str):
        self.id = id
        integration = get_current_integration()
        integration.verifySong(self.id)
        super().__init__()
        integration.connect_to_model(self.id, 'title', self.update_title)

    def update_title(self, title:str):
        self.title_label.set_label(title)
        self.set_tooltip_text(title)
