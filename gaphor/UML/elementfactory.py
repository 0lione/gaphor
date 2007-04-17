# vim: sw=4
"""elementfactory.py
"""

from zope import interface
from zope import component
from gaphor.misc import uniqueid, odict
from gaphor.UML.element import Element
from gaphor.UML.diagram import Diagram
from gaphor.UML.interfaces import IElementCreateEvent, IElementDeleteEvent, \
                                  IFlushFactoryEvent, IModelFactoryEvent, \
                                  IService
from gaphor.UML.event import ElementCreateEvent, ElementDeleteEvent, \
                             FlushFactoryEvent, ModelFactoryEvent


class ElementFactory(object):
    """The ElementFactory is used to create elements and do lookups to
    elements.

    Notifications are send with as arguments (name, element, *user_data).
    The following names are used:
    create - a new model element is created (element is newly created element)
    remove - a model element is removed (element is to be removed element)
    model - a new model has been loaded (element is None)
    flush - model is flushed: all element are removed from the factory
            (element is None)
    """
    interface.implements(IService)

    def __init__(self):
        self._elements = odict.odict()
        self._observers = list()

    def init(self, app):
        pass

    def shutdown(self):
        pass

    def create(self, type):
        """Create a new model element of type type.
        """
        return self.create_as(type, uniqueid.generate_id())

    def create_as(self, type, id):
        """Create a new model element of type 'type' with 'id' as its ID.
        This method should only be used when loading models.
        """
        assert issubclass(type, Element)
        obj = type(id, self)
        self._elements[id] = obj
        obj.connect('__unlink__', self._element_signal)
        self.notify(obj, 'create')
        component.handle(ElementCreateEvent(self, obj))
        return obj

    def size(self):
        """Return the amount of elements currently in the factory.
        """
        return len(self._elements)

    def lookup(self, id):
        """Find element with a specific id.
        """
        return self._elements.get(id)

    __getitem__ = lookup

    def select(self, expression=None):
        """Iterate elements that comply with expression.
        """
        if expression is None:
            for e in self._elements.itervalues():
                yield e
        else:
            for e in self._elements.itervalues():
                if expression(e):
                    yield e #l.append(e)
        #return l

    def lselect(self, expression=None):
        """Like select(), but returns a list.
        """
        return list(self.select(expression))

    def keys(self):
        """Return a list with all id's in the factory.
        """
        return self._elements.keys()

    def iterkeys(self):
        """Return a iterator with all id's in the factory.
        """
        return self._elements.iterkeys()

    def values(self):
        """Return a list with all elements in the factory.
        """
        return self._elements.values()

    def itervalues(self):
        """Return a iterator with all elements in the factory.
        """
        return self._elements.itervalues()

    def is_empty(self):
        """Returns True if the factory holds no elements."""
        if self._elements:
            return False
        else:
            return True

    def flush(self):
        """Flush all elements (remove them from the factory)."""
        self.notify(None, 'flush')
        component.handle(FlushFactoryEvent(self))

        # First flush all diagrams:
        for value in list(self.select(lambda e: isinstance(e, Diagram))):
            # Make sure no updates happen while destroying the canvas
            value.canvas.block_updates = True
            value.unlink()

        for key, value in self._elements.items():
            #print 'ElementFactory: unlinking', value
            #print 'references:', gc.get_referrers(value)
            value.unlink()

        assert len(self._elements) == 0, 'Still items in the factory: %s' % str(self._elements.values())

        # Force Garbage collection, so memory allocated by items is freed.
        import gc
        for i in range(4): gc.collect()

    def swap_element(self, element, new_class):
	assert element in self._elements.values()
        if element.__class__ is not new_class:
            element.__class__ = new_class
            element.notify('__class__')

    def connect(self, callback, *data):
        """Attach 'callback'."""
        self._observers.append((callback,) + data)

    def disconnect(self, callback, *data):
        """Detach a callback identified by it's data."""
        #print 'disconnect', callback, data
        cb = (callback,) + data
        # Remove all occurences of 'cb' from values
        # (if none is found ValueError is raised).
        try:
            while True:
                self._observers.remove(cb)
        except ValueError:
            pass

    def notify(self, element, name):
        """Send notification to attached callbacks that a property
        has changed. This is usually only called by the properties."""
        for cb_data in self._observers:
            try:
                apply(cb_data[0], (element, name) + cb_data[1:])
            except Exception, e:
                log.error('Notification of %s failed.' % cb_data[0], e)

    def notify_model(self):
        self.notify(None, 'model')
        component.handle(ModelFactoryEvent(self))

    def _element_signal(self, element, pspec):
        """Remove an element from the factory """
        #log.debug('element %s send signal %s' % (element, name))
        if pspec == '__unlink__' and self._elements.has_key(element.id):
            #log.debug('Unlinking element: %s' % element)
            # TODO: make undo action
            del self._elements[element.id]
            self.notify(element, 'remove')
            component.handle(ElementDeleteEvent(self, element))
#        elif pspec == '__relink__' and not self._elements.has_key(element.id):
#            log.debug('Relinking element: %s' % element)
#            self._elements[element.id] = element
#            self.notify(element, 'create')

component.provideUtility(ElementFactory(), IService, "ElementFactory")



# vim:sw=4:et
