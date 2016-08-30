import sys
from setuptools import setup


def forbid_publish():
    argv = sys.argv
    blacklist = ['register', 'upload']

    for command in blacklist:
        if command in argv:
            values = {'command': command}
            raise RuntimeError('Command "%(command)s" has been blacklisted' %
                               values)

forbid_publish()

setup(
    name='email-parser',
    packages=[
        'email_parser'
    ],
    package_dir={
        'email_parser': 'email_parser'
    },
    test_suite='tests',
    author='komal gupta',
    
)
