#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'requests>=2.18.4',
    # TODO: put package requirements here
]

setup_requirements = [
    'pytest-runner',
    # TODO(jpoullet2000): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    'pytest_mock>=1.6.3',
    # TODO: put package test requirements here
]

setup(
    name='atlasclient',
    version='0.1.0',
    description="Apache Atlas client",
    long_description=readme + '\n\n' + history,
    author="Jean-Baptiste Poullet",
    author_email='jeanbaptistepoullet@gmail.com',
    url='https://github.com/jpoullet2000/atlasclient',
    packages=find_packages(include=['atlasclient']),
    entry_points={
        'console_scripts': [
            'atlasclient=atlasclient.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='atlasclient',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
