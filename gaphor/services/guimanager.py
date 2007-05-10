"""
"""

import pkg_resources
from zope import interface
from gaphor.interfaces import IService, IActionProvider


class GUIManager(object):

    interface.implements(IService)

    def __init__(self):
        self._ui_components = dict()

    main_window = property(lambda s: s._main_window)

    def init(self, app):
        self._app = app

        #self.init_pygtk()
        self.init_ui_manager()
        self.init_stock_icons()
        self.init_actions()
        self.init_ui_components()
        self.init_main_window()

    def init_pygtk(self):
        """
        Make sure we have GTK+ >= 2.0
        """
        import pygtk
        pygtk.require('2.0')
        del pygtk

    def init_ui_manager(self):
        import gtk
        self.ui_manager = gtk.UIManager()

    def init_stock_icons(self):
        # Load stock items
        import gaphor.ui.stock
        gaphor.ui.stock.load_stock_icons()

    def init_ui_components(self):
        from gaphor.ui.interfaces import IUIComponent
        for ep in pkg_resources.iter_entry_points('gaphor.uicomponents'):
            log.debug('found entry point uicomponent.%s' % ep.name)
            cls = ep.load()
            if not IUIComponent.implementedBy(cls):
                raise 'MisConfigurationException', 'Entry point %s doesn''t provide IUIComponent' % ep.name
            uicomp = cls()
            uicomp.ui_manager = self.ui_manager
            self._ui_components[ep.name] = uicomp
            if IActionProvider.providedBy(uicomp):
                uicomp.__ui_merge_id = self.ui_manager.add_ui_from_string(uicomp.menu_xml)
                self.ui_manager.insert_action_group(uicomp.action_group, -1)
                
    def init_main_window(self):
        from gaphor.ui.accelmap import load_accel_map
        from gaphor.ui.mainwindow import MainWindow
        import gtk

        load_accel_map()
        self._main_window = self._ui_components['mainwindow']
        self._main_window.construct()

        # When the state changes to CLOSED, quit the application
        #self._main_window.connect(lambda win: win.get_state() == MainWindow.STATE_CLOSED and gtk.main_quit()) 
    def init_actions(self):
        from gaphor.actions import diagramactions, editoractions, mainactions
        from gaphor.actions import itemactions, placementactions

    def shutdown(self):
        #self._main_window.close()
        from gaphor.ui.accelmap import save_accel_map
        save_accel_map()

# vim:sw=4:et:ai
