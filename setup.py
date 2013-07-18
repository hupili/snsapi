#!/usr/bin/env python

from distutils.core import setup

setup(name='snsapi',
      version='0.6.0',
      description='lightweight middleware for multiple social networking services',
      author='Pili Hu',
      author_email='me@hupili.net',
      url='https://github.com/hupili/snsapi',
      packages=['snsapi', 'snsapi.third', 'snsapi.plugin', 'snsapi.plugin_trial'],
      package_data={'snsapi': ['conf/*.ini', 'conf/*.example']},
      scripts=['snscli.py', 'snsgui.py'],
      classifiers=[
          'License :: Public Domain',
          'Intended Audience :: Developers',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Science/Research',
          'Natural Language :: English',
          'Programming Language :: Python :: 2.7',
          'Development Status :: 4 - Beta',
      ]
     )
