#!/usr/bin/env python
# vim: sw=4
# Test application for diagram items.
#

import sys
import gtk
import diagram
import diacanvas
import UML
import tree

uc = getattr (UML, 'UseCase')
print 'getattr (UML, "UseCase") ->', uc

def mainquit(*args):
    for k in UML.elements.keys():
	print "Element", k, ":", UML.elements[k].__dict__
    print "Forcing Garbage collection:"
    gtk.main_quit()


model = UML.Model()

print "diagram creating"
dia = diagram.Diagram()
dia.namespace = model
print "diagram created"

treemodel = tree.NamespaceModel(model)

#item = canvas.root.add (diagram.Comment)
#item.move (30, 50)
#item = canvas.root.add (diagram.Actor)
#item.move (150, 50)
item = dia.create_item (diagram.UseCase, (50, 150))
usecase = item.get_subject()
#dia.create_item (diagram.UseCase, (50, 200), subject=usecase)

item = dia.create_item (diagram.Actor, (150, 50))
actor = item.get_subject()
actor.name = "Actor"

item = dia.create_item (diagram.Comment, (10,10))
comment = item.get_subject()

del item#, actor, usecase, comment

print "Comment.presentation:", comment.presentation.list
print "Actor.presentation:", actor.presentation.list
print "UseCase.presentation:", usecase.presentation.list
#view = diacanvas.CanvasView().set_canvas (dia.canvas)
#display_diagram (dia)
#display_canvas_view (diacanvas.CanvasView().set_canvas (dia.canvas))
win = dia.new_view()
win.connect ('destroy', mainquit)
print "diagram displayed"

#for k in UML.Element._hash.keys():
#    print "Element", k, ":", UML.Element._hash[k].__dict__

treemodel.dump()

print 'Going into main'
gtk.main()

UML.save('x.xml')

del win

treemodel.dump()

#print "Comment.presentation:", comment.presentation.list
#print "Actor.presentation:", actor.presentation.list
#print "UseCase.presentation:", usecase.presentation.list
print "removing diagram..."
dia.unlink()
del dia
#UML.update_model()
print "Comment.presentation:", comment.presentation.list
print "Actor.presentation:", actor.presentation.list
print "UseCase.presentation:", usecase.presentation.list
del actor
del usecase
del comment

UML.flush()

print "Garbage collection after gtk.main() has finished (should be empty):",
#UML.update_model()
for k in UML.elements.keys():
    print "Element", k, ":", UML.elements[k].__dict__

print "Program ended normally..."
