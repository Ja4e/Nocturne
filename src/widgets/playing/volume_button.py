# volume_button.py

from gi.repository import Gtk, Gio

@Gtk.Template(resource_path='/com/jeffser/Nocturne/playing/volume_button.ui')
class VolumeButton(Gtk.MenuButton):
    __gtype_name__ = 'NocturneVolumeButton'

    volume_el = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        Gio.Settings(schema_id="com.jeffser.Nocturne").bind(
            "volume",
            self.volume_el.get_adjustment(),
            "value",
            Gio.SettingsBindFlags.DEFAULT
        )

    @Gtk.Template.Callback()
    def on_volume_changed(self, scale_el):
        value = scale_el.get_value()
        if value == 0:
            self.set_icon_name("speaker-0-symbolic")
        elif value < 0.33:
            self.set_icon_name("speaker-1-symbolic")
        elif value < 0.66:
            self.set_icon_name("speaker-2-symbolic")
        else:
            self.set_icon_name("speaker-3-symbolic")
