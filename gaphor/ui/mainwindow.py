
# vim:sw=4

import gtk
import bonobo.ui
import gnome.ui
import namespace
import command.file
import command.diagram
import command.about
import gaphor.UML as UML
import gaphor.config
from gaphor.misc.menufactory import MenuFactory, Menu, MenuItem, MenuSeparator, MenuPlaceholder, MenuStockItem
import stock


class MainWindow:
    """
    The main window for the application. It contains a Namespace-based tree
    view and a menu and a statusbar.
    """

    def __init__(self):
	pass

    def __obsoleted_code(self):
	recent_files = MenuPlaceholder()
	open_windows = MenuPlaceholder()
	# Menu items have the following structure:
	# ( Name, Comment, (ctrl) + Modifier, Command or Submenu )
	menu =  Menu(
		    MenuItem(name=_('_File'), submenu=(
			MenuStockItem(stock_id=gtk.STOCK_NEW,
				 comment=_('Create a new model'),
				 command=command.file.NewCommand()),
	 		MenuStockItem(stock_id=gtk.STOCK_OPEN,
				 comment='Open an existing model',
				 command=command.file.OpenCommand()),
			MenuStockItem(stock_id=gtk.STOCK_SAVE,
				 comment='Save current model',
				 command=command.file.SaveCommand()),
			MenuStockItem(stock_id=gtk.STOCK_SAVE_AS,
				 comment='Save current model as...',
				 command=command.file.SaveAsCommand()),
			MenuSeparator(),
			recent_files,
			MenuSeparator(),
			MenuStockItem(stock_id=gtk.STOCK_QUIT,
				 comment='Exit Gaphor',
				 command=command.file.QuitCommand())
			,)),
		    MenuItem(name='_Insert', submenu=(
			MenuStockItem(stock_id=stock.STOCK_DIAGRAM,
				comment='Create a new diagram',
				command=command.diagram.CreateDiagramCommand())
			,)),
		    MenuItem(name='_Windows', submenu=(
			open_windows,
			MenuSeparator(),
			MenuItem(name='_Close all',
				comment='Close all open windows',
				command=None)
		        ,)),
		    MenuItem(name='_Help', right=1, submenu=(
		    	MenuItem(name='_About',
				comment='About Gaphor',
				command=command.about.AboutCommand())
			,))
		    )
	app = gnome.ui.App (name, title)
	app.set_default_size (200, 300)
	accelgroup = gtk.AccelGroup()
	app.add_accel_group (accelgroup)
	app_bar = gnome.ui.AppBar (has_progress=0, has_status=1,
				   interactivity=gnome.ui.PREFERENCES_USER)
	app.set_statusbar(app_bar)
	model = namespace.NamespaceModel(GaphorResource(UML.ElementFactory))
	view = namespace.NamespaceView(model)

	menu_factory = MenuFactory(menu=menu, accelgroup=accelgroup,
				   statusbar=app_bar)
	menubar = menu_factory.create_menu()

	app.set_menus(menubar)
	app.set_contents(view)

	self.__app = app
	self.__model = model
	self.__view = view
	self.__menubar = menubar
	self.__recent_files = recent_files
	self.__open_windows = open_windows
	app.show_all()
	
    def get_title(self):
	return 'Gaphor v0.1.0'

    def get_name(self):
	return 'gaphor.main'

    def create_contents(self):
	model = namespace.NamespaceModel(GaphorResource(UML.ElementFactory))
	view = namespace.NamespaceView(model)
	self.__model = model
	self.__view = view

	return view

    def get_ui_xml_file(self):
	return 'gaphor-ui.xml'

    def get_window(self):
	return self.__app

    def get_default_size(self):
	return (200, 300)

    def add_window(self, window, name, command=None):
	self.__open_windows.add(key=window, name=name, command=command)

    def remove_window(self, window):
	self.__open_windows.remove(window)
