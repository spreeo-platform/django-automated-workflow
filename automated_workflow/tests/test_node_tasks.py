from django.test import TestCase
from django.core.management import call_command
from automated_workflow.models import Node, NodeAction, NodeRule, NodeTask, WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED, WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED
from django.utils import timezone


class CreateNodeTaskTest(TestCase):

    def setUp(self):

        self.node_a = Node.create_node(name="Node A Test", mode=WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)
        self.node_a_rule_a = NodeRule.create_node_rule(node=self.node_a, name="Node Rule A Test", rule="node_rule_a")

    def test_create_node_task(self):

        self.assertEquals(NodeTask.objects.all().count(), 0)

        NodeTask.create_task(node=self.node_a, rule=self.node_a_rule_a, data={})
        self.assertEquals(NodeTask.objects.all().count(), 1)


class NodeTaskManagerTest(TestCase):

    def setUp(self):

        self.node_a = Node.create_node(name="Node A Test", mode=WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)
        self.node_a_rule_a = NodeRule.create_node_rule(node=self.node_a, name="Node Rule A Test", rule="node_rule_a")

        self.task_a = NodeTask.create_task(node=self.node_a, rule=self.node_a_rule_a, data={})

    def test_ready_tasks(self):
        self.task_b = NodeTask.create_task(node=self.node_a, rule=self.node_a_rule_a, data={}, action_timedelta=timezone.timedelta(days=1))

        self.assertEquals(NodeTask.objects.all().count(), 2)

        self.assertEquals(NodeTask.objects.ready_tasks().count(), 1)

