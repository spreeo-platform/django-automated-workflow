from django.test import TestCase
from django.core.management import call_command
from automated_workflow.models import Node, NodeAction, NodeRule, NodeTask, WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED, WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED


class PullStatusTest(TestCase):

    def setUp(self):

        self.node_a = Node.create_node(name="Node A Test", mode=WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)
        self.node_a_rule_a = NodeRule.create_node_rule(node=self.node_a, name="Node Rule A Test", rule="node_rule_a")

    def test_activate_pull_status(self):

        self.assertFalse(self.node_a_rule_a.pull_status)
        self.node_a_rule_a.activate_pull_status()
        self.assertTrue(self.node_a_rule_a.pull_status)

    def test_enable_rule(self):

        self.assertEquals(self.node_a_rule_a.mode, WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED)

        self.node_a_rule_a.activate_pull_status()
        self.assertTrue(self.node_a_rule_a.pull_status)

        self.node_a_rule_a.enable_rule()

        self.assertEquals(self.node_a_rule_a.mode, WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)

        self.assertFalse(self.node_a_rule_a.pull_status)


class CreateNodeRuleTest(TestCase):

    def setUp(self):
        self.node_a = Node.create_node(name="Node A Test", mode=WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)

    def test_create_node_rule(self):

        self.assertEquals(NodeRule.objects.all().count(), 0)
        self.node_a_rule_a = NodeRule.create_node_rule(node=self.node_a, name="Node Rule A Test", rule="node_rule_a")
        self.assertEquals(NodeRule.objects.all().count(), 1)


class NodeRuleDataTest(TestCase):

    def setUp(self):
        self.context = {}
        self.context['test_id'] = 1
        self.context['test_name'] = "test_name"

        self.setup_params = {}
        self.setup_params['param_1'] = 1
        self.setup_params['param_2'] = 2

        self.node_a = Node.create_node(name="Node A Test", mode=WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)
        self.node_a_rule_a = NodeRule.create_node_rule(node=self.node_a, name="Node Rule A Test", rule="node_rule_a",
                                                       setup_params=self.setup_params, context=self.context)

    def test_get_data_context(self):
        self.assertEquals(self.node_a_rule_a.get_data(key='context'), self.context)

    def test_get_data_setup_params(self):
        self.assertEquals(self.node_a_rule_a.get_data(key='setup_params'), self.setup_params)


class NodeRuleManagerTest(TestCase):

    def setUp(self):

        self.node_a = Node.create_node(name="Node A Test", mode=WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)
        self.node_a_rule_a = NodeRule.create_node_rule(node=self.node_a, name="Node Rule ABC Test", rule="rule_abc")
        self.node_a_rule_b = NodeRule.create_node_rule(node=self.node_a, name="Node Rule XYZ Test", rule="rule_xyz")
        self.node_a_rule_c = NodeRule.create_node_rule(node=self.node_a, name="ABC", rule="abc")

    def test_manager_search(self):

        self.assertEquals(NodeRule.objects.all().count(), 3)
        self.assertEquals(NodeRule.objects.search(search_term='Test').count(), 2)
        self.assertEquals(NodeRule.objects.search(search_term='ABC').count(), 2)
        self.assertEquals(NodeRule.objects.search(search_term='XYZ').count(), 1)

    def test_manager_filter_by_node(self):
        self.assertEquals(NodeRule.objects.filter_by_node(node=self.node_a).count(), 3)

    def test_manager_enable_node_rules(self):

        self.assertEquals(self.node_a_rule_a.mode, WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED)
        self.assertEquals(self.node_a_rule_b.mode, WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED)
        self.assertEquals(self.node_a_rule_c.mode, WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED)

        node_rules = NodeRule.objects.filter_by_node(node=self.node_a)
        node_rules.enable_node_rules()

        updated_node_a_rule_a = NodeRule.objects.get(id=self.node_a_rule_a.id)
        updated_node_a_rule_b = NodeRule.objects.get(id=self.node_a_rule_b.id)
        updated_node_a_rule_c = NodeRule.objects.get(id=self.node_a_rule_c.id)

        self.assertEquals(updated_node_a_rule_a.mode, WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)
        self.assertEquals(updated_node_a_rule_b.mode, WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)
        self.assertEquals(updated_node_a_rule_c.mode, WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)

    def test_manager_filter_by_active_pull_status(self):

        self.assertEquals(NodeRule.objects.filter_by_active_pull_status(node=self.node_a).count(), 0)

        self.node_a_rule_a.enable_rule()
        self.node_a_rule_a.activate_pull_status()

        self.assertTrue(self.node_a_rule_a.pull_status)
        self.assertEquals(self.node_a_rule_a.mode, WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)
        self.assertEquals(NodeRule.objects.filter_by_active_pull_status(node=self.node_a).count(), 1)




