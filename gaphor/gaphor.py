#!/usr/bin/env python
# vim:sw=4
"""
This is the main package for Gaphor, a Python based UML editor.

An extra function is installed in the builtin namespace: GaphorResource().
This function can be used to locate application wide resources, such as
object factories.
"""

import misc.singleton
import misc.logger
import config
import types

class GaphorError(Exception):
    """
    Gaphor specific exception class
    """
    def __init__(self, args=None):
            self.args = args



class Gaphor(misc.singleton.Singleton):
    """
    Gaphor main app. This is a Singleton object that is used as a access point
    to unique resources within Gaphor. The method main() is called once to
    start an interactive instance of Gaphor. If an application wants to use
    Gaphor's functionallity, but not the GUI, that application should not call
    main().

    Resources can be accessed through the get() method. Resources can be
    Python classes or strings. In case of classes, get() will try to find an
    existing class, if none is found, it will create one. No parameters will
    be passed to that class.

    In case of a string resource, a lookup will be done in the GConf
    configuration tree. This is currently not implemented though...
    """

    NAME='gaphor'
    VERSION=config.VERSION
    TITLE='Gaphor v' + VERSION

    __resources = { }
#    __conf = Conf(NAME)

    def init(self, install=1):
	self.__main_window = None
	if install:
	    self.install_gettext()

    def install_gettext(self):
	import gettext
	gettext.install(config.GETTEXT_PACKAGE, unicode=1)

    def main(self):
	import bonobo
	import gnome
	# Initialize gnome.ui, since we need some definitions from it
	import gnome.ui
	from ui import MainWindow
	gnome.init(Gaphor.NAME, Gaphor.VERSION)
	# should we set a default icon here or something?
	self.__main_window = MainWindow()
	self.__main_window.construct()
	# When the state changes to CLOSED, quit the application
	self.__main_window.connect(lambda win: win.get_state() == MainWindow.STATE_CLOSED and bonobo.main_quit())
	#mainwin = GaphorResource(WindowFactory).create(type=MainWindow)

	bonobo.main()
	log.info('Bye!')

    def get_main_window(self):
	return self.__main_window

    def get_resource(resource):
	"""
	*Static method*
	Locate a resource. Resource should be the class of the resource to
	look for or a string. In case of a string the resource will be looked
	up in the GConf configuration.

	example: Get the element factory:
		elemfact = Gaphor.get(gaphor.UML.ElementFactory)

	or (with Gaphor installed in the builtin namespace):
		elemfact = GaphorResource(gaphor.UML.ElementFactory)
	"""
	if isinstance (resource, types.StringType):
	    hash = Gaphor.__resources
	    if hash.has_key(resource):
		return hash[resource]
	else:
	    hash = Gaphor.__resources
	    if hash.has_key(resource):
		return hash[resource]
	    try:
		log.debug('Adding new resource: %s' % resource.__name__)
		r = resource()
		hash[resource] = r
		hash[resource.__name__] = r
		return r
	    except Exception, e:
		raise GaphorError, 'Could not create resource %s (%s)' % (str(resource), str(e))

    get_resource = staticmethod(get_resource)


import __builtin__
__builtin__.__dict__['GaphorError'] = GaphorError
__builtin__.__dict__['GaphorResource'] = Gaphor.get_resource
__builtin__.__dict__['log'] = misc.logger.Logger()

