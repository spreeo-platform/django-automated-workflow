"""
Copyright 2017 PERSADA TERBILANG SDN. BHD.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

AUTHOR : DALIA DAUD
EMAIL : daliadaud@gmail.com
"""

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from .amqp_producers import create_task_producer
import json
# Create your models here.

WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED = 1
WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED = 2


WORKFLOW_RULE_ACTION_STATUS_CHOICES = (
    (WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED, 'Disabled'),
    (WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED, 'Enabled'),
)

TASK_STATUS_READY = 1  # ready to be dispatch
TASK_STATUS_PROCESSING = 2
TASK_STATUS_COMPLETED = 3
TASK_STATUS_FAILED = 4
TASK_STATUS_PENDING = 99


TASK_STATUS_CHOICES = (
    (TASK_STATUS_READY, 'Ready'),  # ready to be queued
    (TASK_STATUS_PROCESSING, 'Processing'),  # retry if a certain task went pass a certain time in queued 'state'
    (TASK_STATUS_COMPLETED, 'Completed'),
    (TASK_STATUS_FAILED, 'Failed'),
    (TASK_STATUS_PENDING, 'Pending'),
)


class NodeActionQuerySet(models.QuerySet):

    def filter_by_node(self, node):
        return self.filter(node=node)

    def search(self, search_term):
        node_action_ids = []

        node_action_ids.extend(NodeAction.objects.filter(name__icontains=search_term).values_list('id', flat=True))

        return self.filter(pk__in=node_action_ids)


class NodeActionManager(models.Manager):
    def get_queryset(self):
        return NodeActionQuerySet(self.model, using=self._db).order_by('priority')

    def filter_by_node(self, node):
        return self.get_queryset().filter_by_node(node=node)

    def search(self, search_term):
        return self.get_queryset().search(search_term=search_term)


class NodeRuleQuerySet(models.QuerySet):

    def enable_node_rules(self):
        self.update(mode=WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED)

    def filter_by_node(self, node):
        return self.filter(node=node)

    def filter_by_active_pull_status(self, node, mode):
        return self.filter(node=node, mode=mode, pull_status=True)

    def search(self, search_term):
        node_rule_ids = []

        node_rule_ids.extend(NodeRule.objects.filter(name__icontains=search_term).values_list('id', flat=True))

        return self.filter(pk__in=node_rule_ids)


class NodeRuleManager(models.Manager):
    def get_queryset(self):
        return NodeRuleQuerySet(self.model, using=self._db)

    def search(self, search_term):
        return self.get_queryset().search(search_term=search_term)

    def filter_by_node(self, node):
        return self.get_queryset().filter_by_node(node=node)

    def filter_by_active_pull_status(self, node, mode=WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED):
        return self.get_queryset().filter_by_active_pull_status(node=node, mode=mode)


class NodeTaskQuerySet(models.QuerySet):

    def ready_tasks(self):
        node_task_ids = []

        node_task_ids.extend(NodeTask.objects.filter(status=TASK_STATUS_READY, execute_date__lte=timezone.now()).values_list('id', flat=True))

        return self.filter(pk__in=node_task_ids)


class NodeTaskManager(models.Manager):
    def get_queryset(self):
        return NodeTaskQuerySet(self.model, using=self._db)

    def ready_tasks(self):
        return self.get_queryset().ready_tasks()


class Workflow(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    mode = models.IntegerField(choices=WORKFLOW_RULE_ACTION_STATUS_CHOICES, default=WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Node(models.Model):
    name = models.CharField(max_length=255)
    workflow = models.ForeignKey(Workflow, related_name='workflow_nodes', blank=True, null=True)
    mode = models.IntegerField(choices=WORKFLOW_RULE_ACTION_STATUS_CHOICES, default=WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @staticmethod
    def create_node(name, workflow=None, mode=WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED):
        return Node.objects.create(name=name, workflow=workflow, mode=mode)

    def enable_node(self):  # enable run and run pull mode rules
        # enable node and rules at the same time
        self.mode = WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED
        self.save()
        node_rules = NodeRule.objects.filter_by_node(node=self)
        node_rules.enable_node_rules()
        self.run_active_pull_rules()

    def run_active_pull_rules(self):
        node_rules = NodeRule.objects.filter_by_active_pull_status(node=self)
        for node_rule in node_rules:
            d = {}
            d['node_rule_id'] = node_rule.id
            d['data'] = node_rule.get_data('context')
            create_task_producer(json.dumps(d))
            node_rule.pull_status = False
            node_rule.save()


class NodeAction(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    node = models.ForeignKey(Node, related_name='node_actions')
    mode = models.IntegerField(choices=WORKFLOW_RULE_ACTION_STATUS_CHOICES, default=WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED)
    action = models.CharField(max_length=255)  # same type of action is acceptable in the same workflow ie send email
    priority = models.IntegerField(default=1)
    data = JSONField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = NodeActionManager()

    def __str__(self):
        return self.name

    @staticmethod
    def create_node_action(name, node, action, mode=WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED):
        return NodeAction.objects.create(name=name, node=node, mode=mode, action=action, data={})


class NodeRule(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    node = models.ForeignKey(Node, related_name='node_rules')
    mode = models.IntegerField(choices=WORKFLOW_RULE_ACTION_STATUS_CHOICES, default=WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED)

    rule = models.CharField(max_length=255)
    data = JSONField(blank=True, null=True)
    action_timedelta = models.DurationField()
    pull_status = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = NodeRuleManager()

    class Meta:
        unique_together = ('node', 'rule')

    def __str__(self):
        return self.name

    @staticmethod
    def create_node_rule(node, name, rule, setup_params="", action_timedelta=timezone.timedelta(0),
                         mode=WORKFLOW_NODE_RULE_ACTION_STATUS_DISABLED, pull_status=False, context=None):

        d = {}
        d['context'] = context
        d['setup_params'] = setup_params
        return NodeRule.objects.create(node=node, name=name, mode=mode, rule=rule, data=d, action_timedelta=action_timedelta, pull_status=pull_status)

    def get_data(self, key):
        return self.data[key]

    def activate_pull_status(self):
        self.pull_status = True
        self.save()

    def enable_rule(self):  # will run any active pull rules
        self.mode = WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED
        self.save()
        if self.node.mode == WORKFLOW_NODE_RULE_ACTION_STATUS_ENABLED:
            d = {}
            d['node_rule_id'] = self.id
            d['data'] = self.get_data('context')
            create_task_producer(json.dumps(d))
            self.pull_status = False
            self.save()


class NodeTask(models.Model):
    node = models.ForeignKey(Node, related_name='node_tasks')
    rule = models.ForeignKey(NodeRule, related_name='rule_tasks')

    status = models.IntegerField(choices=TASK_STATUS_CHOICES, default=TASK_STATUS_READY)
    data = JSONField(blank=True, null=True)
    execute_date = models.DateTimeField(default=timezone.now)
    # 'now' without parentheses will pass the callable now instead of being called once when models.py loads(now())

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = NodeTaskManager()

    @staticmethod
    def create_task(node, rule, data, action_timedelta=timezone.timedelta(0)):
        d = {}
        d['context'] = data
        return NodeTask.objects.create(node=node, rule=rule, data=d, status=TASK_STATUS_READY,
                                       execute_date=timezone.now() + action_timedelta)





