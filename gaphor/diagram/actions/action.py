"""
Action diagram item.
"""

from gaphor import UML
from gaphor.UML.presentation import ElementPresentation
from gaphor.diagram.text import TextBox
from gaphor.diagram.support import represents
from gaphor.diagram.shapes import Box


@represents(UML.Action)
class ActionItem(ElementPresentation):
    def __init__(self, id=None, model=None):
        """
        Create action item.
        """
        super().__init__(id, model)

        name = TextBox(text=lambda: self.subject and self.subject.name or "")
        self.watch("subject<NamedElement>.name")

        self.layout = Box(
            name,
            style={
                "min-width": 50,
                "min-height": 30,
                "padding": (5, 10, 5, 10),
                "border-radius": 15,
                "border": True,
            },
        )


@represents(UML.SendSignalAction)
class SendSignalActionItem(ElementPresentation):
    def __init__(self, id=None, model=None):
        """
        Create action item.
        """
        super().__init__(id, model)

        name = TextBox()

        watch_name(self, name)

        self.layout = Box(
            name,
            style={"min-width": 50, "min-height": 30, "padding": (5, 25, 5, 10)},
            draw=self.draw_border,
        )

    def draw_border(self, box, context, bounding_box):
        cr = context.cairo
        d = 15
        x, y, width, height = bounding_box
        cr.move_to(0, 0)
        cr.line_to(width - d, 0)
        cr.line_to(width, height / 2)
        cr.line_to(width - d, height)
        cr.line_to(0, height)
        cr.close_path()

        cr.stroke()


@represents(UML.AcceptEventAction)
class AcceptEventActionItem(ElementPresentation):
    def __init__(self, id=None, model=None):
        """
        Create action item.
        """
        super().__init__(id, model)

        name = TextBox(style={})

        watch_name(self, name),

        self.layout = Box(
            name,
            style={"min-width": 50, "min-height": 30, "padding": (5, 10, 5, 25)},
            draw=self.draw_border,
        )

    def draw_border(self, box, context, bounding_box):
        cr = context.cairo
        d = 15
        x, y, width, height = bounding_box
        cr.move_to(0, 0)
        cr.line_to(width, 0)
        cr.line_to(width, height)
        cr.line_to(0, height)
        cr.line_to(d, height / 2)
        cr.close_path()

        cr.stroke()
