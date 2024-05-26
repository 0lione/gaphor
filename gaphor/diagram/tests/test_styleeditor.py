from gi.repository import Gdk

from gaphor.core.modeling import Diagram
from gaphor import UML
from gaphor.UML.classes import ClassItem
from gaphor.diagram.styleeditor import StyleEditor
from gaphor.core.modeling import StyleSheet
from gaphor.diagram.tests.fixtures import find

import sys

def test_style_editor_creation(diagram):
    item = diagram.create(ClassItem)
    item.presentation_style.styleSheet = StyleSheet()
    style_editor = StyleEditor(item, lambda : None)
    style_editor.present()
    assert style_editor
    color_picker = find(style_editor.window, "color")
    border_radius = find(style_editor.window, "border-radius")
    background_color = find(style_editor.window, "background-color")
    text_color = find(style_editor.window, "text-color")
    assert color_picker and border_radius and background_color and text_color

def test_set_border_radius(diagram):
    item = diagram.create(ClassItem)
    item.presentation_style.styleSheet = StyleSheet()
    style_editor = StyleEditor(item, lambda : None)
    style_editor.present()
    border_radius = find(style_editor.window, "border-radius")
    border_radius.set_value(10)
    print(f"hello: {item.presentation_style.get_style('border-radius')}")
    assert item.presentation_style.get_style("border-radius") == "10.0"

""""
def test_set_color(diagram):
    item = diagram.create(ClassItem)
    item.presentation_style.styleSheet = StyleSheet()
    style_editor = StyleEditor(item, lambda : None)
    style_editor.present()
    color_picker = find(style_editor.window, "color")
    color_picker.set_rgba(Gdk.RGBA(red=0, green=1, blue=0, alpha=1))
    assert item.presentation_style.get_style("color") == "rgba(0, 255, 0, 1)"
"""