"""
Activity partition item.
"""

from gaphor import UML
from gaphor.diagram.nameditem import NamedItem

class PartitionItem(NamedItem):
    __uml__ = UML.ActivityPartition

    __stereotype__ = {
        'external': lambda self: self.subject and self.subject.isExternal,
    }

    __style__   = {
        'min-size': (100, 400),
    }

    DELTA = 30

    def __init__(self, id=None):
        super(PartitionItem, self).__init__(id)
        self._superpart = False
        self._subpart = False
        self._hdmax = 0 # maximum subpartition header height


    def pre_update(self, context):
        super(PartitionItem, self).pre_update(context)
        
        if not self.subject:
            self._header_size = self._header_size[0], self.DELTA

        # get subpartitions
        children = list(k for k in self.canvas.get_children(self)
                if isinstance(k, PartitionItem))

        self._superpart = self.canvas.get_parent(self) is not None
        self._subpart = len(children) > 0

        handles = self.handles()
        for h in handles:
            h.movable = not (self._subpart or self._superpart)
        if self._superpart and not self._subpart:
            h = handles[2]
            h.movable = True


        if self._subpart:
            wsum = sum(sl.width for sl in children)
            hmax = max(sl.height for sl in children)
            self._hdmax = max(sl._header_size[1] for sl in children)

            self.width = wsum
            self.height = hmax + self._header_size[1] + self.DELTA

            dp = 0
            for sl in self.canvas.get_children(self):
                x, y = self.canvas.get_matrix_i2c(self).transform_point(dp, 0)
                x1, y1 = self.canvas.get_matrix_i2c(sl).transform_point(0, 0)

                # line up headers
                x = x - x1
                y = y - y1 + self._header_size[1] + self._hdmax - sl._header_size[1]
                sl.matrix.translate(x, y)

                sl.height = hmax
                dp += sl.width


    def draw(self, context):
        """
        By default horizontal partition is drawn. It is open on right side
        (or bottom side when horizontal).
        """
        super(PartitionItem, self).draw(context)
        cr = context.cairo
        cr.set_line_width(2.4)

        if self.subject and not self.subject.isDimension and not self._superpart:
            cr.move_to(0, 0)
            cr.line_to(self.width, 0)


        h = self._header_size[1]

        # draw outside lines if this item is toplevel partition
        if not self._superpart:
            cr.move_to(0, self.height)
            cr.line_to(0, h)
            cr.line_to(self.width, h)
            cr.line_to(self.width, self.height)

        if self._subpart:
            # header line for all subparitions
            hd = h + self._hdmax
            cr.move_to(0, hd)
            cr.line_to(self.width, hd)

        if self._subpart:
            # draw inside lines for all children but last one
            dp = 0
            for sl in self.canvas.get_children(self)[:-1]:
                dp += sl.width
                cr.move_to(dp, h)
                cr.line_to(dp, self.height)

        cr.stroke()

        if context.hovered or context.dropzone:
            cr.save()
            cr.set_dash((1.0, 5.0), 0)
            cr.set_line_width(1.0)
            cr.rectangle(0, 0, self.width, self.height)
            d = self.height - self.DELTA
            cr.move_to(0, d)
            cr.line_to(self.width, d)
            cr.stroke()
            cr.restore()


# vim:sw=4:et
