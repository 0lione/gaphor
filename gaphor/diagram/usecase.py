'''
eseCaseItempango diagram item
'''
# vim:sw=4

from modelelement import ModelElementItem
import diacanvas
import gobject
import pango

class UseCaseItem(ModelElementItem):
    MARGIN_X=60
    MARGIN_Y=30
    FONT='sans bold 10'

    def __init__(self):
	ModelElementItem.__init__(self)
	self.set(height=50, width=100)
	self.__border = diacanvas.shape.Ellipse()
	self.__border.set_line_width(2.0)
	self.__name = diacanvas.CanvasText()
	self.add_construction(self.__name)
	assert self.__name != None
	font = pango.FontDescription(UseCaseItem.FONT)
	self.__name.set(font=font, width=self.width,
			alignment=pango.ALIGN_CENTER)
	# Center the text:
	w, h = self.__name.get_property('layout').get_pixel_size()
	#print 'UseCaseItem:',w,h
	self.__name.move(0, (self.height - h) / 2)
	self.__name.set(height=h)
	# Hack since self.<method> is not GC'ed
	self.__name.connect('text_changed', self.on_text_changed)

    def __name_update (self):
	'''Center the name text in the usecase.'''
	w, h = self.__name.get_property('layout').get_pixel_size()
	self.set(min_width=w + UseCaseItem.MARGIN_X,
		 min_height=h + UseCaseItem.MARGIN_Y)
	a = self.__name.get_property('affine')
	aa = (a[0], a[1], a[2], a[3], a[4], (self.height - h) / 2)
	self.__name.set(affine=aa, width=self.width, height=h)

    def load(self, store):
	ModelElementItem.load(self, store)
	self.__name_update()

    def on_update(self, affine):
	ModelElementItem.on_update(self, affine)
	self.__border.ellipse(center=(self.width / 2, self.height / 2), width=self.width, height=self.height)
	self.expand_bounds(1.0)
	self.__border.request_update()
	self.update_child(self.__name, affine)

    def on_handle_motion (self, handle, wx, wy, mask):
	retval  = ModelElementItem.on_handle_motion(self, handle, wx, wy, mask)
	self.__name_update()
	return retval

    def on_event (self, event):
	if event.type == diacanvas.EVENT_KEY_PRESS:
	    self.__name.focus()
	    self.__name.on_event (event)
	    return True
	else:
	    return ModelElementItem.on_event(self, event)

    def on_get_shape_iter(self):
	return self.__border

    def on_shape_next(self, iter):
	return None

    def on_shape_value(self, iter):
	return iter

    # Groupable

    def on_groupable_add(self, item):
	return 0

    def on_groupable_remove(self, item):
	'''Do not allow the name to be removed.'''
	self.emit_stop_by_name('remove')
	return 0

    def on_groupable_get_iter(self):
	return self.__name

    def on_groupable_next(self, iter):
	return None

    def on_groupable_value(self, iter):
	return iter

    def on_groupable_length(self):
	return 1

    def on_groupable_pos(self, item):
	if item == self.__name:
	    return 0
	else:
	    return -1

    def on_subject_update(self, name, old_value, new_value):
	if name == 'name':
	    self.__name.set(text=self.subject.name)
	    self.__name_update()
	else:
	    ModelElementItem.on_subject_update(self, name, old_value, new_value)

    def on_text_changed(self, text_item, text):
	if text != self.subject.name:
	    self.subject.name = text

gobject.type_register(UseCaseItem)

