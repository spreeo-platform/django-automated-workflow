from django.test import TestCase
from django.core.management import call_command
from automated_workflow.models import Node, NodeAction, NodeRule, NodeTask, WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED, WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED


class CreateNodeActionTest(TestCase):

    def setUp(self):
        self.node_a = Node.create_node(name="Node A Test", mode=WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)
        self.node_a_rule_a = NodeRule.create_node_rule(node=self.node_a, name="Node Rule A Test", rule="")

    def test_create_node_action(self):
        self.assertEquals(NodeAction.objects.all().count(), 0)

        NodeAction.create_node_action(name="Node Action A", node=self.node_a, action='action_a')
        self.assertEquals(NodeAction.objects.all().count(), 1)


class NodeActionManagerTest(TestCase):

    def setUp(self):
        self.node_a = Node.create_node(name="Node A Test", mode=WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)
        self.node_b = Node.create_node(name="Node B Test", mode=WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)
        self.node_a_rule_a = NodeRule.create_node_rule(node=self.node_a, name="Node Rule A Test", rule="node_rule_a")

        self.node_a_action_a = NodeAction.create_node_action(name="Node Action ABC", node=self.node_a, action='action_abc', mode=WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)
        self.node_a_action_b = NodeAction.create_node_action(name="Node Action XYZ", node=self.node_a, action='action_xyz', mode=WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)
        self.node_a_action_c = NodeAction.create_node_action(name="Test", node=self.node_a, action='action_test', mode=WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)

        self.node_b_action_a = NodeAction.create_node_action(name="NodeB Action", node=self.node_b, action='action_test_b', mode=WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)

    def test_manager_filter_by_node(self):

        self.assertEquals(NodeAction.objects.all().count(), 4)

        self.assertEquals(NodeAction.objects.filter_by_node(node=self.node_a).count(), 3)
        self.assertEquals(NodeAction.objects.filter_by_node(node=self.node_b).count(), 1)

    def test_manager_search(self):

        self.assertEquals(NodeAction.objects.all().count(), 4)
        self.assertEquals(NodeAction.objects.search(search_term='Test').count(), 1)
        self.assertEquals(NodeAction.objects.search(search_term='ABC').count(), 1)
        self.assertEquals(NodeAction.objects.search(search_term='Node').count(), 3)