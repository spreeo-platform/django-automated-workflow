from django.test import TestCase
from django.core.management import call_command
from automated_workflow.models import Node, NodeAction, NodeRule, NodeTask, WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED, WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED


class EnableNodeTest(TestCase):

    def setUp(self):

        self.node_a = Node.create_node(name="Node A Test")
        self.node_a_rule_a = NodeRule.create_node_rule(node=self.node_a, name="Node Rule A Test", rule="node_rule_a", pull_status=True)

    def test_enable_node(self):

        self.assertEquals(self.node_a.mode, WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED)
        self.node_a.enable_node()
        self.assertEquals(self.node_a.mode, WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)

    def test_run_active_pull_rules(self):

        self.assertEquals(self.node_a_rule_a.mode, WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED)

        self.assertTrue(self.node_a_rule_a.pull_status)

        self.node_a.enable_node()

        updated_node_rule_a = NodeRule.objects.get(id=self.node_a_rule_a.id)

        self.assertEquals(updated_node_rule_a.mode, WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)

        self.assertFalse(updated_node_rule_a.pull_status)


class CreateNodeTest(TestCase):

    def test_create_node(self):
        self.assertEquals(Node.objects.all().count(), 0)

        self.node_a = Node.create_node(name="Node A Test")
        self.assertEquals(Node.objects.all().count(), 1)




