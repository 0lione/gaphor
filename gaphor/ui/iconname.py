"""
With `get_icon_name` you can retrieve an icon name
for a UML model element.
"""

from gaphor import UML
import re
from functools import singledispatch


TO_KEBAB = re.compile(r"([a-z])([A-Z]+)")


def to_kebab_case(s):
    return TO_KEBAB.sub("\\1-\\2", s).lower()


@singledispatch
def get_icon_name(element):
    """
    Get an icon name for a UML model element.
    """
    return "gaphor-" + to_kebab_case(element.__class__.__name__)


@get_icon_name.register(UML.Class)
def get_name_for_class(element):
    if element.extension:
        return "gaphor-metaclass"
    else:
        return "gaphor-class"


@get_icon_name.register(UML.Component)
def get_name_for_component(element):
    for p in element.presentation:
        try:
            if p.__stereotype__ == "subsystem":
                return "gaphor-subsystem"
        except AttributeError:
            return "gaphor-component"


@get_icon_name.register(UML.Property)
def get_name_for_property(element):
    if element.association:
        return "gaphor-association-end"
    else:
        return "gaphor-property"
