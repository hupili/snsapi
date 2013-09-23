#!/usr/bin/env python
# -*- coding: utf-8 -*-

from snsapi.utils import console_output, console_input
from snsapi.snspocket import SNSPocket
from snsapi.snslog import SNSLog as logger

sp = SNSPocket()

import functools

def convert_parameter_to_unicode(func):
    '''
    Decorator to convert parameters to unicode if they are str

       * We use unicode inside SNSAPI.
       * If one str argument is found, we assume it is from console
         and convert it to unicode.

    This can solve for example:

       * The 'text' arg you give to ``update`` is not unicode.
       * You channel name contains non-ascii character, and you
         use ``ht(channel='xxx')`` to get the timeline.
    '''
    def to_unicode(s):
        if isinstance(s, str):
            return console_input(s)
        else:
            return s
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        new_args = map(lambda x: to_unicode(x), args)
        new_kwargs = dict(map(lambda x: (x[0], to_unicode(x[1])), kwargs.items()))
        return func(*new_args, **new_kwargs)
    return wrapper

# Shortcuts for you to operate in Python interactive shell

lc = load_config = sp.load_config
sc = save_config =  sp.save_config
lsc = list_channel =  sp.list_channel
lsp = list_platform =  sp.list_platform
newc = new_channel = sp.new_channel
addc = add_channel = sp.add_channel
clc = clear_channel = sp.clear_channel
auth = sp.auth
ht = home_timeline = convert_parameter_to_unicode(sp.home_timeline)
up = update = convert_parameter_to_unicode(sp.update)
re = reply = convert_parameter_to_unicode(sp.reply)
fwd = forward = convert_parameter_to_unicode(sp.forward)

#==== documentation ====

helpdoc = \
"""
snscli -- the interactive CLI to operate all SNS!

Type "print helpdoc" again to see this document.

To start your new journey, type "print tut"

Here's the command list:
   * load_config
   * save_config
   * list
   * auth
   * home_timeline
   * update
   * reply
   * new_channel
"""

