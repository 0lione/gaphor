"""
Control flow and object flow implementation.

Contains also implementation to split flows using activity edge connectors.
"""

from math import atan, atan2, pi, sin, cos

from gaphor import UML
from gaphor.UML.modelfactory import stereotype_name
from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.diagramline import NamedLine
from gaphor.diagram.text import TextAlign, VerticalAlign
from gaphor.diagram.support import represents
from gaphor.diagram.shapes import Box, Text, EditableText, draw_arrow_tail


@represents(UML.ControlFlow)
class FlowItem(LinePresentation):
    """
    Representation of control flow and object flow. Flow item has name and
    guard. It can be splitted into two flows with activity edge connectors.
    """

    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        def stereotype_text():
            s = (
                self.subject
                and ", ".join(
                    map(
                        stereotype_name, self.subject.appliedStereotype[:].classifier[:]
                    )
                )
                or ""
            )
            return s and f"«{s}»" or ""

        self.shape_tail = Box(
            Text(text=stereotype_text, style={"min-width": 0, "min-height": 0}),
            EditableText(text=lambda: self.subject and self.subject.name or ""),
        )

        self.watch("subject<NamedElement>.name")
        self.watch("subject.appliedStereotype.classifier.name")

        self.guard = EditableText(
            text=lambda: self.subject and self.subject.guard or ""
        )
        self.shape_middle = self.guard

        self.watch("subject<ControlFlow>.guard")
        self.watch("subject<ObjectFlow>.guard")

        self.draw_tail = draw_arrow_tail
