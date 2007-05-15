"""
The main application window.
"""

import gtk

from zope import interface, component
from gaphor.interfaces import IActionProvider
from interfaces import IUIComponent

from gaphor import UML
from gaphor.core import _, inject, action, build_action_group
from gaphor.ui import namespace
from gaphor.ui.diagramtab import DiagramTab
from gaphor.ui.toolbox import Toolbox
from toplevelwindow import ToplevelWindow

from gaphor.ui.objectinspector import ObjectInspector

from interfaces import IDiagramElementReceivedFocus
from gaphor.interfaces import IServiceEvent


class MainWindow(ToplevelWindow):
    """
    The main window for the application.
    It contains a Namespace-based tree view and a menu and a statusbar.
    """
    interface.implements(IActionProvider)

    properties = inject('properties')
    element_factory = inject('element_factory')
    action_manager = inject('action_manager')

    # <old>
    toolbox = (
        ('', (
                'Pointer',
                'InsertComment',
                'InsertCommentLine')),
        (_('Classes'), (
                'InsertClass',
                'InsertInterface',
                'InsertPackage',
                'InsertAssociation',
                'InsertDependency',
                'InsertGeneralization',
                'InsertImplementation')),
        (_('Components'), (
                'InsertComponent',
                'InsertAssemblyConnector',
                'InsertNode',
                'InsertArtifact')),
#        (_('Composite Structures'), (
#                'InsertConnector',)),
        (_('Actions'), (
                'InsertAction',
                'InsertInitialNode',
                'InsertActivityFinalNode',
                'InsertFlowFinalNode',
                'InsertDecisionNode',
                'InsertForkNode',
                'InsertObjectNode',
                'InsertFlow')),
#        (_('Interactions'), (
#                'InsertInteraction',
#                'InsertLifeline',
#                'InsertMessage')),
        (_('Use Cases'), (
                'InsertUseCase',
                'InsertActor',
                'InsertUseCaseAssociation',
                'InsertInclude',
                'InsertExtend')),
        (_('Profiles'), (
                'InsertProfile',
                'InsertMetaClass',
                'InsertStereotype',
                'InsertExtension')),
    )

    menu = (_('_File'), (
                'FileNew',
                'FileOpen',
                'FileRevert',
                _('Recent files'),
                    ('<RecentFiles>',),
                'separator',
                'FileSave',
                'FileSaveAs',
                '<FileSaveSlot>',
                'separator',
                _('_Import'), (
                    '<FileImportSlot>',),
                _('_Export'), (
                    '<FileExportSlot>',),
                'separator',
                'FileCloseTab',
                '<FileSlot>',
                'separator',
                'FileQuit'),
            _('_Edit'), (
                'Undo',
                'Redo',
                'separator',
                'EditCopy',
                'EditPaste',
                'separator',
                'EditDelete',
                'separator',
                'EditSelectAll',
                'EditDeselectAll',
                'separator',
                'ResetToolAfterCreate',
                '<EditSlot>'),
            _('_Diagram'), (
                'ViewZoomIn',
                'ViewZoomOut',
                'ViewZoom100',
                'separator',
                #'SnapToGrid',
                #'ShowGrid',
                #'separator',
                'CreateDiagram',
                'DeleteDiagram',
                'separator',
                # Copy the tool box:
                _('Tools'),
                    #toolbox_to_menu(toolbox),
                'separator',
                '<DiagramSlot>'),
            _('_Window'), (
                'OpenEditorWindow',
                'OpenConsoleWindow',
                '<WindowSlot>'),
            _('_Help'), (
                'Manual',
                'About',
                '<HelpSlot>'),
            )

    # </old>

    title = 'Gaphor'
    size = property(lambda s: s.properties.get('ui.window-size', (760, 580)))
    menubar_path = '/mainwindow'
    toolbar_path = '/mainwindow-toolbar'

    menu_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu action="file">
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
            <separator />
            <menuitem action="file-quit" />
          </menu>
          <menu action="edit">
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
          </menu>
          <menu action="diagram">
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
          </menu>
          <menu action="tools">
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
          </menu>
          <menu action="window">
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
          </menu>
          <menu action="help">
            <placeholder name="primary" />
            <placeholder name="secondary" />
            <placeholder name="ternary" />
          </menu>
        </menubar>
        <toolbar name='mainwindow-toolbar'>
        </toolbar>
        <toolbar action="tools">
        </toolbar>
        <popup action="namespace-popup">
          <menuitem action="tree-view-open" />
          <menuitem action="tree-view-rename" />
          <separator />
          <menuitem action="tree-view-create-diagram" />
          <menuitem action="tree-view-delete-diagram" />
          <separator />
          <menuitem action="tree-view-refresh" />
        </popup>
      </ui>
    """

    def __init__(self):
        ToplevelWindow.__init__(self)
        self._filename = None
        # Map tab contents to DiagramTab
        self.notebook_map = {}
        # Tree view:
        self._tree_view = None 

        self.action_group = build_action_group(self)
        for name, label in (('file', '_File'),
                             ('edit', '_Edit'),
                             ('diagram', '_Diagram'),
                             ('tools', '_Tools'),
                             ('window', '_Window'),
                             ('help', '_Help')):
            a = gtk.Action(name, label, None, None)
            a.set_property('hide-if-empty', False)
            self.action_group.add_action(a)
        self._tab_ui_settings = None

    def get_model(self):
        """
        Return the gtk.TreeModel associated with the main window
        (shown on the left side in a TreeView).
        """
        return self._tree_view.get_model()

    tree_model = property(lambda s: s.tree_view.get_model())

    def get_tree_view(self):
        """
        Get the gtk.TreeView widget that visualized the TreeModel.
        See also get_model().
        """
        return self._tree_view

    tree_view = property(lambda s: s._tree_view)

    def set_filename(self, filename):
        """
        Set the file name of the currently opened model.
        """
        self._filename = filename

        # Add to recent files list
        if filename:
            recent_files = self.properties.get('recent-files', []) 
            if filename not in recent_files:
                recent_files = [filename] + recent_files[:8]
                self.properties.set('recent-files', recent_files)
                # TODO: notify recent files manager
                #self.action_manager.get_slot('RecentFiles').rebuild()

    def get_filename(self):
        """
        Return the file name of the currently opened model.
        """
        return self._filename

    def get_current_diagram_tab(self):
        """
        Get the currently opened and viewed DiagramTab, shown on the right
        side of the main window.
        See also: get_current_diagram(), get_current_diagram_view().
        """
        return self.get_current_tab()

    def get_current_diagram(self):
        """
        Return the Diagram associated with the viewed DiagramTab.
        See also: get_current_diagram_tab(), get_current_diagram_view().
        """
        tab = self.get_current_diagram_tab()
        return tab and tab.get_diagram()

    def get_current_diagram_view(self):
        """
        Return the DiagramView associated with the viewed DiagramTab.
        See also: get_current_diagram_tab(), get_current_diagram().
        """
        tab = self.get_current_diagram_tab()
        return tab and tab.get_view()

    def ask_to_close(self):
        """
        Ask user to close window.
        """
        dialog = gtk.MessageDialog(self.window,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO,
            _("Quit Gaphor?"))
        answer = dialog.run()
        dialog.destroy()
        return answer == gtk.RESPONSE_YES

    def show_diagram(self, diagram):
        """
        Show a Diagram element in a new tab.
        If a tab is already open, show that one instead.
        """
        # Try to find an existing window/tab and let it get focus:
        for tab in self.get_tabs():
            if tab.get_diagram() is diagram:
                self.set_current_page(tab)
                return tab

        tab = DiagramTab(self)
        tab.set_diagram(diagram)
        widget = tab.construct()
        self.add_tab(tab, widget, tab.title)
        self.set_current_page(tab)

        return tab

    def ui_component(self):
        """
        Create the widgets that make up the main window.
        """
        model = namespace.NamespaceModel(self.element_factory)
        view = namespace.NamespaceView(model, self.element_factory)
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.set_shadow_type(gtk.SHADOW_IN)
        scrolled_window.add(view)
        
        view.connect_after('event-after', self._on_view_event)
        view.connect('row-activated', self._on_view_row_activated)
        #view.connect_after('cursor-changed', self._on_view_cursor_changed)

        vbox = gtk.VBox()
        vbox.pack_start(scrolled_window, expand=True)

        paned = gtk.HPaned()
        paned.set_property('position', 160)
        paned.pack1(vbox)
        
        notebook = gtk.Notebook()
        notebook.set_scrollable(True)
        notebook.set_show_border(False)

        notebook.connect_after('switch-page', self._on_notebook_switch_page)

        self.objectInspector = ObjectInspector()
        #self.objectInspector.set_size_request(-1, 50)

        diagramReceivedFocus = component.adapter(IDiagramElementReceivedFocus)(
            self.objectInspector)
        component.provideHandler(diagramReceivedFocus)
        
        second_paned = gtk.VPaned()
        second_paned.set_property('position',
                                 int(self.properties.get('ui.object-inspector-position', 600)))
        second_paned.pack1(notebook)
        second_paned.pack2(self.objectInspector)
        second_paned.show_all()
        paned.pack2(second_paned)
        paned.show_all()

        second_paned.connect('notify::position',
                            self._on_object_inspector_notify_position)

        self.notebook = notebook
        self._tree_view = view

        vbox.set_border_width(3)

        #toolbox = Toolbox(self.menu_factory, self.toolbox)
        #toolbox.construct()
        #vbox.pack_start(toolbox, expand=False)
        #toolbox.show()

        #self._toolbox = toolbox

        return paned

    def construct(self):
        super(MainWindow, self).construct()

        self.window.connect('delete-event', self._on_window_delete)

        # We want to store the window size, so it can be reloaded on startup
        self.window.set_property('allow-shrink', True)
        self.window.connect('size-allocate', self._on_window_size_allocate)
        self.window.connect('destroy', self._on_window_destroy)


    # Notebook methods:

    def add_tab(self, tab_id, contents, label):
        """
        Create a new tab on the notebook with window as its contents.
        Returns: The page number of the tab.
        """
        self.notebook_map[contents] = tab_id
        #contents.connect('destroy', self._on_tab_destroy)
        l = gtk.Label(label)
        # Note: append_page() emits switch-page event
        self.notebook.append_page(contents, l)
        page_num = self.notebook.page_num(contents)
        #self.notebook.set_current_page(page_num)
        return page_num

    def get_current_tab(self):
        """
        Return the window (DiagramTab) that is currently visible on the
        notebook.
        """
        current = self.notebook.get_current_page()
        content = self.notebook.get_nth_page(current)
        return self.notebook_map.get(content)

    def set_current_page(self, tab):
        """
        Force a specific tab (DiagramTab) to the foreground.
        """
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

    def remove_tab(self, tab):
        """
        Remove the tab from the notebook. Tab is such a thing as
        a DiagramTab.
        """
        for p, t in self.notebook_map.iteritems():
            if tab is t:
                num = self.notebook.page_num(p)
                self.notebook.remove_page(num)
                del self.notebook_map[p]
                return

    def select_element(self, element):
        """
        Select an element from the Namespace view.
        The element is selected. After this an action may be executed,
        such as OpenModelElement, which will try to open the element (if it's
        a Diagram).
        """
        path = self.get_model().path_from_element(element)
        #log.debug("PATH = %s" % path)
        # Expand the first row:
        self.get_tree_view().expand_row(path[:-1], False)
        # Select the diagram, so it can be opened by the OpenModelElement action
        selection = self.get_tree_view().get_selection()
        selection.select_path(path)
        #self.action_manager.execute('SelectRow')


    # Signal callbacks:

    def _on_window_destroy(self, window):
        """
        Window is destroyed... Quit the application.
        """
        self._tree_view = None
        self.window = None
        gtk.main_quit()

    def _on_tab_destroy(self, widget):
        tab = self.notebook_map[widget]
        assert isinstance(tab, DiagramTab)
        self.remove_tab(tab)

    def _on_window_delete(self, window = None, event = None):
        return not self.ask_to_close()

    def _on_view_event(self, view, event):
        """
        Show a popup menu if button3 was pressed on the TreeView.
        """
        # handle mouse button 3:
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            menu = self.ui_manager.get_widget('/namespace-popup')
            menu.popup(None, None, None, event.button, event.time)


    def _on_view_row_activated(self, view, path, column):
        """
        Double click on an element in the tree view.
        """
        self.action_manager.execute('tree-view-open')

    #def _on_view_cursor_changed(self, view):
    #    """
    #    Another row is selected, execute a dummy action.
    #    """
    #    #self.action_manager.execute('SelectRow')
    #    pass

    def _on_notebook_switch_page(self, notebook, tab, page_num):
        """
        Another page (tab) is put on the front of the diagram notebook.
        A dummy action is executed.
        """
        log.debug('Switching page to %d' % page_num)
        if self._tab_ui_settings:
            action_group, ui_id = self._tab_ui_settings
            self.ui_manager.remove_action_group(action_group)
            self.ui_manager.remove_ui(ui_id)
        #    self.ui_manager.ensure_update()

        content = self.notebook.get_nth_page(page_num)
        tab = self.notebook_map.get(content)
        assert isinstance(tab, DiagramTab), str(tab)
        
        self.ui_manager.insert_action_group(tab.action_group, -1)
        ui_id = self.ui_manager.add_ui_from_string(tab.menu_xml)
        self._tab_ui_settings = tab.action_group, ui_id
        #self.ui_manager.ensure_update()
        log.debug('Menus updated with %s, %d' % self._tab_ui_settings)

    def _on_window_size_allocate(self, window, allocation):
        """
        Store the window size in a property.
        """
        self.properties.set('ui.window-size', (allocation.width, allocation.height))

    def _on_object_inspector_notify_position(self, paned, arg):
        self.properties.set('ui.object-inspector-position',
                     paned.get_position())

    # Actions:

    @action(name='file-quit', stock_id='gtk-quit')
    def quit(self):
        self.ask_to_close() and gtk.main_quit()

    @action(name='tree-view-open', label='_Open')
    def tree_view_open_selected(self):
        element = self._tree_view.get_selected_element()
        if isinstance(element, UML.Diagram):
            self.show_diagram(element)
        else:
            log.debug('No action defined for element %s' % type(element).__name__)

    @action(name='tree-view-rename', label=_('Rename'))
    def tree_view_rename_selected(self):
        view = self.get_tree_view()
        element = view.get_selected_element()
        path = view.get_model().path_from_element(element)
        column = view.get_column(0)
        cell = column.get_cell_renderers()[1]
        cell.set_property('editable', 1)
        cell.set_property('text', element.name)
        view.set_cursor(path, column, True)
        cell.set_property('editable', 0)

    @action(name='tree-view-create-diagram', label=_('_New diagram'), stock_id='gaphor-diagram')
    def tree_view_create_diagram(self):
        element = self._tree_view.get_selected_element()
        diagram = self.element_factory.create(UML.Diagram)
        diagram.package = element

        diagram.name = '%s diagram' % element.name

        self.select_element(diagram)
        self.show_diagram(diagram)
        self.tree_view_rename_selected()

    @action(name='tree-view-delete-diagram', label=_('_Delete diagram'), stock_id='gtk-delete')
    def tree_view_delete_diagram(self):
        diagram = self._tree_view.get_selected_element()
        assert isinstance(diagram, UML.Diagram)
        m = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,
                              gtk.BUTTONS_YES_NO,
                              'Do you really want to delete diagram %s?\n\n'
                              'This will possibly delete diagram items\n'
                              'that are not shown in other diagrams.\n'
                              'This operation is not undoable!' \
                              % (diagram.name or '<None>'))
        if (m.run() == gtk.RESPONSE_YES):
            diagram.unlink()
        m.destroy()

    @action(name='tree-view-refresh', label=_('_Refresh'))
    def tree_view_refresh(self):
        self._tree_view.get_model().refresh()


gtk.accel_map_add_filter('gaphor')

#@component.adapter(IServiceEvent)
#def on_undo(*args):
#    from gaphor.application import Application
#    Application.get_service('action_manager').execute('UndoStack')
#
#component.provideHandler(on_undo)

# vim:sw=4:et:ai
