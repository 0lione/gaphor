# vim: sw=4
"""
Main window actions.
"""

from gaphor.misc.action import Action, CheckAction, RadioAction, register_action
import sys
import gobject
import gtk
import gaphor.UML as UML
import gaphor.diagram as diagram
import gc
import traceback
from threading import Thread

import gaphor

DEFAULT_EXT='.gaphor'

def main_loop():
    main = gobject.main_context_default()
    while main.pending(): main.iteration(False)

class WorkerThread(Thread):
    """Run a function within a thread. The worker thread has a blocking
    start() function, which calls the GObject main loop every now and then.
    """

    def __init__(self, function):
        Thread.__init__(self)
        self.function = function
        self.error = None

    def start(self):
        Thread.start(self)
        while self.isAlive():
            main_loop()
            self.join(0.5)
            #print '.',

    def run(self):
        try:
            self.function()
        except Exception, e:
            log.error('Error occured while in worker thread', e)
            self.error = e

class NewAction(Action):
    id = 'FileNew'
    label = '_New'
    tooltip = 'Create a new Gaphor project'
    stock_id = 'gtk-new'

    def init(self, window):
        self._window = window

    def execute(self):
        factory = gaphor.resource(UML.ElementFactory)
        factory.flush()
        gc.collect()
        model = factory.create(UML.Package)
        model.name = 'New model'
        diagram = factory.create(UML.Diagram)
        diagram.package = model
        diagram.name='main'
        #stereotypes = factory.create(UML.Profile)
        #stereotypes.name = 'Stereotypes'
        self._window.set_filename(None)
        self._window.set_message('Created a new model')
        factory.notify_model()

        path = self._window.get_model().path_from_element(diagram)
        # Expand the first row:
        self._window.get_tree_view().expand_row(path[:-1], False)
        # Select the diagram, so it can be opened by the OpenModelElement action
        selection = self._window.get_tree_view().get_selection()
        selection.select_path(path)
        self._window.execute_action('OpenModelElement')

register_action(NewAction)


class OpenAction(Action):

    id = 'FileOpen'
    label = '_Open...'
    stock_id='gtk-open'
    tooltip = 'Load a Gaphor project from a file'

    def init(self, window):
        self.filename = None
        self._window = window

    def show_status_window(self, title, message):
        win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        win.set_title(title)
        win.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        win.set_parent(self._window.get_window())
        label = gtk.Label(message)
        label.set_padding(30,30)
        win.add(label)
        win.show_all()
        return win

    def execute(self):
        filesel = gtk.FileSelection('Open Gaphor file')
        filesel.hide_fileop_buttons()
        filesel.set_filename(self.filename or '')

        response = filesel.run()
        filename = filesel.get_filename()
        filesel.destroy()
        if filename and response == gtk.RESPONSE_OK:
            action_states = self._window.action_pool.get_action_states()
            try:
                import gaphor.storage as storage
                log.debug('Loading from: %s' % filename)
                win = self.show_status_window('Loading...', 'Loading model from %s' % filename)
                self.filename = filename
                gc.collect()
                worker = WorkerThread(lambda: storage.load(filename))
                self._window.action_pool.insensivate_actions()
                worker.start()
                if worker.error:
                    log.error('Error while loading model from file %s: %s' % (filename, worker.error))

                self._window.set_filename(filename)
                self._window.set_message('Model loaded successfully')
                model = self._window.get_model()
                view = self._window.get_tree_view()

                # Expand all root elements:
                for node in model.root[1]:
                    view.expand_row(model.path_from_element(node[0]), False)

                # Restore states of actions
                win.destroy()
            finally:
                self._window.action_pool.set_action_states(action_states)
                self._window.action_pool.update_actions()

register_action(OpenAction)


