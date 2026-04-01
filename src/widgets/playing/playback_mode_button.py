# playback_mode_button.py

from gi.repository import Gtk, Gio
from ...constants import PLAYBACK_MODES

@Gtk.Template(resource_path='/com/jeffser/Nocturne/playing/playback_mode_button.ui')
class PlaybackModeButton(Gtk.MenuButton):
    __gtype_name__ = 'NocturnePlaybackModeButton'

    container = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self.settings = Gio.Settings(schema_id="com.jeffser.Nocturne")
        self.settings.connect('changed::playback-mode', lambda settings, key: self.mode_changed(settings.get_value(key).unpack()))
        self.mode_changed(self.settings.get_value('playback-mode').unpack())

        for name, metadata in PLAYBACK_MODES.items():
            button = Gtk.Button(
                css_classes=['flat'],
                icon_name=metadata.get('icon-name'),
                tooltip_text=metadata.get('display-name'),
                name=name
            )
            button.connect('clicked', lambda btn: self.mode_changed(btn.get_name()))
            self.container.append(button)

    def mode_changed(self, name:str):
        self.set_icon_name(PLAYBACK_MODES.get(name, {}).get('icon-name'))
        self.set_tooltip_text(PLAYBACK_MODES.get(name, {}).get('display-name'))
        self.get_popover().popdown()
        if self.settings.get_value('playback-mode').unpack() != name:
            self.settings.set_string('playback-mode', name)
