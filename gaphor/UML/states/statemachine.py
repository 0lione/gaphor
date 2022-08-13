from gaphor import UML
from gaphor.core import gettext
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import FontWeight, VerticalAlign
from gaphor.diagram.presentation import Classified, ElementPresentation
from gaphor.diagram.shapes import Box, Text, draw_border, draw_top_separator
from gaphor.diagram.support import represents
from gaphor.UML.classes.stereotype import stereotype_compartments, stereotype_watches


@represents(UML.StateMachine)
class StateMachineItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("show_stereotypes", self.update_shapes)
        self.watch("subject[NamedElement].name")
        self.watch("children", self.update_shapes)
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)
    show_regions: attribute[int] = attribute("show_regions", int, default=True)

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                Text(
                    text=lambda: UML.recipes.stereotypes_str(
                        self.subject, [gettext("statemachine")]
                    ),
                ),
                Text(
                    text=lambda: self.subject.name or "",
                    style={"font-weight": FontWeight.BOLD},
                ),
                style={"padding": (4, 4, 4, 4)},
            ),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            *(self.show_regions and region_compartment(self.subject) or []),
            style={
                "vertical-align": VerticalAlign.TOP
                if (self.diagram and self.children) or self.show_regions
                else VerticalAlign.MIDDLE,
            },
            draw=draw_border
        )


def region_compartment(subject):
    if not subject:
        return

    for index, region in enumerate(subject.region):
        yield Box(
            style={"min-height": 100, "dash-style": (7, 3)},
            draw=draw_top_separator if index > 0 else None,
        )
