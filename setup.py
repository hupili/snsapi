#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup

REQUIRES = [
    'oauth2 (>=1.5.211)',
    'httplib2 (>=0.8)',
    'python_dateutil (>=2.1)',
    'lxml (>=2.3.2)',
    'nose (>=1.3.0)',
]

INSTALL_REQUIRES=[
    'oauth2',
    'httplib2',
    'python_dateutil',
    'lxml',
]

setup(name='snsapi',
      version='0.7.0',
      description='lightweight middleware for multiple social networking services',
      author='Pili Hu',
      author_email='me@hupili.net',
      maintainer='Pili Hu',
      maintainer_email='me@hupili.net',
      url='https://github.com/hupili/snsapi',
      packages=['snsapi', 'snsapi.third', 'snsapi.plugin', 'snsapi.plugin_trial'],
      package_data={'snsapi': ['data/*.ini', 'data/*.example']},
      data_files=[
          ('data', ['snsapi/data/init-channel.json.example', 'snsapi/data/snsgui.ini'])
      ],
      include_package_data=True,
      scripts=['snscli.py', 'snsgui.py'],
      provides=['snsapi'],
      requires=REQUIRES,
      tests_require=['nose'],
      install_requires=INSTALL_REQUIRES,
      classifiers=[
          'License :: Public Domain',
          'Intended Audience :: Developers',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Science/Research',
          'Natural Language :: English',
          'Programming Language :: Python :: 2.7',
          'Development Status :: 4 - Beta',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Communications :: Chat',
          'Topic :: Internet',
      ]
     )
