SNSAPI
======

A cross-platform **middleware** for Social Networking Services (SNS):

-  Unified interfaces and data structures.
-  The building block of a **user-centric** `meta social
   network <https://github.com/hupili/snsapi/wiki/Taxonomy>`__.
-  Near-zero infrastructure
   `requirements <https://github.com/hupili/snsapi/wiki/Installation>`__.
-  Play with your social channels `like a
   hacker <http://snsapi.ie.cuhk.edu.hk/>`__.

Lightning Demo 1 -- Read Twitter Timeline
-----------------------------------------

Step 1.
~~~~~~~

Register user and developer on Twitter. `Apply for application keys and
access
tokens <https://github.com/hupili/snsapi/wiki/Apply-for-app-key>`__.

Step 2.
~~~~~~~

Save the following codes to ``mytest.py`` in the root dir of this
project:

.. code:: python

    from snscli import *
    nc = new_channel('TwitterStatus')
    nc['app_key'] = 'Your Consumer Key from dev.twitter.com'
    nc['app_secret'] = 'Your Consumer Secret from dev.twitter.com'
    nc['access_key'] = 'Your Access Token from dev.twitter.com'
    nc['access_secret'] = 'Your Access Token Secret from dev.twitter.com'
    add_channel(nc)
    print home_timeline()

Filling your app credentials in the above script: ``app_key``,
``app_secret``, ``access_key``, ``access_key``.

Step 3.
~~~~~~~

Try it by ``python mytest.py``. You will see your home timeline from
twitter.

Remarks
~~~~~~~

SNSApi **unifies the interfaces** of all SNS such that retrieving new
messages from all other platforms are the same:

-  Create a new channel configuration and ``add_channel`` it.
-  Invoke a single ``home_timeline()`` to obtain an aggregated timeline
   from all channels in a batch.

Lightning Demo 2 -- Backup Your Data
------------------------------------

Step 1.
~~~~~~~

`Configure a
channel.json <https://github.com/hupili/snsapi/wiki/Configurations>`__
file with two channels:

-  One is called "myrenren" and it interfaces with Renren (an OSN in
   China).
-  The other is called "mysqlite" and it interfaces with a SQLite3 DB.

See `one
example <https://github.com/hupili/snsapi/tree/master/app/backup-renren/conf/channel.json.example>`__
``channel.json`` configuration.

Step 2.
~~~~~~~

Save the following codes to ``backup.py`` in the root dir of this
project:

.. code:: python

    from snsapi.snspocket import SNSPocket
    sp = SNSPocket()
    sp.load_config()
    sp.auth()

    ml = sp['myrenren'].home_timeline()
    for m in ml:
        sp['mysqlite'].update(m)

Step 3.
~~~~~~~

Try it by ``python backup.py``. Now your timeline of Renren (latest 20
messages by default) is backed up to the SQLite DB. You can run this
script on a regular basis to backup data from all kinds of SNS.

Remarks
~~~~~~~

SNSApi unifies the **data structures** of all SNS so as to enable
flexible/ programmable inter-operation between those services:

-  Backup one message in SQLite is just "update a status" there.
-  In order to read those messages, just invoke ``home_timeline`` of
   your SQLite channel.
-  The data in SQLite DB are ready for further analysis. For example, I
   remember someone said that "snsapi is awesome". Who posted it? I can
   not recall. Now, enter sqlite and use one line of command to get the
   answer: ``select * from message where text like '%snsapi%';``.
-  You can also use EMail or RSS to distribute your statuses and follow
   the updates of your friends.
-  When there are new platforms, it's just one configuration away to use
   them. The intervention from app developer is not needed.

Lightning Demo 3 -- An Ad-Hoc DSN
---------------------------------

`Decentralized Social
Network <https://github.com/hupili/snsapi/wiki/Taxonomy>`__ (DSN) is the
next paradigm of social networking. Current centralized services have a
lot of problems, e.g. `Spying for
free <http://en.wikipedia.org/wiki/PRISM_%28surveillance_program%29>`__.

