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


from django.conf import settings
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='automated_workflow', type='direct')
channel.queue_declare(queue='create_task_test', durable=True)
channel.queue_declare(queue='run_task_test', durable=True)
channel.queue_declare(queue='flow_test')
channel.queue_bind(exchange='automated_workflow', queue='create_task_test')
channel.queue_bind(exchange='automated_workflow', queue='run_task_test')


def create_task_producer(message):
    if settings.TESTING:  # replace this with mock
        return
    channel.basic_publish(exchange='automated_workflow', routing_key='create_task_test', body=message, properties=pika.BasicProperties(delivery_mode=2))
    connection.close()


def test_publish(message):
    if settings.TESTING:  # replace this with mock
        return
    channel.basic_publish(exchange='automated_workflow', routing_key='flow_test', body=message)


def run_task_producer(message):
    if settings.TESTING:  # replace this with mock
        return
    channel.basic_publish(exchange='automated_workflow', routing_key='run_task_test', body=message, properties=pika.BasicProperties(delivery_mode=2))
    connection.close()
