# vim: sw=4
"""
File menu related commands.
NewCommand
OpenCommand
SaveCommand
SaveAsCommand
QuitCommand
"""

from gaphor.misc.command import Command
from gaphor.misc.storage import Storage
import gtk
import gaphor.UML as UML
import gaphor.diagram as diagram
import gc

DEFAULT_EXT='.gaphor'

class NewCommand(Command):

    def execute(self):
	fact = UML.ElementFactory()
	fact.flush()
	gc.collect()
	model = fact.create(UML.Model)
	diagram = fact.create(UML.Diagram)
	diagram.namespace = model
	diagram.name='main'

class OpenCommand(Command):

    def __init__(self):
	Command.__init__(self)
	self.filename = None

    def execute(self):
	filesel = gtk.FileSelection('Open Gaphor file')
	filesel.hide_fileop_buttons()
	
	if self.filename:
	    filesel.set_filename(self.filename)

	filesel.ok_button.connect('clicked', self.on_ok_button_pressed, filesel)
	filesel.cancel_button.connect('clicked',
				      self.on_cancel_button_pressed, filesel)
	
	filesel.show()
	gtk.main()

    def on_ok_button_pressed(self, button, filesel):
	filename = filesel.get_filename()
	filesel.destroy()
	if filename and len(filename) > 0:
	    self.filename = filename
	    print 'Loading from:', filename
	    print 'Flushing old data...'
	    UML.ElementFactory().flush()
	    diagram.DiagramItemFactory().flush()

	    gc.collect()

	    store = Storage()
	    try:
		store.load(filename)
	    except Exception, e:
		import traceback
		print 'Error while loading model from file %s: %s' % (filename, e)
		traceback.print_exc()
	gtk.main_quit()

    def on_cancel_button_pressed(self, button, filesel):
	filesel.destroy()
        gtk.main_quit()


class SaveCommand(Command):

    def __init__(self):
	Command.__init__(self)
	self.filename = None

    def execute(self):
	filesel = gtk.FileSelection('Save file')
	if self.filename:
	    filesel.set_filename(self.filename)

	filesel.ok_button.connect('clicked', self.on_ok_button_pressed, filesel)
	filesel.cancel_button.connect('clicked',
				      self.on_cancel_button_pressed, filesel)
	
	filesel.show()
	gtk.main()

    def on_ok_button_pressed(self, button, filesel):
	filename = filesel.get_filename()
	filesel.destroy()
	if filename and len(filename) > 0:
	    if not filename.endswith(DEFAULT_EXT):
		filename = filename + DEFAULT_EXT
	    self.filename = filename
	    print 'Saving to:', filename
	    store = Storage()
	    try:
		store.save(filename)
	    except Exception, e:
		print 'Error while saving model to file %s: %s' % (filename, e)
	gtk.main_quit()

    def on_cancel_button_pressed(self, button, filesel):
	filesel.destroy()
        gtk.main_quit()


class SaveAsCommand(Command):

    def execute(self):
	SaveCommand().execute()


class QuitCommand(Command):

    def execute(self):
	gtk.main_quit()


class CloseCommand(Command):

    def __init__(self, window):
	self._window = window

    def execute(self):
	self._window.destroy()

