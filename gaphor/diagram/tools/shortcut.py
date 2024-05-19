from gaphas.view import GtkView
from gi.repository import Gdk, Gtk

from gaphor.UML.classes.klass import ClassItem
from gaphor.UML.uml import Class
from gaphor.core import Transaction
from gaphor.core.modeling import Presentation, self_and_owners
from gaphor.core.modeling.diagram import StyledItem


def shortcut_tool(event_manager):
    ctrl = Gtk.EventControllerKey.new()
    ctrl.connect("key-pressed", key_pressed, event_manager)
    return ctrl


def key_pressed(ctrl, keyval, keycode, state, event_manager):
    """Handle the 'Delete' key.

    This can not be handled directly (through GTK's accelerators),
    otherwise this key will confuse the text edit stuff.
    """
    view: GtkView = ctrl.get_widget()
    if keyval in (Gdk.KEY_Delete, Gdk.KEY_BackSpace):
        delete_selected_items(view, event_manager)
        return True
    if keyval == Gdk.KEY_comma:
        test(view, event_manager)
    return False


def test(view: GtkView, event_manager):
    diagram: Diagram = list(view.selection.selected_items)[0].diagram
    item: ClassItem = list(view.selection.selected_items)[0]
    try:
        with Transaction(event_manager):
            item.presentation_style.change_style("color", "red")
    except:
        pass


def delete_selected_items(view: GtkView, event_manager):
    with Transaction(event_manager):
        items = view.selection.selected_items
        for i in list(items):
            assert isinstance(i, Presentation)
            if i.subject and i.subject in self_and_owners(i.diagram):
                del i.diagram.element
            i.unlink()
