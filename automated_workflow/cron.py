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

from .models import NodeTask
from django_cron import CronJobBase, Schedule
from .amqp_producers import run_task_producer
import json


class AutomatedWorkflowTaskCronJob(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'automated_workflow.task_cron_job'    # a unique code

    def do(self):
        print("running automated workflow")
        ready_tasks = NodeTask.objects.ready_tasks()
        for task in ready_tasks:
            d = {}
            d['node_task_id'] = task.id
            run_task_producer(json.dumps(d))

