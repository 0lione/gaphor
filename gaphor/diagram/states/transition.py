"""
State transition implementation.
"""

from gaphor import UML
from gaphor.diagram.diagramline import NamedLine
from gaphor.diagram.style import ALIGN_LEFT, ALIGN_RIGHT, ALIGN_TOP


class TransitionItem(NamedLine):
    """
    Representation of state transition.
    """

    __uml__ = UML.Transition

    __style__ = {
            'name-align': (ALIGN_RIGHT, ALIGN_TOP),
            'name-padding': (5, 15, 5, 5),
    }

    def __init__(self, id = None):
        NamedLine.__init__(self, id)
        self._guard = self.add_text('guard.specification.value', editable=True)


    def postload(self):
        if self.subject and self.subject.guard:
            self._guard.text = self.subject.guard.value
        super(FlowItem, self).postload()


    def draw_tail(self, context):
        cr = context.cairo
        cr.line_to(0, 0)
        cr.stroke()
        cr.move_to(15, -6)
        cr.line_to(0, 0)
        cr.line_to(15, 6)


# vim:sw=4:et:ai
