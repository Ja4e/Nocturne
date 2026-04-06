# spectrum.py

from gi.repository import Gtk, Gdk, GObject, GLib
from ...integrations import get_current_integration
from colorthief import ColorThief
import io

class Spectrum(Gtk.DrawingArea):
    __gtype_name__ = 'NocturneSpectrum'

    def __init__(self):
        integration = get_current_integration()
        super().__init__()
        self.set_content_width(480)
        self.set_content_height(360)
        self.target_magnitudes = [0] * 32
        self.current_magnitudes = [0] * 32
        self.color = [0.2, 0.6, 0.9]
        self.fall_speed = 0.01

        self.set_draw_func(self.on_draw)

        integration.connect_to_model('currentSong', 'buttonState', self.playback_changed)
        integration.connect_to_model('currentSong', 'magnitudes', self.on_update_magnitudes)
        integration.connect_to_model('currentSong', 'songId', self.song_changed)

        GLib.timeout_add(16, self.on_tick)

    def on_update_magnitudes(self, new_magnitudes):
        self.target_magnitudes = [max(0.0, (m + 80) / 80) for m in new_magnitudes]

    def on_tick(self):
        for i in range(len(self.target_magnitudes)):
            if self.target_magnitudes[i] >= self.current_magnitudes[i]:
                self.current_magnitudes[i] = min(self.target_magnitudes[i], self.fall_speed + self.current_magnitudes[i])
            else:
                self.current_magnitudes[i] = max(0, self.current_magnitudes[i] - self.fall_speed)
        self.queue_draw()
        return True

    def on_draw(self, drawing_area, cr, width, height):
        if not self.current_magnitudes:
            return

        n = len(self.current_magnitudes)
        dx = width / (n - 1)

        cr.move_to(0, height)

        cr.line_to(0, height * (1 - self.current_magnitudes[0]))

        for i in range(n - 1):
            x1 = i * dx
            y1 = height * (1 - self.current_magnitudes[i])
            x2 = (i + 1) * dx
            y2 = height * (1 - self.current_magnitudes[i + 1])

            # Control points for smoothness
            xc = (x1 + x2) / 2
            cr.curve_to(xc, y1, xc, (y1 + y2) / 2, x2, (y1 +y2) / 2)

        cr.line_to(width, height)
        cr.close_path()

        cr.set_source_rgba(*self.color, 0.75)
        cr.fill_preserve()

    def song_changed(self, songId:str):
        integration = get_current_integration()
        if model := integration.loaded_models.get(songId):
            if gbytes := model.get_property('gdkPaintableBytes'):
                raw_bytes = bytes(gbytes.get_data())
                img_io = io.BytesIO(raw_bytes)
                self.color = [min(c/255, 1) for c in ColorThief(img_io).get_color(quality=10)]
        else:
            self.target_magnitudes = [0] * 32

    def playback_changed(self, playbackState:str):
        if playbackState == "play":
            self.target_magnitudes = [0] * 32
