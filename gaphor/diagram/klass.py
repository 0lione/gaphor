"""ClassItem diagram item
"""
# vim:sw=4:et

# TODO: make loading of features work (adjust on_groupable_add)
#       probably best to do is subclass Feature in OperationItem and A.Item

from __future__ import generators

import gobject
import pango
import diacanvas

import gaphor.UML as UML
from gaphor.diagram import initialize_item

from classifier import ClassifierItem
from feature import FeatureItem
from attribute import AttributeItem
from operation import OperationItem

class Compartment(list):
    """Specify a compartment in a class item.
    A compartment has a line on top and a list of FeatureItems.
    """

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.visible = True
        self.separator = diacanvas.shape.Path()
        self.separator.set_line_width(2.0)
        self.sep_y = 0

    def save(self, save_func):
        #log.debug('Compartment.save: %s' % self)
        for item in self:
            save_func(None, item)

    def pre_update(self, width, height, affine):
        """Calculate the size of the feates in this compartment.
        """
        if self.visible:
            self.sep_y = height
            height += ClassItem.COMP_MARGIN_Y
            for f in self:
                w, h = f.get_size(update=True)
                #log.debug('feature: %f, %f' % (w, h))
                f.set_pos(ClassItem.COMP_MARGIN_X, height)
                f.set_property('visible', True)
                height += h
                width = max(width, w + 2 * ClassItem.COMP_MARGIN_X)
            height += ClassItem.COMP_MARGIN_Y
        else:
            for f in self:
                f.set_property('visible', False)
        return width, height

    def update(self, width, affine):
        if self.visible:
            for f in self:
                self.owner.update_child(f, affine)
            self.separator.line(((0, self.sep_y), (width, self.sep_y)))


