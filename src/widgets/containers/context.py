# context.py

from gi.repository import Gtk, Adw, GLib

def get_context_buttons_list(options:dict, model_id:str, cb_handler:callable=None) -> list:
    if cb_handler is None:
        cb_handler = lambda btn, callback: callback() if callback else None
    buttons = []
    for name, data in options.items():
        btn = Gtk.Button(
            css_classes=data.get('css', []),
            child=Adw.ButtonContent(
                label=name,
                icon_name=data.get('icon-name'),
                halign=Gtk.Align.START
            )
        )
        if data.get('sensitive', True):
            btn.connect('clicked', cb_handler, data.get('connection'))
        if data.get('action-name') and data.get('sensitive', True):
            btn.set_action_name(data.get('action-name'))
            if model_id:
                btn.set_action_target_value(GLib.Variant.new_string(model_id))
        btn.set_sensitive(data.get('sensitive', True))
        buttons.append(btn)
    return buttons

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
        buttons = get_context_buttons_list(options, model_id, cb_handler=self.callback_handler)
        for btn in buttons:
            btn.add_css_class('flat')
            self.append(btn)

    def callback_handler(self, button, callback):
        popover = button.get_ancestor(Gtk.Popover)
        if popover:
            popover.popdown()
        if callback:
            callback()
        