class SaveAsAction(Action):
    id = 'FileSaveAs'
    stock_id = 'gtk-save-as'

    def init(self, window):
        self._window = window
        self.factory = gaphor.resource('ElementFactory')
        self.factory.connect(self.on_element_factory)
        self.on_element_factory(self)
        # Disconnect when the window is closed:
        window.connect(self.on_window_closed)

    def on_element_factory(self, *args):
        #factory = gaphor.resource('ElementFactory')
        if self.factory.values():
            self.sensitive = True
        else:
            self.sensitive = False

    def on_window_closed(self, window):
        if self._window.get_state() == self._window.STATE_CLOSED:
            self.factory.disconnect(self.on_element_factory)

    def show_status_window(self, title, message):
        win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        win.set_title(title)
        win.set_parent(self._window.get_window())
        win.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        label = gtk.Label(message)
        label.set_padding(30,30)
        win.add(label)
        win.show_all()
        return win

    def save(self, filename):
        if filename and len(filename) > 0:
            import gaphor.storage as storage
            if not filename.endswith(DEFAULT_EXT):
                filename = filename + DEFAULT_EXT

            log.debug('Saving to: %s' % filename)
            win = self.show_status_window('Saving...', 'Saving model to %s' % filename)
            worker = WorkerThread(lambda: storage.save(filename))
            action_states = self._window.action_pool.get_action_states()
            self._window.action_pool.insensivate_actions()
            worker.start()
            if worker.error:
                log.error('Error while saving model to file %s: %s' % (filename, worker.error))

            self._window.set_filename(filename)

            # Restore states of actions
            self._window.action_pool.set_action_states(action_states)
            win.destroy()

    def execute(self):
        filename = self._window.get_filename()
        filesel = gtk.FileSelection('Save file as')
        filesel.set_filename(filename or '')
        response = filesel.run()
        filename = None
        if response == gtk.RESPONSE_OK:
            filename = filesel.get_filename()
        filesel.destroy()
        self.save(filename)

register_action(SaveAsAction)


class SaveAction(SaveAsAction):
    id = 'FileSave'
    stock_id = 'gtk-save'

    def execute(self):
        filename = self._window.get_filename()
        if filename:
            self.save(filename)
        else:
            SaveAsAction.execute(self)

register_action(SaveAction)


class QuitAction(Action):
    id = 'FileQuit'
    stock_id = 'gtk-quit'
    tooltip='Quit Gaphor'

    def init(self, window):
        self._window = window

    def execute(self):
        log.debug('Quiting gaphor...')
        self._window.close()
        del self._window
        gc.collect()

register_action(QuitAction)


class OpenEditorWindowAction(Action):
    id = 'OpenEditorWindow'
    label = '_Editor'
    tooltip = 'Open the Gaphor Editor'

    def init(self, window):
        self._window = window

    def execute(self):
        from gaphor.ui import EditorWindow
        
        ew = EditorWindow()
        ew.construct()
        self._window.add_transient_window(ew)
        self._window.set_message('Editor launched')

register_action(OpenEditorWindowAction)


class OpenConsoleWindowAction(Action):
    id = 'OpenConsoleWindow'
    label = '_Console'
    tooltip = 'Open the Gaphor Console'

    def init(self, window):
        self._window = window

    def execute(self):
        from gaphor.ui.consolewindow import ConsoleWindow
        
        ew = ConsoleWindow()
        ew.construct()
        self._window.add_transient_window(ew)
        self._window.set_message('Console launched')

register_action(OpenConsoleWindowAction)


class OpenStereotypeWindowAction(Action):
    id = 'OpenStereotypeWindow'
    label = 'S_tereotypes'
    tooltip = 'Open the Gaphor Stereotypes'

    def init(self, window):
        self._window = window

    def execute(self):
        from gaphor.ui.stereotypewindow import StereotypeWindow
        
        ew = StereotypeWindow()
        #ew.construct(self._window.get_window())
        ew.run(self._window.get_window())
        #self._window.add_transient_window(ew)
        #self._window.set_message('Stereortypes launched')

register_action(OpenStereotypeWindowAction)


