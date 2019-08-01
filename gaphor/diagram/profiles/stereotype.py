"""
Support code for dealing with stereotypes in diagrams.
"""

from gaphor import UML
from gaphor.diagram.shapes import Box, Text, draw_top_separator
from gaphor.diagram.text import TextAlign, VerticalAlign


def stereotype_compartments(subject):
    return filter(
        None,
        (
            _create_stereotype_compartment(appliedStereotype)
            for appliedStereotype in subject.appliedStereotype
        )
        if subject
        else [],
    )


def _create_stereotype_compartment(appliedStereotype):
    slots = [slot for slot in appliedStereotype.slot if slot.value]

    if slots:
        return Box(
            Text(
                text=lambda: f"«{UML.model.stereotype_name(appliedStereotype.classifier[0])}»",
                style={"padding": (0, 0, 4, 0)},
            ),
            *(
                Text(
                    text=lambda: UML.format(slot), style={"text-align": TextAlign.LEFT}
                )
                for slot in slots
            ),
            style={"padding": (4, 4, 4, 4), "vertical-align": VerticalAlign.TOP},
            draw=draw_top_separator,
        )
    else:
        return None
