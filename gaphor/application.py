"""
The Application object. One application should be available.

All important services are present in the application object:
 - plugin manager
 - undo manager
 - main window
 - UML element factory
 - action sets
"""

import pkg_resources
from zope import component
from gaphor.interfaces import IService
from gaphor.event import ServiceInitializedEvent, ServiceShutdownEvent
import gaphor.UML


class _Application(object):

    # interface.implements(IApplication)
    
    def __init__(self):
        self._uninitialized_services = {}

    def init(self):
        """
        Initialize the application.
        """
        self.load_services()
        self.init_all_services()

    def load_services(self):
        """
        Load services from resources.

        Services are registered as utilities in zope.component.
        Service should provide an interface gaphor.interfaces.IService.
        """
        for ep in pkg_resources.iter_entry_points('gaphor.services'):
            #print ep, dir(ep)
            log.debug('found entry point service.%s' % ep.name)
            cls = ep.load()
            if not IService.implementedBy(cls):
                raise 'MisConfigurationException', 'Entry point %s doesn''t provide IService' % ep.name
            srv = cls()
            self._uninitialized_services[ep.name] = srv

    def init_all_services(self):
        while self._uninitialized_services:
            self.init_service(self._uninitialized_services.iterkeys().next())

    def init_service(self, name):
        """
        Initialize a not yet initialized service.

        Raises ComponentLookupError if the service has nor been found
        """
        try:
            srv = self._uninitialized_services.pop(name)
        except KeyError:
            raise component.ComponentLookupError(IService, name)
        else:
            log.info('initializing service service.%s' % name)
            # TODO: do init() before provideUtility!
            component.provideUtility(srv, IService, name)
            srv.init(self)
            component.handle(ServiceInitializedEvent(srv))
            return srv

    distribution = property(lambda s: pkg_resources.get_distribution('gaphor'),
                            doc='Get the PkgResources distribution for Gaphor')

    def get_service(self, name):
        try:
            return component.getUtility(IService, name)
        except component.ComponentLookupError:
            return self.init_service(name)

    def run(self):
        import gtk
        gtk.main()

    def shutdown(self):
        for srv in component.getAllUtilitiesRegisteredFor(IService):
            srv.shutdown()
            component.handle(ServiceShutdownEvent(srv))


# Make sure there is only one!
Application = _Application()

def restart():
    Application.shutdown()
    Application = _Application()


# vim:sw=4:et:ai
