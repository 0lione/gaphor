import cairo

from gaphor.diagram.shapes import Box, Line
from gaphor.diagram.text import TextBox, FloatingText
from gaphas.canvas import Context


def cairo_mock_context(recorder):
    class MethodMock:
        def __init__(self, name):
            self.name = name

        # As far as I know, cairo methods are never called as keyword arguments
        def __call__(self, *args):
            recorder((self.name, args))

    class CairoContextMock(cairo.Context):
        def __init__(self, surface):
            self.events = []
            super().__init__()

        def __getattribute__(self, name):
            return MethodMock(name)

    return CairoContextMock(cairo.SVGSurface(None, 100, 100))


def test_box_size():
    box = Box()

    assert box.size(cr=None) == (0, 0)


def test_draw_empty_box():
    box = Box(draw=None)

    box.draw(context=None, bounding_box=None)


def test_draw_box_with_custom_draw_function():
    called = False

    def draw(box, context, bounding_box):
        nonlocal called
        called = True

    box = Box(draw=draw)

    box.draw(context=None, bounding_box=None)

    assert called


def test_draw_line():
    line = Line()
    events = []
    cr = cairo_mock_context(events.append)
    points = [(0, 0), (100, 100)]

    line.draw(context=Context(cairo=cr), points=points)


def test_draw_line_with_text():
    line = Line(FloatingText())
    events = []
    cr = cairo_mock_context(events.append)
    points = [(0, 0), (100, 100)]

    line.draw(context=Context(cairo=cr, hovered=1, selected=0), points=points)

    assert ("move_to", (0, 0)) in events

    # Endpoint is translated, then drawn, so arrows can draw
    # themselves relative to their own origin.
    assert ("translate", (100, 100)) in events
    assert ("line_to", (0, 0)) in events
