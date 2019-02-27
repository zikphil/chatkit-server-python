# -*- coding: utf-8 -*-
from setuptools import setup
import os
import re


# Lovingly adapted from https://github.com/kennethreitz/requests/blob/39d693548892057adad703fda630f925e61ee557/setup.py
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pusher_chatkit/version.py'), 'r') as fd:
    VERSION = re.search(r'^VERSION = [\']([^\']*)[\']',
                        fd.read(), re.MULTILINE).group(1)

if not VERSION:
    raise RuntimeError('Ensure `VERSION` is correctly set in ./pusher_chatkit/version.py')

setup(
    name='pusher-chatkit-server',
    version=VERSION,
    description='A Python library to interact with the Pusher Chatkit API',
    url='https://github.com/zikphil/chatkit-server-python',
    author='Philippe Labat',
    author_email='philippe@labat.ca',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    license='MIT',

    packages=[
        'pusher_chatkit'
    ],

    install_requires=[
        'requests>=2.3.0',
        'urllib3>=1.24.1',
        'PyJWT>=1.7.1'
    ],

    extras_require={
        'tornado': ['tornado>=5.0.0']
    },
)