SNSApi is just a middleware to offload your burden in interfacing with
different platforms. Now, try to build something without worrying about
the interfacing detials.

.. figure:: https://docs.google.com/drawings/d/1S-REIYN46lR6WpmimG1v5CPJdDYlfVnGDwY3vL5Tju4/pub?w=400
   :alt: 

See `RSoc Community Page <https://github.com/hupili/snsapi/wiki/Rsoc>`__
if you are interested.

Supported Platforms
-------------------

Enther the interactive shell by ``python -i snscli.py``. Get the
supported platforms as follows:

::

    Supported platforms:
       * Email
       * FacebookFeed
       * RSS
       * RSS2RW
       * RSSSummary
       * RenrenBlog
       * RenrenFeed
       * RenrenPhoto
       * RenrenShare
       * RenrenStatus
       * RenrenStatusDirect
       * SQLite
       * SinaWeiboBase
       * SinaWeiboStatus
       * SinaWeiboWapStatus
       * TencentWeiboStatus
       * TwitterStatus
       * ...

More platforms are coming! Please join us!

Get Started
-----------

-  Clone and install dependencies via ``pip``. Then you are ready to go.
   See `installation
   guide <https://github.com/hupili/snsapi/wiki/Installation>`__ if you
   need more detailed information. See
   `troubleshooting <https://github.com/hupili/snsapi/wiki/Troubleshooting>`__
   page if you encounter problems in your initial tests.
-  We have several `demo
   apps <https://github.com/hupili/snsapi/tree/master/app>`__ in this
   repo. You can start with them and see how to use those classes of
   SNSAPI.
-  Users who don't want to write Python or other non-Python programmers
   can start with our command-line-interface (``snscli.py``). `The
   official SNSAPI website <http://snsapi.ie.cuhk.edu.hk/>`__ should get
   your started quickly along this line. This CLI can allow interfacing
   with other languages using STDIN/ STDOUT.
-  Users who are not comfortable with CLI can use the
   graphical-user-interface (``snsgui.py``). See `more user
   interfaces <https://github.com/hupili/snsapi/wiki/End-user-interfaces>`__.

Resources
---------

-  `SNSApi Website <http://snsapi.ie.cuhk.edu.hk/>`__: maintained by
   `@hupili <https://github.com/hupili/>`__; welcome to report problems
   to admin, or send pull request to `website
   repo <https://github.com/hupili/snsapi-website>`__ directly.
-  `SNSApi Website (CN) <http://snsapi.sinaapp.com/>`__: maintained by
   `@xuanqinanhai <https://github.com/xuanqinanhai>`__.
-  `SNSApi doc <https://snsapi.readthedocs.org/en/latest/>`__:
   automatically generated from code using Sphinx; also available as
   inline doc using ``help(XXX)`` from Python shell.
-  `SNSApi Github Wiki <https://github.com/hupili/snsapi/wiki>`__:
   editable by all GitHub users; welcome to share your experience.
-  `SNSApi Google
   Group <https://groups.google.com/forum/?fromgroups#!forum/snsapi>`__:
   The most efficient way to get help, discuss new ideas and organize
   community activities. Please join us!

License
-------

|copyleft|

All materials of this project are released to public domain, except for
the followings:

-  ``snsapi/third/*``: The third party modules. Please refer to their
   original LICENSE. We have pointers in ``snsapi/third/README.md`` for
   those third party modules.

Other
-----

-  Old version of this readme `in
   Chinese <https://github.com/hupili/snsapi/blob/master/doc/snsapi-old-readme-cn.md>`__

Build Status
------------

-  master: |master|
-  dev: |dev|

.. |copyleft| image:: http://unlicense.org/pd-icon.png
   :target: http://unlicense.org
.. |master| image:: https://travis-ci.org/hupili/snsapi.png?branch=master
.. |dev| image:: https://travis-ci.org/hupili/snsapi.png?branch=dev
