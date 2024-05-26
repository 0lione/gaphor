from gi.repository import Gdk, Gtk

from gaphor.core.modeling import Diagram
from gaphor import UML
from gaphor.UML.classes import ClassItem
from gaphor.diagram.styleeditor import StyleEditor
from gaphor.core.modeling import StyleSheet
from gaphor.diagram.tests.fixtures import find
from gaphor.core import transactional

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
    assert item.presentation_style.get_style("border-radius") == "10.0"

def test_set_color(diagram):
    item = diagram.create(ClassItem)
    item.presentation_style.styleSheet = StyleSheet()
    style_editor = StyleEditor(item, lambda : None)
    style_editor.present()
    color_picker = find(style_editor.window, "color")
    rgba = Gdk.RGBA()
    rgba.parse("rgba(255, 0, 0, 1)")
    color_picker.set_rgba(rgba)
    style_editor.on_color_set(color_picker)
    assert item.presentation_style.get_style("color") == "rgba(255, 0, 0, 1.0)"

def test_set_background_color(diagram):
    item = diagram.create(ClassItem)
    item.presentation_style.styleSheet = StyleSheet()
    style_editor = StyleEditor(item, lambda : None)
    style_editor.present()
    background_color = find(style_editor.window, "background-color")
    rgba = Gdk.RGBA()
    rgba.parse("rgba(0, 255, 0, 1)")
    background_color.set_rgba(rgba)
    style_editor.on_background_color_set(background_color)
    assert item.presentation_style.get_style("background-color") == "rgba(0, 255, 0, 1.0)"

def test_set_text_color(diagram):
    item = diagram.create(ClassItem)
    item.presentation_style.styleSheet = StyleSheet()
    style_editor = StyleEditor(item, lambda : None)
    style_editor.present()
    text_color = find(style_editor.window, "text-color")
    rgba = Gdk.RGBA()
    rgba.parse("rgba(0, 0, 255, 1)")
    text_color.set_rgba(rgba)
    style_editor.on_text_color_set(text_color)
    assert item.presentation_style.get_style("text-color") == "rgba(0, 0, 255, 1.0)"