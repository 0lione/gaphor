from gaphor.core.modeling import Diagram
from gaphor import UML
from gaphor.UML.classes import ClassItem
from gaphor.diagram.styleeditor import StyleEditor
from gaphor.core.modeling import StyleSheet
from gaphor.diagram.tests.fixtures import find


def test_style_editor_creation(diagram):
    item = diagram.create(ClassItem)
    style_editor = StyleEditor(item, lambda : None)
    style_editor.present()
    assert style_editor
    color_picker = find(style_editor.window, "color")
    border_radius = find(style_editor.window, "border-radius")
    background_color = find(style_editor.window, "background-color")
    text_color = find(style_editor.window, "text-color")
    assert color_picker and border_radius and background_color and text_color


def test_set_border_radius(element_factory):
    diagram = element_factory.create(Diagram)
    item = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    style_sheet = StyleSheet(item)
    diagram.styleSheet = style_sheet
    style_editor = StyleEditor(item, lambda: None)
    style_editor.present()
    border_radius = find(style_editor.window, "border-radius")
    border_radius.set_value(10)

    assert diagram.styleSheet is not None
    assert style_editor.subject.presentation_style.get_style("border-radius") is not None
