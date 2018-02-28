#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
import os

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')
test_requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_requirements.txt')
setup_requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'setup_requirements.txt')

with open(requirements_path) as requirements_file:
    requirements = requirements_file.readlines()

with open(test_requirements_path) as test_requirements_file:
    test_requirements = test_requirements_file.readlines()

with open(setup_requirements_path) as setup_requirements_file:
    setup_requirements = setup_requirements_file.readlines()

setup(
    name='atlasclient',
    version='0.1.0',
    description="Apache Atlas client",
    long_description=readme + '\n\n' + history,
    author="Jean-Baptiste Poullet",
    author_email='jeanbaptistepoullet@gmail.com',
    url='https://github.com/jpoullet2000/atlasclient',
    packages=find_packages(include=['atlasclient']),
    include_package_data=True,
    install_requires=requirements,
    license='Apache Software License 2.0',
    zip_safe=False,
    keywords='atlasclient',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    #setup_requires=setup_requirements,
)
