
# vim:sw=4:et

import gtk
import namespace
import gaphor
import gaphor.UML as UML
from abstractwindow import AbstractWindow

class MainWindow(AbstractWindow):
    """The main window for the application.
    It contains a Namespace-based tree view and a menu and a statusbar.
    """

    menu = ('_File', (
                'FileNew',
                'FileOpen',
                'separator',
                'FileSave',
                'FileSaveAs',
                'separator',
                '_Export', (
                    'FileExportSVG',),
                'separator',
                'FileCloseTab',
                'separator',
                'FileQuit'),
            '_Edit', (
                'EditUndo',
                'EditRedo',
                'separator',
                'EditDelete',
                'separator',
                'EditSelectAll',
                'EditDeselectAll'),
            '_Diagram', (
                'ViewZoomIn',
                'ViewZoomOut',
                'ViewZoom100',
                'separator',
                'SnapToGrid',
                'ShowGrid',
                'separator',
                'CreateDiagram'),
            '_Window', (
                'OpenEditorWindow',
                'OpenConsoleWindow'),
            #'_Help', (
            #    'About',)
            )

    toolbar =  ('FileOpen',
                'separator',
                'FileSave',
                'FileSaveAs',
                'separator',
                'EditUndo',
                'EditRedo',
                'separator',
                'ViewZoomIn',
                'ViewZoomOut',
                'ViewZoom100')

    wrapbox =  ('Pointer',
                'separator',
                'InsertClass',
                'InsertPackage',
                'separator',
                'InsertAssociation',
                'InsertDependency',
                'InsertGeneralization',
                'separator',
                'InsertComment',
                'InsertCommentLine',
                'InsertAction',
                'InsertInitialNode',
                'InsertActivityFinalNode',
                'InsertDecisionNode',
                'InsertFlow')

    ns_popup = ('RenameModelElement',
                'OpenModelElement',
                'separator',
                'CreateDiagram')

    def __init__(self):
        AbstractWindow.__init__(self)
        self.__filename = None
        self.__transient_windows = []
        self.notebook_map = {}

    def get_model(self):
        self._check_state(AbstractWindow.STATE_ACTIVE)
        return self.model

    def get_tree_view(self):
        return self.view

    def set_filename(self, filename):
        self.__filename = filename

    def get_filename(self):
        return self.__filename

    def get_transient_windows(self):
        return self.__transient_windows

    def get_current_diagram_tab(self):
        return self.get_current_tab()

    def get_current_diagram(self):
        tab = self.get_current_diagram_tab()
        return tab and tab.get_diagram()

    def get_current_diagram_view(self):
        tab = self.get_current_diagram_tab()
        return tab and tab.get_view()

    def construct(self):
        model = namespace.NamespaceModel(gaphor.resource(UML.ElementFactory))
        view = namespace.NamespaceView(model)
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        #scrolled_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scrolled_window.add(view)
        
        view.connect_after('event-after', self.on_view_event)
        view.connect('row-activated', self.on_view_row_activated)
        view.connect_after('cursor-changed', self.on_view_cursor_changed)
        view.set_size_request(200, 200)

        #scrolled_window.show_all()
        #ns_paned = gtk.VPaned()
        #ns_paned.pack1(scrolled_window)#, expand=True)
        vbox = gtk.VBox()
        vbox.pack_start(scrolled_window, expand=True)

        paned = gtk.HPaned()
        #paned.pack1(scrolled_window)
        #paned.pack1(ns_paned)
        paned.pack1(vbox)
        notebook = gtk.Notebook()
        #notebook.popup_enable()
        notebook.set_scrollable(True)
        notebook.set_show_border(False)
 
        notebook.connect_after('switch-page', self.on_notebook_switch_page)

        paned.pack2(notebook)
        paned.show_all()

        self.notebook = notebook
        self.model = model
        self.view = view

        self._construct_window(name='main',
                               title='Gaphor v' + gaphor.resource('Version'),
                               size=(760, 580),
                               contents=paned)
                               #contents=scrolled_window)
        wrapbox = self.menu_factory.create_wrapbox(self.wrapbox)
        #wrapbox.set_aspect_ratio(1/256)
        vbox.pack_start(wrapbox, expand=False)
        wrapbox.show()
        #vbox.set_resize_mode(gtk.RESIZE_QUEUE)
        #wrapbox.set_resize_mode(gtk.RESIZE_QUEUE)
        #scrolled_window = gtk.ScrolledWindow()
        #scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        #scrolled_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        #scrolled_window.add_with_viewport(wrapbox)
        #scrolled_window.show()
        #ns_paned.pack2(scrolled_window)#, expand=False)
        #wrapbox.queue_resize()
        #wrapbox.set_size_request(0,0)

        #def print_me(wrapbox, rect, mutex):
        #    print wrapbox, rect, mutex
        #    if not mutex:
        #        mutex.append(1)
        #        wrapbox.queue_resize()
        #        mutex.remove(1)

        #paned.connect('motion-notify-event', print_me)
        #wrapbox.connect('size-allocate', print_me, [])

    def add_transient_window(self, window):
        """Add a window as a sub-window of the main application.
        """
        # Assign the window the accelerators od the main window too
        window.get_window().add_accel_group(self.accel_group)
        #self.__transient_windows.append(window)
        #window.connect(self.on_transient_window_closed)

    # Notebook methods:

    def new_tab(self, window, contents, label):
        #contents = tab.get_contents()
        l = gtk.Label(label)
        #img = gtk.Image()
        #img.set_from_stock('gtk-close', gtk.ICON_SIZE_MENU)
        #b = gtk.Button()
        #b.set_border_width(0)
        #b.add(img)
        #h = gtk.HBox()
        #h.set_spacing(4)
        #h.pack_start(l, expand=False)
        #h.pack_start(b, expand=False)
        #h.show_all()
        self.notebook.append_page(contents, l)
        page_num = self.notebook.page_num(contents)
        self.notebook.set_current_page(page_num)
        self.notebook_map[contents] = window
        self.execute_action('TabChange')
        return page_num

    def get_current_tab(self):
        current = self.notebook.get_current_page()
        content = self.notebook.get_nth_page(current)
        return self.notebook_map.get(content)

    def set_current_page(self, tab):
        for p, t in self.notebook_map.iteritems():
            if tab is t:
                num = self.notebook.page_num(p)
                self.notebook.set_current_page(num)
                return

    def set_tab_label(self, tab, label):
        for p, t in self.notebook_map.iteritems():
            if tab is t:
                l = gtk.Label(label)
                l.show()
                self.notebook.set_tab_label(p, l)

    def get_tabs(self):
        return self.notebook_map.values()

    def remove_tab(self, window):
        for c, w in self.notebook_map.iteritems():
            if window is w:
                num = self.notebook.page_num(c)
                self.notebook.remove_page(num)
                del self.notebook_map[c]
                self.execute_action('TabChange')
                return

    # Signal callbacks:

    def _on_window_destroy(self, window):
        """Window is destroyed... Quit the application.
        """
        AbstractWindow._on_window_destroy(self, window)
        #gaphor.resource(UML.ElementFactory).disconnect(self.__on_element_factory_signal)
        del self.model
        del self.view

    def on_view_event(self, view, event):
        self._check_state(AbstractWindow.STATE_ACTIVE)
        # handle mouse button 3:
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            #selection = view.get_selection()
            #model, iter = selection.get_selected()
            #assert model is self.model
            #if not iter:
                #return
            #element = model.get_value(iter, 0)
            #path = model.path_from_element(element)
            self._construct_popup_menu(menu_def=self.ns_popup, event=event)

    def on_view_row_activated(self, view, path, column):
        self._check_state(AbstractWindow.STATE_ACTIVE)
        node = self.get_model().node_from_path(path)
        element = self.get_model().element_from_node(node)
        self.execute_action('OpenModelElement')

    def on_view_cursor_changed(self, view):
        self.execute_action('SelectRow')

    def on_notebook_switch_page(self, notebook, tab, page_num):
        #print notebook, tab, page_num
        self.execute_action('TabChange')

#    def on_transient_window_closed(self, window):
#        assert window in self.__transient_windows
#        log.debug('%s closed.' % window)
#        self.__transient_windows.remove(window)

    def __on_transient_window_notify_title(self, window):
        pass

    #def __on_element_factory_signal(self, obj, key):
        #print '__on_element_factory_signal', key
        #factory = gaphor.resource(UML.ElementFactory)
        #self.set_capability('model', not factory.is_empty())

gtk.accel_map_add_filter('gaphor')

import mainactions
