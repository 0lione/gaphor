
# vim:sw=4:et
import gobject
import diacanvas
import gaphor.UML as UML

class PlacementTool(diacanvas.PlacementTool):

    def __init__(self, item_factory, action_id, **properties):
        """item_factory is a callable. It is used to create a CanvasItem
        that is displayed on the diagram.
        """
        diacanvas.PlacementTool.__init__(self, None, **properties)
        self.item_factory = item_factory
        self.action_id = action_id
        self.is_released = False

    def _create_item(self, view, event):
        if event.button == 3:
            return None

        item = None

        try:
            item = self.item_factory()
        except Exception, e:
            log.error('Error while creating item: %s' % e, e)
        else:
            if self.properties and len(self.properties) > 0:
                try:
                    for (k, v) in self.properties.items():
                        item.set_property(k, v)
                except TypeError, e:
                    log.error('PlacementTool: could not set property %s' % k, e)
                
        return item

    def _grab_handle(self, view, event, item):
        if not self.is_released:
            if isinstance(item, diacanvas.CanvasElement):
                #print 'PlacementTool: setting handle of Element'
                handle = item.handles[diacanvas.HANDLE_SE]
                if not handle.get_property('movable'):
                    view_item = view.find_view_item(item)
                    view.focus(view_item)
                    return
            diacanvas.PlacementTool._grab_handle(self, view, event, item)

    def do_button_press_event(self, view, event):
        view.unselect_all()
        #print 'Gaphor: on_button_press_event: %s' % self.__dict__
        return diacanvas.PlacementTool.do_button_press_event(self, view, event)

    def do_button_release_event(self, view, event):
        self.is_released = True
        view.set_tool(None)
        #print 'Gaphor: do_button_release_event: %s' % self.__dict__
        return diacanvas.PlacementTool.do_button_release_event(self, view, event)

gobject.type_register(PlacementTool)

