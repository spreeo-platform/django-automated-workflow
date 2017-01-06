
=======================
   AUTOMATED WORKFLOW
=======================

Automated Workflow is an action/trigger app

Quick start
-----------

1. Add "automated_workflow" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'automated_workflow',
    ]

2. Include the URLconf in your project urls.py like this::

    url(r'^automated_workflow/', include('automated_workflow.urls')),

3. Run `python manage.py migrate` to create the models.
