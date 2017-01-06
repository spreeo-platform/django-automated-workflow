import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

PACKAGE = "automated_workflow"
NAME = "django-automated-workflow"
DESCRIPTION = "A trigger/rule action workflow for Django"
AUTHOR = "Dalia Daud"
AUTHOR_EMAIL = "daliadaud@gmail.com"
URL = "https://github.com/spreeo-platform/django-automated-workflow"
VERSION = __import__(PACKAGE).__version__


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=read("README.rst"),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="Apache License 2.0",
    url=URL,
    packages=find_packages(exclude=["tests.*", "tests"]),
    package_data=find_package_data(PACKAGE, only_in_packages=False),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
        ],
    install_requires=[
        "Django==1.10.4",
        "django-common-helpers==0.9.0",
        "django-cron==0.5.0",
        "pika==0.10.0",
        "psycopg2==2.6.2"
        ],
    zip_safe=False,
    )
