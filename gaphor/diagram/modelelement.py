'''
ModelElement

Abstract base class for element-like Diagram items.
'''
# vim:sw=4

if __name__ == '__main__':
    import sys
    sys.path.append('..')
    del sys

import gobject
import diacanvas as dia
#from metaitem import MetaItem
from UML import Element

__revision__ = '$revision$'
__author__ = 'Arjan J. Molenaar'
__date__ = '$date$'



class ModelElement (dia.CanvasElement, dia.CanvasAbstractGroup):
#    __metaclass__ = MetaItem
    __gproperties__ = {
	'subject': (gobject.TYPE_PYOBJECT, 'subject',
		    'subject held by the model element',
		    gobject.PARAM_READWRITE),
	'auto_resize': (gobject.TYPE_BOOLEAN, 'auto resize',
			'Set auto-resize for the diagram item',
			1, gobject.PARAM_READWRITE),
    }

    def __init__(self):
	self.__gobject_init__()
	self.subject = None
	self.auto_resize = 0
	self.connect ('notify::parent', self.on_parent_notify)

    def do_set_property (self, pspec, value):
	if pspec.name == 'subject':
	    print 'Setting subject:', value
	    self.preserve_property('subject')
	    if value != self.subject:
		if self.subject:
		    self.subject.disconnect(self.on_subject_update)
		value.connect(self.on_subject_update)
		self.subject = value

	elif pspec.name == 'auto_resize':
	    self.auto_resize = value
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name

    def do_get_property(self, pspec):
	if pspec.name == 'subject':
	    return self.subject
	elif pspec.name == 'auto_resize':
	    return self.auto_resize
	else:
	    raise AttributeError, 'Unknown property %s' % pspec.name

    # DiaCanvasItem callbacks
    def on_glue(self, handle, wx, wy):
	return dia.CanvasElement.on_glue (self, handle, wx, wy)

    def on_connect_handle (self, handle):
	return dia.CanvasElement.on_connect_handle (self, handle)

    def on_disconnect_handle (self, handle):
	return dia.CanvasElement.on_disconnect_handle (self, handle)

    def on_parent_notify (self):
        if self.parent:
	    print 'Have Parent'
	    self.subject.undo_presentation (self)
	else:
	    print 'No parent...'
	    self.subject.remove_presentation_undoable (self)

    def on_subject_update (self, name):
	if name == '__unlink__':
	    self.set_property ('subject', None)
	    self.set_property ('parent', None)
	else:
	    print 'ModelElement: unhandled signal "%s"' % str(name)

gobject.type_register(ModelElement)
dia.set_callbacks(ModelElement)
dia.set_groupable(ModelElement)

if __name__ == '__main__':
    me = ModelElement()
    print me, me.__gtype__
