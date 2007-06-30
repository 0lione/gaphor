"""
Lifeline diagram item.
"""

import gaphas
from gaphas.geometry import distance_line_point, Rectangle

from gaphor import UML
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_MIDDLE

class LifetimeItem(gaphas.Item):
    MIN_WIDTH = 10
    def __init__(self):
        super(LifetimeItem, self).__init__()
        self._th = gaphas.Handle()
        self._bh = gaphas.Handle()
        self._handles.append(self._th)
        self._handles.append(self._bh)

        self._th.movable = False
        self._th.visible = False


    def is_visible(self):
        return self._bh.y - self._th.y > self.MIN_WIDTH


    def set_pos(self, x, y):
        self._th.x = x
        self._bh.x = x
        self._th.y = y


    def update(self, context):
        super(LifetimeItem, self).update(context)
        th = self._th
        bh = self._bh
        dy = max(self.MIN_WIDTH, bh.y - th.y)
        bh.y = th.y + dy


    def draw(self, context):
        cr = context.cairo
        if context.hovered or context.focused or self.is_visible():
            cr.save()
            th = self._th
            bh = self._bh
            cr.move_to(th.x, th.y)
            cr.line_to(bh.x, bh.y)
            cr.restore()




# Lifeline semantics:
#  lifeline_name[: class_name]
#  lifeline_name: str
#  class_name: name of referenced ConnectableElement
class LifelineItem(NamedItem):
    __uml__      = UML.Lifeline
    __style__ = {
        'name-align': (ALIGN_CENTER, ALIGN_MIDDLE),
    }

    def __init__(self, id = None):
        NamedItem.__init__(self, id)

        lt = self._lifetime = LifetimeItem()
        self._handles.extend(self._lifetime.handles())

        x, y = self.style.min_size
        lt.set_pos(x / 2.0, y)


    def pre_update(self, context):
        super(LifelineItem, self).pre_update(context)
        self._lifetime.pre_update(context)


    def update(self, context):
        super(LifelineItem, self).update(context)
        self._lifetime.set_pos(self.width / 2.0, self.height)
        self._lifetime.update(context)


    def draw(self, context):
        super(LifelineItem, self).draw(context)
        self._lifetime.draw(context)

        cr = context.cairo
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()


    def point(self, x, y):
        d1 = super(LifelineItem, self).point(x, y)
        lt = self._lifetime
        h1, h2 = lt.handles()
        d2 = distance_line_point(h1.pos, h2.pos, (x, y))[0]
        return min(d1, d2)


# vim:sw=4:et
