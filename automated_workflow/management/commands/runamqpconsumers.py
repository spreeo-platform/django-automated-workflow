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

from django.core.management.base import BaseCommand
import pika
from automated_workflow.models import NodeTask, NodeRule, NodeAction, TASK_STATUS_COMPLETED
from automated_workflow.base import BaseAction
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='flow_test')
channel.queue_declare(queue='run_task_test', durable=True)
channel.queue_declare(queue='create_task_test', durable=True)


def callback_node_task_creator(ch, method, properties, body):
    decoded = body.decode('utf-8')  # body in bytes not in string
    d = json.loads(decoded)
    node_rule = NodeRule.objects.get(id=int(d['node_rule_id']))
    NodeTask.create_task(rule=node_rule, node=node_rule.node, data=d['data'], action_timedelta=node_rule.action_timedelta)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("Task created")


def callback_task_dispatcher(ch, method, properties, body):
    decoded = body.decode('utf-8')  # body in bytes not in string
    d = json.loads(decoded)
    task = NodeTask.objects.get(id=int(d['node_task_id']))
    node_actions = NodeAction.objects.filter_by_node(task.node)
    for node_action in node_actions:
        action = BaseAction.get_instance(node_action.action)
        dispatcher_params = action.get_dispatcher_parameters()
        dispatcher_kwargs = {}
        data = task.data
        context = {}
        for param in dispatcher_params:
            context.update(data.get('context', {}))
            context.update(node_action.data.get('setup_params', {}))
            for key, value in context.items():
                if key == param:
                    dispatcher_kwargs[key] = value
        dispatcher_kwargs['context'] = context
        action_return_kwargs = action.dispatcher(**dispatcher_kwargs)
        task_context = task.data.get('context', {})
        task_context.update(action_return_kwargs)
        task.save()
        print("Action dispatched")
    task.status = TASK_STATUS_COMPLETED
    task.save()
    ch.basic_ack(delivery_tag=method.delivery_tag)


class Command(BaseCommand):

    def handle(self, *args, **options):
        channel.basic_consume(callback_node_task_creator, queue='create_task_test')
        channel.basic_consume(callback_task_dispatcher, queue='run_task_test')
        print("Consuming Message")
        channel.start_consuming()

