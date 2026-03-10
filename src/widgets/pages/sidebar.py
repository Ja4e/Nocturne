# sidebar.py

from gi.repository import Gtk, Adw, GLib

@Gtk.Template(resource_path='/com/jeffser/Nocturne/pages/sidebar.ui')
class MainSidebar(Adw.NavigationPage):
    __gtype_name__ = 'NocturneMainSidebar'

    sidebar = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        GLib.idle_add(self.connect_adaptive)

    def connect_adaptive(self):
        self.get_root().breakpoint_el.connect('apply', lambda *_: self.sidebar.set_mode(Adw.SidebarMode.PAGE))
        self.get_root().breakpoint_el.connect('unapply', lambda *_: self.sidebar.set_mode(Adw.SidebarMode.SIDEBAR))
        condition = self.get_root().breakpoint_el.get_condition().to_string()
        is_small = self.get_root().get_width() < int(condition.split(': ')[1].strip('sp'))
        self.sidebar.set_mode(Adw.SidebarMode.PAGE if is_small else Adw.SidebarMode.SIDEBAR)

        self.get_root().main_bottom_sheet.connect('notify::reveal-bottom-bar', self.bottom_bar_toggled)

    def bottom_bar_toggled(self, bottom_bar, gparam):
        self.set_margin_bottom(70 if bottom_bar.get_reveal_bottom_bar() else 0)
