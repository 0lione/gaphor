# vim:sw=4:et
'''
Feature diagram item. Feature is a super class of both Attribute, Operations and
Methods.
'''

import gobject
import pango
import diacanvas
import diacanvas.shape
from diacanvas import CanvasItem, CanvasEditable
from diacanvas.geometry import distance_rectangle_point
from diagramitem import DiagramItem

from gaphor.diagram import initialize_item

class FeatureItem(CanvasItem, CanvasEditable, DiagramItem):
    """FeatureItems are model elements who recide inside a ClassItem, such as
    methods and attributes. Those items can have comments attached, but only on
    the left and right side.
    Note that features can also be used inside objects.
    """
    # Properties, also add the DiagramItem properties here.
    __gproperties__ = {
        'expression':  (gobject.TYPE_STRING, 'expression',
                         'The expression represented by this Feature',
                         '', gobject.PARAM_READWRITE)
    }
    __gproperties__.update(DiagramItem.__gproperties__)

    __gsignals__ = DiagramItem.__gsignals__

    FONT='sans 10'

    def __init__(self, id=None):
        self.__gobject_init__()
        DiagramItem.__init__(self, id)
        self._expression = diacanvas.shape.Text()
        self._expression.set_font_description(pango.FontDescription(FeatureItem.FONT))
        self._expression.set_wrap_mode(diacanvas.shape.WRAP_NONE)
        self.set_flags(diacanvas.COMPOSITE)

    # Ensure we call the right connect functions:
    connect = DiagramItem.connect
    disconnect = DiagramItem.disconnect

    def save(self, save_func):
        for prop in ('affine',):
            self.save_property(save_func, prop)
        DiagramItem.save(self, save_func)
        
    def postload(self):
        if self.subject and self.subject.name:
            self._expression.set_text(self.subject.name)

    def do_set_property(self, pspec, value):
        if pspec.name == 'expression':
            if self.subject:
                self.preserve_property('expression')
                self.subject.parse(value)
                self._expression.set_text(self.subject.render())
                self.request_update()
        else:
            DiagramItem.do_set_property(self, pspec, value)

    def do_get_property(self, pspec):
        if pspec.name == 'expression':
            # TODO:
            return self.subject and self.subject.render() or ''
        else:
            return DiagramItem.do_get_property(self, pspec)

    def get_size(self, update=False):
        """Return the size of the feature. If update == True the item is
        directly updated.
        """
        w, h = self._expression.to_pango_layout(True).get_pixel_size()
        if update:
            self.set_bounds((0, 0, max(10, w), h))
        return w, h

    def set_pos(self, x, y):
        a = self.get_property('affine')
        a = (a[0], a[1], a[2], a[3], x, y)
        self.set(affine=a)

    def on_subject_notify(self, pspec, notifiers=()):
        DiagramItem.on_subject_notify(self, pspec, ('name',) + notifiers)
        self._expression.set_text(self.subject and self.subject.name or '')

    def on_subject_notify__name(self, subject, pspec):
        assert self.subject is subject
        self._expression.set_text(self.subject.name)
        self.request_update()

    def on_text_notify(self, pspec):
        if self.subject and self.text != self.subject.name:
            self.subject.name = self.text
            #self.parent.request_update()

    # CanvasItem callbacks:

    def on_update(self, affine):
        CanvasItem.on_update(self, affine)
        #log.debug('FeatureItem.on_update: %f, %f' % self.get_size(True))

    def on_event(self, event):
        if event.type == diacanvas.EVENT_BUTTON_PRESS:
            log.debug('FeatureItem.on_event: button_press')
            return True
        if event.type == diacanvas.EVENT_2BUTTON_PRESS:
            log.debug('FeatureItem.on_event: 2button_press')
            self.start_editing(self._expression)
            return True
        else:
            return CanvasItem.on_event(self, event)

    def on_point(self, x, y):
        return distance_rectangle_point(self.get_bounds(), (x, y))

    def on_shape_iter(self):
        return iter([self._expression])

    # Editable

    def on_editable_start_editing(self, shape):
        #self.preserve_property('expression')
        pass

    def on_editable_editing_done(self, shape, new_text):
        self.set_property('expression', new_text)
        #if new_text != self.subject.name:
        #    self.subject.name = new_text
        #self.request_update()

initialize_item(FeatureItem)
