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

import inspect


class BaseRule(object):  # framework
    _instances = []

    def __init__(self, name, rule_type, setup_params, return_params):
        self.name = name
        self.rule_type = rule_type
        self.setup_parameters = setup_params
        self.return_params = return_params
        BaseRule._instances.append(self)

    @staticmethod
    def get_instance(name):
        for instance in BaseRule._instances:
            if instance.name == name:
                return instance
        return None

    def setup_params(self):
        return self.setup_params

    @staticmethod
    def get_all_instances():
        return BaseRule._instances


class BaseAction(object):
    # add return kwargs
    _instances = []

    def __init__(self, name, dispatcher, setup_params, return_params):
        self.name = name
        self.dispatcher = dispatcher
        self.setup_params = setup_params
        self.return_params = return_params
        BaseAction._instances.append(self)

    def get_dispatcher_parameters(self):
        return inspect.getargspec(self.dispatcher).args

    @staticmethod
    def get_instance(name):
        for instance in BaseAction._instances:
            if instance.name == name:
                return instance
        return None










