from __future__ import annotations

import importlib.resources
import textwrap

# from gaphor.diagram.presentation import PresentationStyle
# from gaphor.transaction import Transaction
# from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling.element import Element
from gaphor.core.modeling.event import AttributeUpdated
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import CompiledStyleSheet

SYSTEM_STYLE_SHEET = (importlib.resources.files("gaphor") / "diagram.css").read_text(
    "utf-8"
)

DEFAULT_STYLE_SHEET = textwrap.dedent(
    """\
    diagram {
     /* line-style: sloppy 0.3; */
    }
    """
)


class StyleSheet(Element):
    _compiled_style_sheet: CompiledStyleSheet

    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        self._style_elems = {}
        self._system_font_family = "sans"
        self.compile_style_sheet()

    colorPickerResult: attribute[str] = attribute("colorPickerResult", str, "")
    styleSheet: attribute[str] = attribute("styleSheet", str, DEFAULT_STYLE_SHEET)
    naturalLanguage: attribute[str] = attribute("naturalLanguage", str)

    @property
    def style_elems(self) -> dict:
        return self._style_elems

    @property
    def system_font_family(self) -> str:
        return self._system_font_family

    @system_font_family.setter
    def system_font_family(self, font_family: str):
        self._system_font_family = font_family
        self.compile_style_sheet()

    @style_elems.setter
    def style_elems(self, newset: set):
        self._style_elems = newset
        self.compile_style_sheet()

    def compile_style_sheet(self) -> None:
        self._compiled_style_sheet = CompiledStyleSheet(
            SYSTEM_STYLE_SHEET,
            f"diagram {{ font-family: {self._system_font_family} }}",
            self.colorPickerResult + self.styleSheet,
        )

    def new_compiled_style_sheet(self) -> CompiledStyleSheet:
        return self._compiled_style_sheet.copy()

    def postload(self):
        self.recover_style_elems()
        super().postload()
        self.compile_style_sheet()

    def handle(self, event):
        # Ensure compiled style sheet is always up-to-date:
        if (
            isinstance(event, AttributeUpdated)
            and event.property is StyleSheet.styleSheet
        ):
            self.compile_style_sheet()

        super().handle(event)

    def recover_style_elems(self):
        # for line in self.colorPickerResult.split("\n"):
        #     parts = line.split("{")
        #     if len(parts) == 2:
        #         key = parts[0].strip()
        #         value = parts[1].strip().rstrip("}").rstrip(";")
        #         self.style_elems[key] = value
        self.styleSheet += self.colorPickerResult
        self.colorPickerResult = ""

    def update_style_elems(self):
        temp = ""
        for k, v in self.style_elems.items():
            temp += f"{k} {{{v};}}\n"
        return temp

    def new_style_elem(self, elem: PresentationStyle):
        self.style_elems[elem.key()] = str(elem)
        self.colorPickerResult = self.update_style_elems()
        self.compile_style_sheet()

    def delete_style_elem(self, elem: str):
        if self.style_elems.get(elem) is not None:
            self.style_elems.pop(elem)
            self.colorPickerResult = self.update_style_elems()
            self.compile_style_sheet()
            return True
        return False
    
    def translate_to_stylesheet(self, elem: str):
        if self.style_elems.get(elem) is not None:
            self.styleSheet += self.style_elems.get(elem)
            self.delete_style_elem(elem)
