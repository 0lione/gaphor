"""
DEPRECATED

DiagramItem provides basic functionality for presentations.
Such as a modifier 'subject' property and a unique id.
"""

import ast
import logging

from gaphas.state import observed, reversible_property

from gaphor import UML
from gaphor.diagram.textelement import EditableTextSupport
from gaphor.diagram.style import Style, ALIGN_CENTER, ALIGN_TOP
from gaphor.diagram.support import set_diagram_item


logger = logging.getLogger(__name__)


class DiagramItemMeta(type):
    """
    Initialize a new diagram item.
    2. Set items style information.

    @ivar style: style information
    """

    def __init__(self, name, bases, data):
        type.__init__(self, name, bases, data)

        self.set_style(data)

    def set_style(self, data):
        """
        Set item style information by merging provided information with
        style information from base classes.

        @param cls:   new instance of diagram item class
        @param bases: base classes of an item
        @param data:  metaclass data with style information
        """
        style = Style()
        for c in self.__bases__:
            if hasattr(c, "style"):
                for (name, value) in list(c.style.items()):
                    style.add(name, value)

        if "__style__" in data:
            for (name, value) in data["__style__"].items():
                style.add(name, value)

        self.style = style


class StereotypeSupport:
    """
    Support for stereotypes for every diagram item.
    """

    STEREOTYPE_ALIGN = {
        "text-align": (ALIGN_CENTER, ALIGN_TOP),
        "text-padding": (5, 10, 2, 10),
        "text-outside": False,
        "text-align-group": "stereotype",
        "line-width": 2,
    }

    def __init__(self):
        super().__init__()
        self._stereotype = self.add_text(
            "stereotype",
            style=self.STEREOTYPE_ALIGN,
            visible=lambda: self._stereotype.text,
        )
        self._show_stereotypes_attrs = False

    @observed
    def _set_show_stereotypes_attrs(self, value):
        self._show_stereotypes_attrs = value
        self.update_stereotypes_attrs()

    show_stereotypes_attrs = reversible_property(
        fget=lambda s: s._show_stereotypes_attrs,
        fset=_set_show_stereotypes_attrs,
        doc="""
            Diagram item should show stereotypes attributes when property
            is set to True.

            When changed, method `update_stereotypes_attrs` is called.
            """,
    )

    def update_stereotypes_attrs(self):
        """
        Update display of stereotypes attributes.

        The method does nothing at the moment. In the future it should
        probably display stereotypes attributes under stereotypes header.

        Abstract class for classifiers overrides this method to display
        stereotypes attributes in compartments.
        """
        pass

    def set_stereotype(self, text=None):
        """
        Set the stereotype text for the diagram item.

        Note, that text is not Stereotype object.

        @arg text: stereotype text
        """
        self._stereotype.text = text
        self.request_update()

    stereotype = property(lambda s: s._stereotype, set_stereotype)

    def update_stereotype(self):
        """
        Update the stereotype definitions (text) of this item.

        Note, that this method is also called from
        ExtensionItem.confirm_connect_handle method.
        """
        # by default no stereotype, however check for __stereotype__
        # attribute to assign some static stereotype see interfaces,
        # use case relationships, package or class for examples
        stereotype = getattr(self, "__stereotype__", ())
        if stereotype:
            stereotype = self.parse_stereotype(stereotype)

        # Phew! :] :P
        stereotype = UML.model.stereotypes_str(self.subject, stereotype)
        self.set_stereotype(stereotype)

    def parse_stereotype(self, data):
        if isinstance(data, str):  # return data as stereotype if it is a string
            return (data,)

        subject = self.subject

        for stereotype, condition in list(data.items()):
            if isinstance(condition, tuple):
                cls, predicate = condition
            elif isinstance(condition, type):
                cls = condition
                predicate = None
            elif callable(condition):
                cls = None
                predicate = condition
            else:
                assert False, "wrong conditional %s" % condition

            ok = True
            if cls:
                ok = isinstance(subject, cls)  # isinstance(subject, cls)
            if predicate:
                ok = predicate(self)

            if ok:
                return (stereotype,)
        return ()


class DiagramItem(
    UML.Presentation, StereotypeSupport, EditableTextSupport, metaclass=DiagramItemMeta
):
    """
    Basic functionality for all model elements (lines and elements!).

    This class contains common functionality for model elements and
    relationships.
    It provides an interface similar to UML.Element for connecting and
    disconnecting signals.

    This class is not very useful on its own. It contains some glue-code for
    diacanvas.DiaCanvasItem and gaphor.UML.Element.

    Example:
        class ElementItem(diacanvas.CanvasElement, DiagramItem):
            connect = DiagramItem.connect
            disconnect = DiagramItem.disconnect
            ...

    @cvar style: styles information (derived from DiagramItemMeta)
    """

    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self.watch(
            "subject.appliedStereotype.classifier.name",
            self.on_element_applied_stereotype,
        )

    # TODO: Use adapters for load/save functionality
    def save(self, save_func):
        if self.subject:
            save_func("subject", self.subject)

        save_func("show_stereotypes_attrs", self.show_stereotypes_attrs)

    def load(self, name, value):
        if name == "subject":
            type(self).subject.load(self, value)
        elif name == "show_stereotypes_attrs":
            self._show_stereotypes_attrs = ast.literal_eval(value)
        else:
            try:
                setattr(self, name.replace("-", "_"), ast.literal_eval(value))
            except:
                logger.warning(
                    "%s has no property named %s (value %s)" % (self, name, value)
                )

    def postload(self):
        if self.subject:
            self.update_stereotype()
            self.update_stereotypes_attrs()

    def save_property(self, save_func, name):
        """
        Save a property, this is a shorthand method.
        """
        save_func(name, getattr(self, name.replace("-", "_")))

    def pre_update(self, context):
        EditableTextSupport.pre_update(self, context)

    def post_update(self, context):
        EditableTextSupport.post_update(self, context)

    def draw(self, context):
        EditableTextSupport.draw(self, context)

    def item_at(self, x, y):
        return self

    def on_element_applied_stereotype(self, event):
        if self.subject:
            self.update_stereotype()
            self.request_update()
