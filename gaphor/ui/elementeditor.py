"""The element editor is a utility window used for editing elements."""

import importlib.resources
import logging
import textwrap
from typing import Optional

from gi.repository import GLib, Gtk

from gaphor.abc import ActionProvider
from gaphor.core import Transaction, action, event_handler, gettext
from gaphor.core.modeling import Presentation, StyleSheet
from gaphor.core.modeling.event import AssociationUpdated, AttributeUpdated, ModelReady
from gaphor.diagram.propertypages import PropertyPages
from gaphor.ui.abc import UIComponent
from gaphor.ui.event import DiagramSelectionChanged

log = logging.getLogger(__name__)


def new_builder(*object_ids):
    builder = Gtk.Builder()
    builder.set_translation_domain("gaphor")
    with importlib.resources.path("gaphor.ui", "elementeditor.glade") as glade_file:
        builder.add_objects_from_file(str(glade_file), object_ids)
    return builder


class ElementEditor(UIComponent, ActionProvider):
    """The ElementEditor class is a utility window used to edit UML elements.
    It will display the properties of the currently selected element in the
    diagram."""

    title = gettext("Element Editor")
    size = (275, -1)

    def __init__(self, event_manager, element_factory, diagrams, properties):
        """Constructor. Build the action group for the element editor window.
        This will place a button for opening the window in the toolbar.
        The widget attribute is a PropertyEditor."""
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.diagrams = diagrams
        self.properties = properties
        self.vbox: Optional[Gtk.Box] = None
        self._current_item = None
        self._expanded_pages = {gettext("Properties"): True}
        self._on_style_sheet_changed_id = -1
        self._style_sheet_timeout_id = 0

    def open(self):
        """Display the ElementEditor pane."""
        builder = new_builder("elementeditor", "style-sheet-buffer")

        self.revealer = builder.get_object("elementeditor")
        self.editor_stack = builder.get_object("editor-stack")
        self.vbox = builder.get_object("editors")

        current_view = self.diagrams.get_current_view()
        self._selection_change(focused_item=current_view and current_view.focused_item)

        self.event_manager.subscribe(self._selection_change)
        self.event_manager.subscribe(self._element_changed)

        self.enable_style_sheet = builder.get_object("enable-style-sheet")
        self.style_sheet_buffer = builder.get_object("style-sheet-buffer")

        self.event_manager.subscribe(self._model_ready)
        self._on_style_sheet_changed_id = self.style_sheet_buffer.connect(
            "changed", self.on_style_sheet_changed
        )

        return self.revealer

    def close(self, widget=None):
        """Hide the element editor window and deactivate the toolbar button.
        Both the widget and event parameters default to None and are
        idempotent if set."""

        self.event_manager.unsubscribe(self._selection_change)
        self.event_manager.unsubscribe(self._element_changed)
        self.event_manager.unsubscribe(self._model_ready)
        self.vbox = None
        self._current_item = None
        return True

    @action(name="show-editors", shortcut="<Primary>e", state=True)
    def toggle_editor_visibility(self, active):
        self.revealer.set_reveal_child(active)

    ## Diagram item editor

    def _get_adapters(self, item):
        """
        Return an ordered list of (order, name, adapter).
        """
        adaptermap = {}
        if isinstance(item, Presentation) and item.subject:
            for adapter in PropertyPages(item.subject):
                adaptermap[(adapter.order, adapter.__class__.__name__)] = adapter
        for adapter in PropertyPages(item):
            adaptermap[(adapter.order, adapter.__class__.__name__)] = adapter

        return sorted(adaptermap.items())

    def create_pages(self, item):
        """
        Load all tabs that can operate on the given item.
        """
        assert self.vbox
        adapters = self._get_adapters(item)

        for (_, name), adapter in adapters:
            try:
                page = adapter.construct()
                if not page:
                    continue
                elif isinstance(page, Gtk.Expander):
                    page.set_expanded(self._expanded_pages.get(name, True))
                    page.connect_after("activate", self.on_expand, name)
                self.vbox.pack_start(page, False, True, 0)
            except Exception:
                log.error(
                    "Could not construct property page for " + name, exc_info=True
                )

    def clear_pages(self):
        """
        Remove all tabs from the notebook.
        """
        assert self.vbox
        for page in self.vbox.get_children():
            page.destroy()

    def on_expand(self, widget, name):
        self._expanded_pages[name] = widget.get_expanded()

    @event_handler(DiagramSelectionChanged)
    def _selection_change(self, event=None, focused_item=None):
        """
        Called when a diagram item receives focus.

        This reloads all tabs based on the current selection.
        """
        assert self.vbox
        item = event and event.focused_item or focused_item
        if item is self._current_item and self.vbox.get_children():
            return

        self._current_item = item
        self.clear_pages()

        if item:
            self.create_pages(item)
        else:
            builder = new_builder("no-item-selected")

            self.vbox.pack_start(
                child=builder.get_object("no-item-selected"),
                expand=False,
                fill=True,
                padding=0,
            )

            tips = builder.get_object("tips")

            def on_show_tips_changed(checkbox):
                active = checkbox.get_active()
                tips.show() if active else tips.hide()
                self.properties.set("show-tips", active)

            show_tips = builder.get_object("show-tips")
            show_tips.connect("toggled", on_show_tips_changed)
            show_tips.set_active(self.properties.get("show-tips", True))

    @event_handler(AssociationUpdated)
    def _element_changed(self, event: AssociationUpdated):
        if event.property is Presentation.subject:  # type: ignore[misc] # noqa: F821
            element = event.element
            if element is self._current_item:
                self.clear_pages()
                self.create_pages(self._current_item)

    ## Settings stack

    @action(name="show-settings", state=False)
    def toggle_editor_settings(self, active):
        self.editor_stack.set_visible_child_name("settings" if active else "editors")

    @action(name="enable-style-sheet", state=False)
    def toggle_enable_style_sheet(self, active):
        style_sheets = self.element_factory.lselect(StyleSheet)
        if active and not style_sheets:
            style_sheet = self.element_factory.create(StyleSheet)
            style_sheet.style_sheet = "* { }"
        elif not active and style_sheets:
            for style_sheet in style_sheets:
                # Trigger style update on diagrams:
                style_sheet.styleSheet = ""
                style_sheet.unlink()

    def on_style_sheet_changed(self, buffer):
        style_sheets = self.element_factory.lselect(StyleSheet)
        if style_sheets:
            text = buffer.get_text(
                buffer.get_start_iter(), buffer.get_end_iter(), False
            )
            style_sheet = style_sheets[0]

            if self._style_sheet_timeout_id:
                GLib.source_remove(self._style_sheet_timeout_id)

            def tx_update_style_sheet(style_sheet, text):
                with Transaction(self.event_manager):
                    style_sheet.styleSheet = text
                self._style_sheet_timeout_id = 0

            self._style_sheet_timeout_id = GLib.timeout_add(
                800, tx_update_style_sheet, style_sheet, text
            )

    @event_handler(ModelReady)
    def _model_ready(self, event):
        style_sheets = self.element_factory.lselect(StyleSheet)

        self.enable_style_sheet.set_active(bool(style_sheets))

        self.style_sheet_buffer.handler_block(self._on_style_sheet_changed_id)
        self.style_sheet_buffer.set_text(
            style_sheets[0].styleSheet if style_sheets else ""
        )
        self.style_sheet_buffer.handler_unblock(self._on_style_sheet_changed_id)
