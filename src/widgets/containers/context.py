# context.py

from gi.repository import Gtk, Adw, GLib

class ContextContainer(Gtk.Box):
    __gtype_name__ = 'NocturneContextContainer'

    def __init__(self, options:dict, model_id:str):
        #options:
        #name : {
        #   icon-name:str
        #   css:list
        #   connection:callable
        #   action-name:str
        #   sensitive:bool
        #}

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL
        )
        for name, data in options.items():
            btn = Gtk.Button(
                css_classes=['small', 'flat', 'button_no_bold'] + data.get('css', []),
                child=Adw.ButtonContent(
                    label=name,
                    icon_name=data.get('icon-name'),
                    halign=Gtk.Align.START
                )
            )
            if data.get('sensitive', True):
                btn.connect('clicked', self.callback_handler, data.get('connection'))
            if data.get('action-name') and data.get('sensitive', True):
                btn.set_action_name(data.get('action-name'))
                if model_id:
                    btn.set_action_target_value(GLib.Variant.new_string(model_id))
            btn.set_sensitive(data.get('sensitive', True))
            self.append(btn)

    def callback_handler(self, button, callback):
        popover = button.get_ancestor(Gtk.Popover)
        if popover:
            popover.popdown()
        if callback:
            callback()
        
