#!/usr/bin/env python
# vim: sw=4

import types, gtk, UML, diacanvas, diagram

[
    FILE_LOAD,
    FILE_SAVE,
    FILE_DUMP,
    FILE_QUIT,
    EDIT_UNDO,
    EDIT_REDO,
    EDIT_DEL_FOCUSED,
    VIEW_ZOOM_IN,
    VIEW_ZOOM_OUT,
    VIEW_ZOOM_100,
    VIEW_SNAP_TO_GRID,
    ITEM_ADD_ACTOR,
    ITEM_ADD_USECASE,
    ITEM_ADD_COMMENT,
    ITEM_ADD_COMMENT_LINE,
    ITEM_ADD_GENERALIZATION,
    ITEM_ADD_DEPENDENCY,
    ITEM_ADD_REALIZATION,
    ITEM_ADD_INCLUDE,
    ITEM_ADD_EXTEND
] = range(20)

class DiagramView:

    def __init__(self, dia):
	win = gtk.Window()
	if dia.name == '':
	    win.set_title ('Unknown')
	else:
	    win.set_title (dia.name)

	win.set_default_size (300, 300)
	
	view = diacanvas.CanvasView (canvas=dia.canvas)

	vbox = gtk.VBox(homogeneous=gtk.FALSE)
	win.add (vbox)
	vbox.show()
	
	accelgroup = gtk.AccelGroup()
	win.add_accel_group(accelgroup)

	item_factory = gtk.ItemFactory(gtk.MenuBar, '<main>', accelgroup)
	item_factory.create_items(DiagramView.__menu_items, self)

	menubar = item_factory.get_widget('<main>')
	vbox.pack_start(menubar, gtk.FALSE, gtk.FALSE, 0)
	menubar.show()

	table = gtk.Table(2,2, gtk.FALSE)
	table.set_row_spacings (4)
	table.set_col_spacings (4)
	vbox.pack_start (table)
	table.show()

	frame = gtk.Frame()
	frame.set_shadow_type (gtk.SHADOW_IN)
	table.attach (frame, 0, 1, 0, 1,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK)
	frame.show()

	view.set_scroll_region(0, 0, 600, 450)
	frame.add (view)
	view.show()
	
	sbar = gtk.VScrollbar (view.get_vadjustment())
	table.attach (sbar, 1, 2, 0, 1, gtk.FILL,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK)
	sbar.show()

	sbar = gtk.HScrollbar (view.get_hadjustment())
	table.attach (sbar, 0, 1, 1, 2, gtk.EXPAND | gtk.FILL | gtk.SHRINK,
		      gtk.FILL)
	sbar.show()

	win.show()
	
	self.window = win
	self.canvasview = view
	self.diagram = dia

    def __menu_item_cb (self, action, widget):
	view = self.canvasview
	dia = self.diagram

	def pre_button_press (tool, view, event):
	    view.unselect_all()
	    return 0

	def post_button_press (tool, view, event, diagram, uml_type):
	    print 'Unset_tool:', tool, view, event
	    if uml_type is not None:
		factory = UML.ElementFactory()
		subject = factory.create (uml_type)
		if issubclass (uml_type, UML.Namespace):
		    subject.namespace = dia.namespace
		tool.new_object.set_subject(subject)
	    view.set_tool (None)
	    print 'Tool unset'
	    return 0

	def set_placement_tool (diagram_type, uml_type):
	    #diagram = view.get_data ('diagram')
	    tool = diacanvas.PlacementTool (diagram_type)
	    view.set_tool (tool)
	    tool.connect ('button_press_event', pre_button_press)
	    tool.connect ('button_release_event', post_button_press,
	    			dia, uml_type)

	print 'Action:', action, gtk.item_factory_path_from_widget(widget), view
	view.canvas.push_undo(None)

	if action == FILE_LOAD:
	    factory = UML.ElementFactory ()
	    print 'unset_canvas'
	    view.unset_canvas ()
	    print 'UML.flush'
	    del self.diagram
	    factory.flush ()
	    print 'UML.load'
	    factory.load ('a.xml')
	    print 'UML.lookup'
	    self.diagram = factory.lookup (2)
	    print 'view.set_canvas'
	    view.set_canvas (self.diagram.canvas)
	elif action == FILE_SAVE:
	    factory = UML.ElementFactory ()
	    factory.save ('a.xml')
	elif action == FILE_DUMP:
	    factory = UML.ElementFactory ()
	    for val in factory.values():
	        print 'Object', val
		for key in val.__dict__.keys():
		    print '	', key, ':',
		    if isinstance (val.__dict__[key], UML.Sequence):
			print val.__dict__[key].list
		    else:
		        print val.__dict__[key]

	elif action == FILE_QUIT:
	    gtk.Widget.destroy (self.window)
	    gtk.main_quit()
	elif action == EDIT_UNDO:
	    view.canvas.pop_undo()
	elif action == EDIT_REDO:
	    view.canvas.pop_redo()
	elif action == EDIT_DEL_FOCUSED:
	    # If the item is a composite, remove the parent...
	    item = view.focus_item.item
	    while item and item.flags & diacanvas.COMPOSITE:
	    	item = item.parent
	    if item and item.parent:
		item.parent.remove (item)
	elif action == VIEW_ZOOM_IN:
	    view.set_zoom (view.get_zoom() + 0.1)
	elif action == VIEW_ZOOM_OUT:
	    view.set_zoom (view.get_zoom() - 0.1)
	elif action == VIEW_ZOOM_100:
	    view.set_zoom (1.0)
	elif action == VIEW_SNAP_TO_GRID:
	    snap = view.canvas.get_property ('snap_to_grid')
	    view.canvas.set_property ('snap_to_grid', not snap)

	elif action == ITEM_ADD_ACTOR:
	    set_placement_tool (diagram.Actor, UML.Actor)

	elif action == ITEM_ADD_USECASE:
	    set_placement_tool (diagram.UseCase, UML.UseCase)
	elif action == ITEM_ADD_COMMENT:
	    set_placement_tool (diagram.Comment, UML.Comment)
	elif action == ITEM_ADD_COMMENT_LINE:
	    set_placement_tool (diagram.CommentLine, None)
	elif action == ITEM_ADD_GENERALIZATION:
	    set_placement_tool (diagram.Generalization, None)
	elif action == ITEM_ADD_REALIZATION:
	    set_placement_tool (diagram.Realization, None)
	elif action == ITEM_ADD_DEPENDENCY:
	    set_placement_tool (diagram.Dependency, None)
	elif action == ITEM_ADD_INCLUDE:
	    set_placement_tool (diagram.Include, None)
	elif action == ITEM_ADD_EXTEND:
	    set_placement_tool (diagram.Extend, None)
	else:
	    print 'This item is not iimplemented yet.'

    __menu_items = (
	( '/_File', None, None, 0, '<Branch>' ),
	( '/File/_Load from a.xml', '<control>L', __menu_item_cb, FILE_LOAD, ''),
	( '/File/_Save to a.xml', '<control>S', __menu_item_cb, FILE_SAVE, ''),
	( '/File/_Dump', '<control>D', __menu_item_cb, FILE_DUMP, ''),
	( '/File/sep1', None, None, 0, '<Separator>' ),
	( '/File/_Quit', '<control>Q', __menu_item_cb, FILE_QUIT, ''),
	( '/_Edit', None, None, 0, '<Branch>' ),
	( '/Edit/_Undo', '<control>Z', __menu_item_cb, EDIT_UNDO ),
	( '/Edit/_Redo', '<control>R', __menu_item_cb, EDIT_REDO ),
	( '/Edit/Delete f_Ocused', None, __menu_item_cb, EDIT_DEL_FOCUSED ),
	( '/_View', None, None, 0, '<Branch>' ),
	( '/View/Zoom _In', None, __menu_item_cb, VIEW_ZOOM_IN ),
	( '/View/Zoom _Out', None, __menu_item_cb, VIEW_ZOOM_OUT ),
	( '/View/_Zoom 100%', None, __menu_item_cb, VIEW_ZOOM_100 ),
	( '/View/sep1', None, None, 0, '<Separator>' ),
	( '/View/_Snap to grid', None, __menu_item_cb, VIEW_SNAP_TO_GRID, '<ToggleItem>' ),
	( '/New _Item', None, None, 0, '<Branch>' ),
	( '/New Item/Actor', None, __menu_item_cb, ITEM_ADD_ACTOR ),
	( '/New Item/Use Case', None, __menu_item_cb,  ITEM_ADD_USECASE ),
	( '/New Item/Comment', None, __menu_item_cb,  ITEM_ADD_COMMENT ),
	( '/New Item/Comment Line', None, __menu_item_cb,  ITEM_ADD_COMMENT_LINE ),
	( '/New Item/Generalization', None, __menu_item_cb,  ITEM_ADD_GENERALIZATION ),
	( '/New Item/Dependency', None, __menu_item_cb,  ITEM_ADD_DEPENDENCY ),
	( '/New Item/Realization', None, __menu_item_cb,  ITEM_ADD_REALIZATION ),
	( '/New Item/Include', None, __menu_item_cb,  ITEM_ADD_INCLUDE ),
	( '/New Item/Extend', None, __menu_item_cb,  ITEM_ADD_EXTEND )
    )

