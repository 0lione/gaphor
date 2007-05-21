
import gtk
import unittest

from gaphor.application import restart, Application
from gaphor.ui.diagramtab import DiagramTab
from gaphor.ui.diagramtoolbox import DiagramToolbox
from gaphor import UML

class DiagramToolboxTestCase(unittest.TestCase):

    def setUp(self):
        restart()
        Application.init(services=['element_factory', 'properties'])
        diagram = UML.Diagram()
        tab = DiagramTab(None)
        tab.diagram = diagram
        tab.construct()
        self.tab = tab

    def test_standalone_construct_with_diagram(self):
        pass # is setUp()

    def _test_placement_action(self, action):
        self.tab.toolbox.action_group.get_action(action).activate()
        assert self.tab.view.tool
        # Ensure the factory is working
        self.tab.view.tool._factory()

    def test_placement_pointer(self):
        self.tab.toolbox.action_group.get_action('toolbox-pointer').activate()

    def test_placement_comment(self):
        self._test_placement_action('toolbox-comment')

    def test_placement_comment_line(self):
        self._test_placement_action('toolbox-comment-line')

    def test_placement_class(self):
        self._test_placement_action('toolbox-class')

    def test_placement_interface(self):
        self._test_placement_action('toolbox-interface')

    def test_placement_package(self):
        self._test_placement_action('toolbox-package')

    def test_placement_component(self):
        self._test_placement_action('toolbox-component')

    def test_placement_node(self):
        self._test_placement_action('toolbox-node')

    def test_placement_artifact(self):
        self._test_placement_action('toolbox-artifact')

    def test_placement_association(self):
        self._test_placement_action('toolbox-association')

    def test_placement_dependency(self):
        self._test_placement_action('toolbox-dependency')

    def test_placement_generalization(self):
        self._test_placement_action('toolbox-generalization')

    def test_placement_implementation(self):
        self._test_placement_action('toolbox-implementation')

# vim:sw=4:et:ai
