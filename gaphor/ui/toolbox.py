"""
Toolbox.
"""

import logging
from zope import component
from zope.interface import implementer

from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import Gtk

from gaphor.core import _, inject, toggle_action, build_action_group
from gaphor.interfaces import IActionProvider
from gaphor.ui.interfaces import IUIComponent, IDiagramPageChange
from gaphor.ui.diagramtoolbox import TOOLBOX_ACTIONS

log = logging.getLogger(__name__)

class _Toolbox(Gtk.ToolPalette):
    """
    A toolbox is a ToolPalette widget that contains a ToolItems (buttons) that
    are added to a ToolItemGroup. Each group has a label above the buttons.
    When the user clicks on the name the group's content toggles to show or
    hide the buttons.

    The toolbox is generated based on a definition with the form:
    ('name', ('boxAction1', 'boxAction2',...), 'name2', ('BoxActionN',...))

    """

    TARGET_STRING = 0
    TARGET_TOOLBOX_ACTION = 1
    DND_TARGETS = [
        Gtk.TargetEntry.new("STRING", Gtk.TargetFlags.SAME_APP, TARGET_STRING),
        Gtk.TargetEntry.new("text/plain", Gtk.TargetFlags.SAME_APP, TARGET_STRING),
        Gtk.TargetEntry.new(
            "gaphor/toolbox-action", Gtk.TargetFlags.SAME_APP, TARGET_TOOLBOX_ACTION
        ),
    ]

    __gsignals__ = {
        "toggled": (
            GObject.SignalFlags.RUN_FIRST,
            None,
            (GObject.TYPE_STRING, GObject.TYPE_INT),
        )
    }

    properties = inject("properties")

    def __init__(self, toolboxdef):
        """Create a new Toolbox instance.

        ToolItemGroups and ToolItems are created using the menu_factory and
        based on the toolboxdef definition.

        """
        GObject.GObject.__init__(self)
        self.buttons = []
        self.shortcuts = {}
        self._construct(toolboxdef)

    def toolbox_button(self, action_name, stock_id):
        button = Gtk.ToolButton.new_from_stock(stock_id)
        button.action_name = action_name
        button.set_use_drag_window(True)

        # Enable Drag and Drop
        button.drag_source_set(
            Gdk.ModifierType.BUTTON1_MASK,
            self.DND_TARGETS,
            Gdk.DragAction.COPY | Gdk.DragAction.LINK,
        )
        button.drag_source_set_icon_stock(stock_id)
        button.connect("drag-data-get", self._button_drag_data_get)

        return button

    def _construct(self, toolboxdef):
        shortcuts = self.shortcuts
        for title, items in toolboxdef:
            tool_item_group = Gtk.ToolItemGroup.new(title)
            for action_name, label, stock_id, shortcut in items:
                button = self.toolbox_button(action_name, stock_id)
                if label:
                    button.set_tooltip_text("%s (%s)" % (label, shortcut))
                self.buttons.append(button)
                tool_item_group.insert(button, -1)
                button.show()
                shortcuts[shortcut] = action_name
            self.add(tool_item_group)
            tool_item_group.show()

    def _button_drag_data_get(self, button, context, data, info, time):
        """The drag-data-get event signal handler.

        The drag-data-get signal is emitted on the drag source when the drop
        site requests the data which is dragged.

        Args:
            button (Gtk.Button): The button that received the signal.
            context (Gdk.DragContext): The drag context.
            data (Gtk.SelectionData): The data to be filled with the dragged
                data.
            info (int): The info that has been registered with the target in
                the Gtk.TargetList
            time (int): The timestamp at which the data was received.

        """
        data.set(type=data.get_target(), format=8, data=button.action_name.encode())


Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=0)


@implementer(IUIComponent, IActionProvider)
class Toolbox(object):

    title = _("Toolbox")
    placement = ("left", "diagrams")

    component_registry = inject("component_registry")
    main_window = inject("main_window")
    properties = inject("properties")

    menu_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu action="diagram">
            <separator/>
            <menuitem action="reset-tool-after-create" />
            <separator/>
          </menu>
        </menubar>
      </ui>
    """

    def __init__(self, toolbox_actions=TOOLBOX_ACTIONS):
        self._toolbox = None
        self._toolbox_actions = toolbox_actions
        self.action_group = build_action_group(self)
        self.action_group.get_action("reset-tool-after-create").set_active(
            self.properties.get("reset-tool-after-create", True)
        )

    def open(self):
        widget = self.construct()
        self.main_window.window.connect_after(
            "key-press-event", self._on_key_press_event
        )
        return widget

    def close(self):
        if self._toolbox:
            self._toolbox.destroy()
            self._toolbox = None

    def construct(self):
        toolbox = _Toolbox(self._toolbox_actions)
        toolbox.show()

        toolbox.connect("destroy", self._on_toolbox_destroyed)
        self._toolbox = toolbox
        return toolbox

    def _on_key_press_event(self, view, event):
        """
        Grab top level window events and select the appropriate tool based on the event.
        """
        if event.get_state() & Gdk.ModifierType.SHIFT_MASK or (
            event.get_state() == 0 or event.get_state() & Gdk.ModifierType.MOD2_MASK
        ):
            keyval = Gdk.keyval_name(event.keyval)
            self.set_active_tool(shortcut=keyval)

    def _on_toolbox_destroyed(self, widget):
        self._toolbox = None

    @toggle_action(name="reset-tool-after-create", label=_("_Reset tool"), active=False)
    def reset_tool_after_create(self, active):
        self.properties.set("reset-tool-after-create", active)

    @component.adapter(IDiagramPageChange)
    def _on_diagram_page_change(self, event):
        self.update_toolbox(event.diagram_page.toolbox.action_group)

    def update_toolbox(self, action_group):
        """
        Update the buttons in the toolbox. Each button should be connected
        by an action. Each button is assigned a special _action_name_
        attribute that can be used to fetch the action from the ui manager.
        """
        if not self._toolbox:
            return

        for button in self._toolbox.buttons:

            action_name = button.action_name
            action = action_group.get_action(action_name)
            if action:
                button.set_related_action(action)

    def set_active_tool(self, action_name=None, shortcut=None):
        """
        Set the tool based on the name of the action
        """
        # HACK:
        toolbox = self._toolbox
        if shortcut and toolbox:
            action_name = toolbox.shortcuts.get(shortcut)
            log.debug("Action for shortcut %s: %s" % (shortcut, action_name))
            if not action_name:
                return