class ClassItem(ClassifierItem, diacanvas.CanvasGroupable):
    """This item visualizes a Class instance.

    A ClassItem contains two compartments (Compartment): one for
    attributes and one for operations. To add and remove such features
    the ClassItem implements the CanvasGroupable interface.
    Items can be added by callling class.add() and class.remove().
    This is used to handle CanvasItems, not UML objects!
    """
    __gproperties__ = {
        'show-attributes': (gobject.TYPE_BOOLEAN, 'show attributes',
                            '',
                            1, gobject.PARAM_READWRITE),
        'show-operations': (gobject.TYPE_BOOLEAN, 'show operations',
                            '',
                            1, gobject.PARAM_READWRITE),
    }
    HEAD_MARGIN_X=30
    HEAD_MARGIN_Y=10
    COMP_MARGIN_X=5
    COMP_MARGIN_Y=5

    def __init__(self, id=None):
        ClassifierItem.__init__(self, id)
        self.set(height=50, width=100)
        self._attributes = Compartment('attributes', self)
        self._operations = Compartment('operations', self)
        self._border = diacanvas.shape.Path()
        self._border.set_line_width(2.0)

    def save(self, save_func):
        # Store the show- properties *before* the width/height properties,
        # otherwise the classes will unintentionally grow due to "visible"
        # attributes or operations.
        self.save_property(save_func, 'show-attributes')
        self.save_property(save_func, 'show-operations')
        ClassifierItem.save(self, save_func)

    def postload(self):
        ClassifierItem.postload(self)
        self.sync_compartments()

    def do_set_property(self, pspec, value):
        if pspec.name == 'show-attributes':
            self.preserve_property('show-attributes')
            self._attributes.visible = value
            self.request_update()
        elif pspec.name == 'show-operations':
            self.preserve_property('show-operations')
            self._operations.visible = value
            self.request_update()
        else:
            ClassifierItem.do_set_property(self, pspec, value)

    def do_get_property(self, pspec):
        if pspec.name == 'show-attributes':
            return self._attributes.visible
        elif pspec.name == 'show-operations':
            return self._operations.visible
        return ClassifierItem.do_get_property(self, pspec)

    def has_capability(self, capability):
        #log.debug('has_capability: %s' % capability)
        if capability == 'show-attributes':
            return self._attributes.visible
        elif capability == 'show-operations':
            return self._operations.visible
        return ClassifierItem.has_capability(self, capability)

    def _create_attribute(self, attribute):
        """Create a new attribute item.
        """
        new = AttributeItem()
        new.subject = attribute
        self.add(new)

    def _create_operation(self, operation):
        """Create a new operation item.
        """
        new = OperationItem()
        new.subject = operation
        self.add(new)
        
    def sync_features(self, features, compartment, creator=None):
        """Common function for on_subject_notify__ownedAttribute() and
        on_subject_notify__ownedOperation().
        - features: the list of attributes or operations in the model
        - compartment: our local representation
        - creator: factory method for creating new attr. or oper.'s
        """
        # Extract the UML elements from the compartment
        my_features = map(getattr, compartment,
                      ['subject'] * len(compartment))

        for a in [f for f in features if f not in my_features]:
            creator(a)

        tmp = [f for f in my_features if f not in features]
        if tmp:
            # Create a feature->item mapping
            mapping = dict(zip(my_features, compartment))
            for a in tmp:
                self.remove(mapping[a])
            
    def sync_compartments(self):
        """Sync the contents of the attributes and operations compartments
        with the data in self.subject.
        """
        attributes = [a for a in self.subject.ownedAttribute if not a.association]
        self.sync_features(attributes, self._attributes, self._create_attribute)
        self.sync_features(self.subject.ownedOperation, self._operations,
                           self._create_operation)

    def on_subject_notify(self, pspec, notifiers=()):
        #log.debug('Class.on_subject_notify(%s, %s)' % (pspec, notifiers))
        ClassifierItem.on_subject_notify(self, pspec, ('ownedAttribute', 'ownedOperation'))
        # Create already existing attributes and operations:
        if self.subject:
            self.sync_compartments()
        self.request_update()

    def on_subject_notify__ownedAttribute(self, subject, pspec=None):
        """Called when the ownedAttribute property of our subject changes.
        """
        #log.debug('on_subject_notify__ownedAttribute')
        # Filter attributes that are connected to an association:
        attributes = [a for a in subject.ownedAttribute if not a.association]
        self.sync_features(attributes, self._attributes, self._create_attribute)

    def on_subject_notify__ownedOperation(self, subject, pspec=None):
        """Called when the ownedOperation property of our subject changes.
        """
        #log.debug('on_subject_notify__ownedOperation')
        self.sync_features(subject.ownedOperation, self._operations,
                                 self._create_operation)

    def on_update(self, affine):
        """Overrides update callback.
        """

        width = 0
        height = ClassItem.HEAD_MARGIN_Y

        compartments = (self._attributes, self._operations)

        # TODO: update stereotype

        # Update class name
        w, name_height = self.get_name_size()
        height += name_height
        name_y = height / 2
        
        height += ClassItem.HEAD_MARGIN_Y
        width = w + ClassItem.HEAD_MARGIN_X

        for comp in compartments:
            width, height = comp.pre_update(width, height, affine)

        self.set(min_width=width, min_height=height)

        #if affine:
        width = max(width, self.width)
        height = max(height, self.height)

        # We know the width of all text components and set it:
        # Note: here the upadte flag is set for all sub-items (again)!
        #    self._name.set_property('width', width)
        self.update_name(x=0, y=name_y, width=width, height=name_height)

        for comp in compartments:
            comp.update(width, affine)

        ClassifierItem.on_update(self, affine)

        self._border.rectangle((0,0),(width, height))
        self.expand_bounds(1.0)

    def on_shape_iter(self):
        yield self._border
        for s in ClassifierItem.on_shape_iter(self):
            yield s
        if self._attributes.visible:
            yield self._attributes.separator
        if self._operations.visible:
            yield self._operations.separator

    # Groupable

    def on_groupable_add(self, item):
        """Add an attribute or operation.
        """
        #if isinstance(item.subject, UML.Property):
        if isinstance(item, AttributeItem):
            #log.debug('Adding attribute %s' % item)
            self._attributes.append(item)
            item.set_child_of(self)
        #elif isinstance(item.subject, UML.Operation):
        elif isinstance(item, OperationItem):
            #log.debug('Adding operation %s' % item)
            self._operations.append(item)
            item.set_child_of(self)
        else:
            log.warning('feature %s is not a Feature' % item)
            return 0
        self.request_update()
        return 1

    def on_groupable_remove(self, item):
        """Remove a feature subitem.
        """
        if item in self._attributes:
            self._attributes.remove(item)
            item.set_child_of(None)
        elif item in self._operations:
            self._operations.remove(item)
            item.set_child_of(None)
        else:
            log.warning('feature %s not found in feature list' % item)
            return 0
        self.request_update()
        #log.debug('Feature removed: %s' % item)
        return 1

    def on_groupable_iter(self):
        #log.debug('on_groupable_iter')
        for i in self._attributes:
            #log.debug('on_groupable_iter (attr): %s' % i)
            yield i
        for i in self._operations:
            #log.debug('on_groupable_iter (oper): %s' % i)
            yield i

initialize_item(ClassItem, UML.Class)
