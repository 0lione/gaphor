# vim: sw=4
'''diagram.py
This module contains a model elements (!) Diagram which is the abstract
representation of a UML diagram. Diagrams can be visualized and edited.'''

__author__ = 'Arjan Molenaar'
__version__ = '$revision$'
__date__ = '$date$'

from uml2 import Namespace, PackageableElement
import gobject
import diacanvas
import gaphor.misc.uniqueid as uniqueid

class DiagramCanvas(diacanvas.Canvas):
    '''
    Some additions to diacanvas.Canvas class, esp. load and save functionallity.
    '''
    _savable_canvas_properties = [ 'extents', 'static_extents',
	    'snap_to_grid', 'grid_int_x', 'grid_int_y', 'grid_ofs_x',
	    'grid_ofs_y', 'grid_color', 'grid_bg' ]

    def save(self, save_func):
	for prop in DiagramCanvas._savable_canvas_properties:
	    save_func(prop, self.get_property(prop))
	save_func('root_affine', self.root.get_property('affine'))
	# Save child items:
	for item in self.root.children:
	    save_func(None, item) #item.save(canvas_store.new(item))

    def load(self, name, value):
	self.set_property ("allow_undo", 0)

	# First create the canvas:
	if name == 'root_affine':
	    self.root.set_property('affine', eval(value))
	else:
	    self.set_property (name, eval(value))

	self.update_now ()

    def postload(self):
	self.update_now ()

	# setting allow-undo to 1 here will cause update info from later
	# created elements to be put on the undo stack.
	self.clear_undo()
	self.clear_redo()
	self.set_property ("allow_undo", 1)

gobject.type_register(DiagramCanvas)


class Diagram(Namespace, PackageableElement):

    def __init__(self, id):
	super(Diagram, self).__init__(id)
        self.canvas = DiagramCanvas()
	self.canvas.set_undo_stack_depth(10)
	self.canvas.set_property ("allow_undo", 1)

    def save(self, save_func):
	super(Diagram, self).save(save_func)
	save_func('canvas', self.canvas)

    def create(self, type):
	"""Create a new canvas item on the canvas. It is created with
	a unique ID and it is attached to the diagram's root item."""
	assert issubclass(type, diacanvas.CanvasItem)
	obj = type(uniqueid.generate_id())
	obj.set_property('parent', self.canvas.root)
	return obj

