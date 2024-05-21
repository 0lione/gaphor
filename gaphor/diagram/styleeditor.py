from gi.repository import Gtk

from gaphor.core import Transaction
from gaphor.core import transactional
from gaphor.core.modeling import Element
from gaphor.core.modeling import Presentation, self_and_owners

class StyleEditor:
    def __init__(self, subject, close_callback):
        self.subject = subject
        self.window_builder = Gtk.Builder()
        self.window_builder.add_from_file("gaphor/diagram/styleeditor.ui")
        self.window = None
        self.close_callback = close_callback
        self.color_button = None

    def present(self):
        if self.window is None:
            self.window = self.window_builder.get_object("style-editor")
            self.window.connect("close-request", self.close)
            self.color_button = self.window_builder.get_object("color-button")
            self.color_button.connect("color-set", self.on_color_set)
        self.window.present()

    def close(self, widget=None):
        if self.window:
            self.window.destroy()
            self.window = None
        self.close_callback()

    @transactional
    def on_color_set(self, widget):
        colors = widget.get_rgba()
        r = int(colors.red * 255)
        g = int(colors.green * 255)
        b = int(colors.blue * 255)
        a = colors.alpha
        self.subject.presentation_style.change_style("color", f"rgba({r}, {g}, {b}, {a})")