class SNSAPITutorial(object):
    """docstring for SNSAPITutorial"""
    def __init__(self):
        super(SNSAPITutorial, self).__init__()
        self.pointer = -1
        self.sections = []

        self.sections.append("""
Section 0. Introduction

    This tutorial will present the basics of
    SNSAPI to you. We'll walk you through
    configuring, authorising, reading timeline,
    updating status, replying to one status, etc.

    To navigate this tutorial, you need:
    >>> tut.next() # move to next section
    >>> tut.prev() # move to previous section

    Note that "print tut" is the shortcut
    to move to the next section.

    The tutorial will loop around after it hits
    the last section.
        """)

        self.sections.append("""
Section 1. Help and Principles

    Type "print helpdoc" whenever you forget commands.

    Note that those commands are essentially Python
    functions derived from SNSPocket class. You
    can use the normal way to invoke them and seek
    for online documentation.

    e.g.
        Type "list_channel()" to list the current
        channels.

    e.g.
        Type "help(sp.list_channel)" to see the
        detailed description of parameters.
        """)

        self.sections.append("""
Section 2. Create Your First Channel

    Type:
    >>> nc = new_channel()
    >>> print nc

    See the template we created for you. Now fill in
    information using standard Python assignment.

    e.g.
    >>> nc["channel_name"] = "test_rss"

    We subscribe the RSS feed of SNSAPI wiki pages.
    Configure accordingly, and add this channel:
    >>> nc["channel_name"] = "test_rss"
    >>> nc["url"] = "https://github.com/hupili/snsapi/wiki.atom"
    >>> nc["platform"] = "RSS"
    >>> add_channel(nc)

    You can use "list_channel()" to check it.

    You can use "list_platform()" to see what are the currently
    supported platforms.
        """)

        self.sections.append("""
Section 3. Read Your Timeline

    Type:
    >>> sl = home_timeline()
    >>> print sl

    You can read the news feeds of SNSAPI wiki pages now.
    In order to expose the same interface as other platforms,
    only a subset of the information is formatted. e.g.
    publish date, author, title, and link.

    The basic function of SNSAPI is to unify the interface.
    You can expect to call home_timeline() on any other
    platforms (most of them). The returned object is a list.
    You can of course inspect it using "print sl[0]",
    "print len(sl)".
        """)

        self.sections.append("""
Section 4. Load, Save Configuration

    Try:
    >>> save_config()

    You can "quit()" and invoke this CLI again. Use
    "load_config()" to recover the channels you've just
    configured. To let this tutorial continue, we try to
    clear channels and load them from file.

    Try:
    >>> list_channel()
    >>> clear_channel()
    >>> list_channel()
    >>> load_config()
    >>> list_channel()

    You don't have problem figuring out what's going on
    by looking at the console output.
        """)

        self.sections.append("""
Section 5. Configure one "Real" SNS (OSN)

    The RSS channel just gives you a flavour of how SNSAPI
    works. It requires the minimum operation. In this section,
    we'll configure one Renren channel and update/reply
    status using SNSAPI. You have to spend some time applying
    for an app key.

    See our wiki page if you haven't done so or you need
    troubleshooting assistance:
        https://github.com/hupili/snsapi/wiki/Apply-for-app-key

    Try:
    >>> clear_channel()
    >>> nc = new_channel()
    >>> nc["platform"] = "RenrenStatus"
    >>> nc["app_secret"] = "YOU_APP_SECRET_KEY"
    >>> nc["app_key"] = "YOU_APP_KEY"
    >>> nc["channel_name"] = "test_renren"
    >>> nc["auth_info"]["callback_url"] = "http://snsapi.sinaapp.com/auth.php"
    >>> add_channel(nc)
    >>> auth()
    >>> sl = home_timeline(count = 5)
    >>> print sl

    In the auth stage, you will be prompt a browser for
    authorization by default. After authorizing your own
    App, you can copy the url which contains authorization
    code to snscli console. If you use the above defaults,
    we should be able to guide you through the process at
    every step. Check wether you get 5 statuses from
    your home timeline.
        """)

        self.sections.append("""
Section 6. Update and Reply on SNS

    Try update your own status:
    >>> update("t.....")
    >>> sl = home_timeline(count = 5)
    >>> print sl[0]

    If the return value is "True", then we successfully updated
    one status. We can get the status using home_timeline().
    Check if this is the message you just post.

    Now we reply to it:
    >>> reply(sl[0].ID, "a reply")

    Again, you'll see "True" on successful reply. You can
    login the web portal of this SNS and check whether it
    is successful.
        """)

        self.sections.append("""
Section 7. Cross Channel Operation

    Let's do something advanced. First configure one OSN
    channel as is done in the last two sections. Then
    configure one RSS2RW channel. You can write feeds using
    RSS2RW channel. Here's the basic settings:

    >>> n["platform"] = "RSS2RW"
    >>> n["channel_name"] = "output"
    >>> n["url"] = "output.atom"
    >>> add_channel(n)
    >>> list_channel()

    Let's read the statuses from OSN and write some of
    them to an RSS2 feed:

    >>> sl = home_timeline(5)
    >>> print sl[0]
    >>> print home_timeline(channel = "output")
    >>> update(text = unicode(sl[0]), channel = "output")
    >>> print home_timeline(channel = "output")
    >>> update(text = unicode(sl[3]), channel = "output")
    >>> print home_timeline(channel = "output")

    Besides the console output, you can also check the
    resuling "output.atom" file. It is a valid RSS file
    so you can subscribe to it using RSS Readers. Note
    how simple this task is! It's a totally different
    thing from OSN, but you can use the same "update()"
    method to put information there!
        """)

        self.sections.append("""
Section 8. Advanced Use Case

    Congratulations! You have grasped all basics of SNSAPI.
    Feeling interested? Um, let's look at one more complex
    idea:
       * Follow (being friends with) different users on
       different platforms.
       * Use SNSAPI to pull all the new information.
       * Classifying, filtering, etc. Whatever you like.
       * Output those valuable statuses to one single
       RSS file.
       * Subscribe to that feed alone! You can get all
       information in just one place.
       * Take a step further. You can use ifttt.com to
       forward the RSS to your cell phone by SMS for free!

    Think wild. We are standing on top of different platforms
    (and there will definitely be more). Let's make all
    the things to work for us.
        """)

        self.sections.append("""
Section 9. Programming Interface

    Don't know Python?
    It's absolutely OK!

    We intend to use STDIN/STDOUT to communicate with
    all other languages. (of course, Python programmers
    will find it more convenient to use the class directly)

    e.g.
        echo -e 'load_config()\\nauth()\\nprint home_timeline(5)\\nquit()' | python -i snscli.py

    You can use the above line to get home timeline from
    bash. You can deal with it using grep, awk, etc. Same
    to all other programming laguages: write command to
    STDIN and read result from STDOUT. You may have noticed
    that the console output is not clean. Writing logs to
    a file will make it much better. Check out the next
    and the last section for pointers.
        """)

        self.sections.append("""
Section 10. Closing Remarks

    Here's a few pointers to proceed next:
       * Check out our wiki for more advanced use cases.
       * Check "snsapi/snsconf.py" for some hardcoded
       but tunable configurations. (e.g. those of logging)
       * Check "snsapi/app" for some sample apps.
       * Look at the codes, write plugins, write Apps, etc.

    Enjoy!

    The next time you type "print tut", we'll start
    all over again~
        """)

    def next(self):
        self.pointer += 1
        tut = self.sections[self.pointer % len(self.sections)]
        console_output(tut)

    def prev(self):
        self.pointer -= 1
        tut = self.sections[self.pointer % len(self.sections)]
        console_output(tut)

    def __str__(self):
        self.pointer += 1
        tut = self.sections[self.pointer % len(self.sections)]
        return tut

tut = SNSAPITutorial()


if __name__ == '__main__':
    #==== default initialization one may like ====
    print helpdoc
    load_config()
    list_channel()
    auth()

    logger.info("Ready to drop into the interactive shell of SNSCLI!")
    import code
    code.interact(local=locals())