class AboutAction(Action):
    id = 'About'
    label = '_About'
    stock_id = 'gtk-about'
    tooltip='About Gaphor'
    
    def init(self, window):
        self._window = window

    def execute(self):
        logo = gtk.gdk.pixbuf_new_from_file (gaphor.resource('DataDir') + '/pixmaps/logo.png')
	version = gaphor.resource('Version')
        about = gtk.Dialog("About Gaphor", self._window.get_window(), 0, (gtk.STOCK_OK, gtk.RESPONSE_OK))
	vbox = about.vbox

	image = gtk.Image()
	image.set_from_pixbuf(logo)
	vbox.pack_start(image)

	def add_label(text, padding_x=0, padding_y=0):
	    label = gtk.Label(text)
	    label.set_property('use-markup', True)
	    label.set_padding(padding_x, padding_y)
	    label.set_justify(gtk.JUSTIFY_CENTER)
	    vbox.pack_start(label)

	#add_label('<span size="xx-large" weight="bold">Gaphor</span>')
	add_label('<span weight="bold">version %s</span>' % version)
	add_label('<span variant="smallcaps">UML Modeling tool for GNOME</span>', 8, 8)
	add_label('<span size="small">Copyright (c) 2001-2004 Arjan J. Molenaar</span>', 8, 8)
	vbox.pack_start(gtk.HSeparator())
	add_label('This software is published\n'
		  'under the terms of the\n'
		  '<span weight="bold">GNU General Public License v2</span>.\n'
		  'See the COPYING file for details.', 0, 8)
	vbox.show_all()
        about.run()
	about.destroy()

register_action(AboutAction)


class CreateDiagramAction(Action):
    id = 'CreateDiagram'
    label = '_New diagram'
    stock_id = 'gaphor-diagram'

    def init(self, window):
        self._window = window

    def update(self):
        element = self._window.get_tree_view().get_selected_element()
        self.sensitive = isinstance(element, UML.Package)

    def execute(self):
        element = self._window.get_tree_view().get_selected_element()
        diagram = gaphor.resource('ElementFactory').create(UML.Diagram)
        diagram.package = element

        path = self._window.get_model().path_from_element(diagram)
        # Expand the row:
        self._window.get_tree_view().expand_row(path[:-1], False)
        # Select the diagram, so it can be opened by the OpenModelElement action
        selection = self._window.get_tree_view().get_selection()
        selection.select_path(path)
        self._window.execute_action('OpenModelElement')

register_action(CreateDiagramAction, 'SelectRow')


class OpenElementAction(Action):
    id = 'OpenModelElement'
    label = '_Open'

    def init(self, window):
        self._window = window

    def update(self):
        element = self._window.get_tree_view().get_selected_element()
        self.sensitive = isinstance(element, UML.Diagram)

    def execute(self):
        element = self._window.get_tree_view().get_selected_element()
        if isinstance(element, UML.Diagram):
            # Try to find an existing window/tab and let it get focus:
            for tab in self._window.get_tabs():
                if tab.get_diagram() is element:
                    self._window.set_current_page(tab)
                    return
            # Import here to avoid cyclic references
            from gaphor.ui.diagramtab import DiagramTab
            diagram_tab = DiagramTab(self._window)
            #diagram_tab.set_owning_window(self._window)
            #diagram_tab.sub_window = False
            diagram_tab.set_diagram(element)
            diagram_tab.construct()
            #self._window.add_transient_window(diagram_window)
            #self._window.new_notebook_tab(diagram_window, element.name)
        else:
            log.debug('No action defined for element %s' % type(element).__name__)

register_action(OpenElementAction, 'SelectRow')


class RenameElementAction(Action):
    id = 'RenameModelElement'
    label = '_Rename'

    def init(self, window):
        self._window = window

    def execute(self):
        view = self._window.get_tree_view()
        selection = view.get_selection()
        model, iter = selection.get_selected()
        if not iter:
            return
        element = model.get_value(iter, 0)
        path = model.path_from_element(element)
        column = view.get_column(0)
        cell = column.get_cell_renderers()[1]
        cell.set_property('editable', 1)
        cell.set_property('text', element.name)
        view.set_cursor(path, column, True)
        cell.set_property('editable', 0)

register_action(RenameElementAction)


class DeleteCommand(Action):
    """Delete a model element through the tree view. This is only applicable
    to Diagram's and is not undoable."""
    id = 'DeleteElement'
    label = '_Delete'

    def set_parameters(self, params):
        self._window = params['window']
        #self._element = params['element']

    def execute(self):
        pass
        #if isinstance(self._element, UML.Diagram):
        #    self._element.unlink()

class SelectRowAction(Action):
    id = 'SelectRow'

    def init(self, window):
        pass

    def execute(self):
        pass

register_action(SelectRowAction)


class TabChangeAction(Action):
    id = 'TabChange'

    def init(self, window):
        pass

register_action(TabChangeAction)
