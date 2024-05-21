from gi.repository import Gtk

class StyleEditor:
    def __init__(self):
        self.window_builder = Gtk.Builder()
        self.window_builder.add_from_file("gaphor/diagram/styleeditor.ui")
        self.window = None

    def present(self):
        if self.window:
            self.window.present()
            return

        self.window = self.window_builder.get_object("style-editor")
        self.window.connect("close-request", self.close)
        self.window.present()

    def close(self, widget=None):
        if self.window:
            self.window.destroy()
            self.window = None
