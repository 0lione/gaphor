'''
CommentLine -- A line that connects a comment to another model element.
'''
# vim:sw=4

import gobject
import diacanvas
import UML
import relationship

class DependencyItem(relationship.RelationshipItem):

    def __init__(self):
	relationship.RelationshipItem(self)
	self.set(dash=(7.0, 5.0), has_head=1, head_fill_color=0,
		 head_a=0.5, head_b=15.0, head_c=10.0, head_d=10.0)
	
    # Gaphor Connection Protocol

    def find_relationship(self, head_subject, tail_subject):
	for rel in head_subject.supplierDependency:
	    if rel.client is tail_subject:
		return rel

    def allow_connect_handle(self, handle, connecting_to):
	"""
	This method is called by a canvas item if the user tries to connect
	this object's handle. allow_connect_handle() checks if the line is
	allowed to be connected. In this case that means that one end of the
	line should be connected to a Comment.
	Returns: TRUE if connection is allowed, FALSE otherwise.
	"""
	try:
	    return isinstance(handle.owner.subject, UML.ModelElement)
	except AttributeError:
	    return 0

    def confirm_connect_handle (self, handle):
	"""
	This method is called after a connection is established. This method
	sets the internal state of the line and updates the data model.
	"""
	print 'confirm_connect_handle', handle
	c1 = self.handles[0].connected_to
	c2 = self.handles[-1].connected_to
	if c1 and c2:
	    s1 = c1.subject
	    s2 = c2.subject
	    relation = self.find_relationship(s1, s2)
	    if not relation:
		relation = Dependency()
		relation.supplier = s1
		relation.client = s2
	    self.set_property ('subject', relation)

    def allow_disconnect_handle (self, handle):
	return 1

    def confirm_disconnect_handle (self, handle, was_connected_to):
	print 'confirm_disconnect_handle', handle
	c1 = None
	c2 = None
	if handle is self.handles[0]:
	    c1 = was_connected_to
	    c2 = self.handles[-1].connected_to
	elif handle is self.handles[-1]:
	    c1 = self.handles[0].connected_to
	    c2 = was_connected_to
	
	if c1 and c2:
	    s1 = c1.subject
	    s2 = c2.subject
	    if isinstance (s1, UML.Comment):
		del s1.annotatedElement[s2]
	    elif isinstance (s2, UML.Comment):
		del s2.annotatedElement[s1]
	    else:
		raise TypeError, 'One end of the CommentLine should connect to a Comment. How could this connect anyway?'

gobject.type_register(DependencyItem)
