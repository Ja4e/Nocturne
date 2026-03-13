# wrapbox.py

from gi.repository import Gtk, Adw, GLib

@Gtk.Template(resource_path='/com/jeffser/Nocturne/containers/wrapbox.ui')
class Wrapbox(Gtk.Box):
    __gtype_name__ = 'NocturneWrapbox'

    header_button = Gtk.Template.Child()
    list_el = Gtk.Template.Child()

    def set_header(self, label:str, icon_name:str, page_tag:str=None):
        self.header_button.set_tooltip_text(label)
        self.header_button.get_child().set_label(label)
        self.header_button.get_child().set_icon_name(icon_name)
        if page_tag:
            self.header_button.set_action_target_value(GLib.Variant.new_string(page_tag))
            self.header_button.set_action_name('app.replace_root_page')

    def remove_all(self):
        for child in list(self.list_el):
            self.list_el.remove(child)

    def set_widgets(self, widgets:list):
        if len(list(self.list_el)):
            GLib.idle_add(self.remove_all)
        GLib.idle_add(self.set_visible, len(widgets) > 0)
        for page in widgets:
            GLib.idle_add(self.list_el.append, page)
