#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# snsgui.py
# a simple gui for snsapi using Tkinter
#
# Author: Alex.wang
# Create: 2013-02-11 15:51


'''
# snsgui - a simple gui for snsapi using Tkinter


Usage
-----

* Press '+' button to add a sns channel.
* Press the Button before '+' to switch channel.
* Click 'Show More' in gray.
* Press 'Post' button to post new Status to current channel.


Theme Config
------------

* open conf/snsgui.ini
* find [theme] section and copy it
* custom your theme, change the value in the copied section
* name your theme, change [theme] to [THEME NAME]
* apply your theme, change 'theme' value in [snsapi] section to your theme name


Add Email Provider
------------------

* open conf/snsgui.ini
* find [Gmail] section and copy it
* change the value in the copied section
* name it, change [Gmail] to [EMAIL_ID]
* add it, add a 'EMAIL_ID = true' line in [email] section
'''


import Tkinter
import tkMessageBox
import tkSimpleDialog
import webbrowser
from ConfigParser import ConfigParser
import os

import snsapi
from snsapi.snspocket import SNSPocket
from snsapi.utils import utc2str


# supported platform
EMAIL = 'Email'
RSS = 'RSS'
RSS_RW = 'RSS2RW'
RSS_SUMMARY = 'RSSSummary'
RENREN_BLOG = 'RenrenBlog'
RENREN_SHARE = 'RenrenShare'
RENREN_STATUS = 'RenrenStatus'
SQLITE = 'SQLite'
SINA_WEIBO = 'SinaWeiboStatus'
TENCENT_WEIBO = 'TencentWeiboStatus'
TWITTER = 'TwitterStatus'


TITLE = 'snsapi'
CONFILE = os.path.join(snsapi._dir_static_data, 'snsgui.ini')


sp = SNSPocket()
gui = None
config = None


class SNSGuiConfig(ConfigParser):
    def __init__(self):
        ConfigParser.__init__(self)
        self.optionxform = str
        self.read(CONFILE)
        self.theme = self.get('snsgui', 'theme')
    def getcolor(self, option):
        return self.get(self.theme, option)
    def email(self):
        '''get supported email platforms'''
        return self.options('email')
    def getmail(self, option):
        '''get mail config dict'''
        d = {}
        for key, value in self.items(option):
            d[key] = value
        return d


class NewChannel(tkSimpleDialog.Dialog):
    '''Dialog to create new Channel'''
    def __init__(self, master, platform):
        self.platform = platform
        tkSimpleDialog.Dialog.__init__(self, master, 'Add %s Channel' % platform)
    def textField(self, master, row, label, id, init = ''):
        var = Tkinter.StringVar(master, init)
        setattr(self, id, var)
        Tkinter.Label(master, text = label).grid(row = row, column = 0, sticky = Tkinter.E)
        Tkinter.Entry(master, textvariable = var).grid(row = row, column = 1, sticky = Tkinter.NSEW)
        return row + 1
    def body(self, master):
        row = self.textField(master, 0, 'Channel Name:', 'channel_name')

        if self.platform in (RENREN_BLOG, RENREN_SHARE, RENREN_STATUS, SINA_WEIBO, TENCENT_WEIBO, TWITTER):
            row = self.textField(master, row, 'App Key:', 'app_key')
            row = self.textField(master, row, 'App Secret:', 'app_secret')

        if self.platform == EMAIL:
            items = config.email()
            self.email = Tkinter.StringVar(master, items[0])
            Tkinter.Label(master, text = 'Email:').grid(row = row, column = 0, sticky = Tkinter.E)
            Tkinter.OptionMenu(master, self.email, *items).grid(row = row, column = 1, sticky = Tkinter.NSEW)
            row += 1

        if self.platform in (EMAIL, RSS_RW, SQLITE):
            row = self.textField(master, row, 'User Name:', 'username')

        if self.platform in (EMAIL, ):
            row = self.textField(master, row, 'Password:', 'password')

        if self.platform in (TWITTER, ):
            row = self.textField(master, row, 'Access Key:', 'access_key')
            row = self.textField(master, row, 'Access Secret:', 'access_secret')

        if self.platform in (RSS, RSS_RW, RSS_SUMMARY, SQLITE):
            row = self.textField(master, row, 'Url:', 'url')

        if self.platform in (RENREN_BLOG, RENREN_SHARE, RENREN_STATUS, SINA_WEIBO, TENCENT_WEIBO):
            auth_info = Tkinter.LabelFrame(master, text = 'Auth info')

            self.textField(auth_info, 0, 'Callback Url:', 'callback_url')
            self.textField(auth_info, 1, 'Cmd Request Url:', 'cmd_request_url', '(default)')
            self.textField(auth_info, 2, 'Cmd Fetch Code:', 'cmd_fetch_code', '(default)')
            self.textField(auth_info, 3, 'Save Token File:', 'save_token_file', '(default)')

            auth_info.grid(row = row, column = 0, columnspan = 2)
            row += 1

    def validate(self):
        if not self.channel_name.get():
            return False

        if self.platform in (RENREN_BLOG, RENREN_SHARE, RENREN_STATUS, SINA_WEIBO, TENCENT_WEIBO, TWITTER):
            if not self.app_key.get() or not self.app_secret.get():
                return False

        if self.platform in (EMAIL, RSS_RW):
            if not self.username.get():
                return False

        if self.platform in (EMAIL, ):
            if not self.password.get():
                return False

        if self.platform in (TWITTER, ):
            if not self.access_key.get() or not self.access_secret.get():
                return False

        if self.platform in (RSS, RSS_RW, RSS_SUMMARY, SQLITE):
            if not self.url.get():
                return False

        if self.platform in (RENREN_BLOG, RENREN_SHARE, RENREN_STATUS, SINA_WEIBO, TENCENT_WEIBO):
            if not self.callback_url.get() or not self.cmd_request_url.get() or not self.cmd_fetch_code.get() or not self.save_token_file.get():
                return False

        return True

    def apply(self):
        channel = sp.new_channel(self.platform)
        channel['channel_name'] = self.channel_name.get()

        # app_key and app_secret
        if self.platform in (RENREN_BLOG, RENREN_SHARE, RENREN_STATUS, SINA_WEIBO, TENCENT_WEIBO, TWITTER):
            channel['app_key'] = self.app_key.get()
            channel['app_secret'] = self.app_secret.get()

        # username is optional for sqlite
        if self.platform == SQLITE and self.username.get():
            channel['username'] = self.username.get()

        if self.platform == RSS_RW:
            channel['author'] = self.username.get()

        if self.platform == EMAIL:
            channel['username'] = self.username.get()
            mail = config.getmail(self.email.get())
            channel['imap_host'] = mail['imap_host']
            channel['imap_port'] = int(mail['imap_port'])
            channel['smtp_host'] = mail['smtp_host']
            channel['smtp_port'] = int(mail['smtp_port'])
            channel['address'] = '%s@%s' % (self.username.get(), mail['domain'])

        # password
        if self.platform in (EMAIL, ):
            channel['password'] = self.password.get()

        # access_key and access_secret
        if self.platform in (TWITTER, ):
            channel['access_key'] = self.access_key.get()
            channel['access_secret'] = self.access_secret.get()

        # url
        if self.platform in (RSS, RSS_RW, RSS_SUMMARY, SQLITE):
            channel['url'] = self.url.get()

        # auth_info
        if self.platform in (RENREN_BLOG, RENREN_SHARE, RENREN_STATUS, SINA_WEIBO, TENCENT_WEIBO):
            channel['auth_info']['callback_url'] = self.callback_url.get()
            channel['auth_info']['cmd_request_url'] = self.cmd_request_url.get()
            channel['auth_info']['cmd_fetch_code'] = self.cmd_fetch_code.get()
            channel['auth_info']['save_token_file'] = self.save_token_file.get()

        self.result = channel


class TextDialog(tkSimpleDialog.Dialog):
    '''a general text input box'''
    def __init__(self, master, title, init_text = ''):
        self.init_text = init_text
        tkSimpleDialog.Dialog.__init__(self, master, title)

    def destroy(self):
        self.textWidget.unbind('<Return>', self.bind_id)
        tkSimpleDialog.Dialog.destroy(self)

    def body(self, master):
        self.textWidget = Tkinter.Text(master, width = 50, height = 6)
        self.bind_id = self.textWidget.bind('<Return>', self.enter_key)
        self.textWidget.insert('1.0', self.init_text)
        self.textWidget.pack(expand = True, fill = Tkinter.BOTH)

        return self.textWidget

    def enter_key(self, event):
        self.textWidget.insert(Tkinter.END, '\n')

        # this will stop further bound function, e.g. `OK' button
        return 'break'

    def get_text(self):
        text = ''
        for key, value, index in self.textWidget.dump('1.0', Tkinter.END, text = True):
            text += value
        return text.rstrip()

    def validate(self):
        if not self.get_text():
            return False

        return True

    def apply(self):
        self.result = self.get_text()


class StatusList(Tkinter.Text):
    '''Text widget to show status'''
    def __init__(self, master):
        self.allStatus = []
        Tkinter.Text.__init__(self, master, width = 50, height = 27, relief = Tkinter.FLAT)
        self.__misc()
        for s in sp.home_timeline(5):
            self.insert_status(s)

    def __misc(self):
        # common used tags
        self.tag_config('link', foreground = config.getcolor('link'), underline = 1)
        self.tag_config('text', justify = Tkinter.LEFT)
        self.tag_config('username', foreground = config.getcolor('username'))
        self.tag_config('time', foreground = config.getcolor('time'))
        self.tag_config('other', foreground = config.getcolor('other'))
        self.tag_config('right', justify = Tkinter.RIGHT)

        # `Show More button'
        self.tag_config('center', justify = Tkinter.CENTER)
        self.tag_config('top', foreground = config.getcolor('more'), spacing1 = 5, spacing3 = 5)
        self.tag_bind('top', '<Button-1>', self.top_more)
        self.tag_config('bottom', foreground = config.getcolor('more'), spacing1 = 5, spacing3 = 5)
        self.tag_bind('bottom', '<Button-1>', self.bottom_more)

        self.mark_set('start', '1.0')
        self.mark_gravity('start', Tkinter.LEFT)
        self.mark_set('head', '1.0')
        self.insert('start', 'Show More\n', ('top', 'center'))
        self.mark_gravity('head', Tkinter.LEFT)

        self.mark_set('stop', Tkinter.END)
        self.mark_set('tail', Tkinter.END)
        self.mark_gravity('tail', Tkinter.LEFT)
        self.insert('stop', 'Show More\n', ('bottom', 'center'))
        self.mark_gravity('tail', Tkinter.RIGHT)

    @staticmethod
    def get_mark(status):
        '''get status mark id'''
        return 's#%08x' % id(status)

    def __insert_status(self, index, status):
        '''insert status to Text widget'''
        self.configure(state = Tkinter.NORMAL)

        mark = self.get_mark(status)
        mark_start = mark + '.start'
        mark_end = mark + '.end'
        tag_text = mark + '.text'
        tag_link = mark + '.link'
        tag_forward = mark + '.forward'
        tag_reply = mark + '.reply'
        self.tag_config(tag_forward, foreground = config.getcolor('button'))
        self.tag_config(tag_reply, foreground = config.getcolor('button'))
        self.tag_config(tag_text, borderwidth = 0)
        if index == 0:
            anchor = 'head'
        else:
            anchor = self.get_mark(self.allStatus[index - 1]) + '.end'
        self.mark_set(mark_start, anchor)
        self.mark_gravity(mark_start, Tkinter.LEFT)
        self.mark_set(mark_end, anchor)

        data = status.parsed
        self.insert(mark_end, data.username, ('text', 'username'))
        self.insert(mark_end, ' at ', ('text', 'other'))
        self.insert(mark_end, utc2str(data.time), ('text', 'time'))
        self.insert(mark_end, '\n  ', ('text', 'other'))
        try:
            text = data.title
        except:
            text = data.text
        self.insert(mark_end, text, 'text')
        if data.has_key('link'):
            self.insert(mark_end, '[link]', (tag_link, 'link'))
            self.tag_bind(tag_link, '<Button-1>', lambda e, link = data.link: webbrowser.open(link))
        self.insert(mark_end, '\n', 'text')

        # action buttons
        self.insert(mark_end, 'forward', (tag_forward, 'right'))
        self.tag_bind(tag_forward, '<Button-1>', lambda e, status = status: gui.forward_status(status))
        self.insert(mark_end, ' | ', ('text', 'other'))
        self.insert(mark_end, 'reply', (tag_reply, 'right'))
        self.tag_bind(tag_reply, '<Button-1>', lambda e, status = status: gui.reply_status(status))
        self.insert(mark_end, ' \n', 'text')

        self.configure(state = Tkinter.DISABLED)

    def insert_status(self, status):
        if status in self.allStatus: return

        self.allStatus.append(status)
        self.allStatus.sort(key = lambda v: v.parsed.time, reverse = True)
        self.__insert_status(self.allStatus.index(status), status)

    def show_status(self, n):
        '''show N status'''
        for s in sp.home_timeline(n, gui.channel):
            self.insert_status(s)

    def top_more(self, event):
        self.show_status(1)

    def bottom_more(self, event):
        n = len(self.allStatus) / len(sp) + 2
        self.show_status(n)


class SNSGui(Tkinter.Frame):
    # check snsapi.platform.platform_list
    PLATFORMS = {
        'email': EMAIL,
        'rss': RSS,
        'rss rw': RSS_RW,
        'rss summary': RSS_SUMMARY,
        'renren blog': RENREN_BLOG,
        'renren share': RENREN_SHARE,
        'renren status': RENREN_STATUS,
        'sqlite': SQLITE,
        'sina weibo': SINA_WEIBO,
        'tencent weibo': TENCENT_WEIBO,
        'twitter': TWITTER,
    }
    def __init__(self, master):
        self.channel = None
        sp.load_config()
        sp.auth()

        Tkinter.Frame.__init__(self, master)
        self.__menus()
        self.__widgets()

    def destroy(self):
        sp.save_config()
        Tkinter.Frame.destroy(self)

    def __menus(self):
        self.channelListMenu = Tkinter.Menu(self, tearoff = False)
        self.channelListMenu.add_command(label = 'All', command = lambda: self.switch_channel(None))
        if len(sp): self.channelListMenu.add_separator()
        for cname in sp.iterkeys():
            self.channelListMenu.add_command(label = cname, command = lambda channel = cname: self.switch_channel(channel))

        self.channelTypeMenu = Tkinter.Menu(self, tearoff = False)
        self.channelTypeMenu.add_separator()
        for label in self.PLATFORMS.iterkeys():
            self.channelTypeMenu.add_command(label = label, command = lambda platform = label: self.add_channel(platform))

        self.moreMenu = Tkinter.Menu(self, tearoff = False)
        self.moreMenu.add_separator()
        self.moreMenu.add_command(label = 'Help', command = self.show_help)
        self.moreMenu.add_command(label = 'About', command = self.show_about)

    def __widgets(self):
        self.topFrame = Tkinter.LabelFrame(self, text = 'Channel')
        self.channelButton = Tkinter.Button(self.topFrame, text = 'All', command = lambda: self.channelListMenu.post(*self.winfo_pointerxy()))
        self.addChannelButton = Tkinter.Button(self.topFrame, text = '+', command = lambda: self.channelTypeMenu.post(*self.winfo_pointerxy()))
        self.postButton = Tkinter.Button(self.topFrame, text = 'Post', command = self.post_status)
        self.moreButton = Tkinter.Button(self.topFrame, text = '...', command = lambda: self.moreMenu.post(*self.winfo_pointerxy()))

        self.topFrame.grid_columnconfigure(2, weight = 1)
        self.channelButton.grid(row = 0, column = 0)
        self.addChannelButton.grid(row = 0, column = 1)
        self.postButton.grid(row = 0, column = 3)
        self.moreButton.grid(row = 0, column = 4)

        self.statusFrame = Tkinter.LabelFrame(self, text = 'Status')
        self.statusList = StatusList(self.statusFrame)
        self.scrollbar = Tkinter.Scrollbar(self.statusFrame, command = self.statusList.yview)
        self.statusList.configure(yscrollcommand = self.scrollbar.set)

        self.statusFrame.grid_rowconfigure(0, weight = 1)
        self.statusFrame.grid_columnconfigure(0, weight = 1)
        self.statusList.grid(row = 0, column = 0, sticky = Tkinter.NSEW)
        self.scrollbar.grid(row = 0, column = 1, sticky = Tkinter.NS)

        self.grid_rowconfigure(1, weight = 1, minsize = 200)
        self.grid_columnconfigure(0, weight = 1, minsize = 200)
        self.topFrame.grid(row = 0, column = 0, sticky = Tkinter.EW)
        self.statusFrame.grid(row = 1, column = 0, sticky = Tkinter.NSEW)

    def show_help(self):
        tkMessageBox.showinfo('Help - ' + TITLE, '''Glossary:
Channel: where Status come from and post to.

Usage:
 * Press `+' button to add a sns channel.
 * Press the Button before `+' to switch channel.
 * Click `Show More' in gray.
 * Press `Post' button to post new Status to current channel.
''')

    def show_about(self):
        tkMessageBox.showinfo('About - ' + TITLE, '''a Tkinter GUI for snsapi

by Alex.wang(iptux7#gmail.com)''')

    def switch_channel(self, channel):
        if self.channel == channel:
            return

        if channel:
            sp.auth(channel)
        cname = channel or 'All'
        self.channel = channel
        self.channelButton.configure(text = cname)

    def add_channel(self, platform):
        channel = NewChannel(self, self.PLATFORMS[platform]).result
        if not channel:
            return

        sp.add_channel(channel)
        if len(sp) == 1: self.channelListMenu.add_separator()
        cname = channel['channel_name']
        self.channelListMenu.add_command(label = cname, command = lambda channel = cname: self.switch_channel(channel))

    def get_post_text(self, title, init_text = ''):
        if not self.channel:
            tkMessageBox.showwarning(TITLE, 'switch to a channel first')
            return
        if sp[self.channel].platform in (RSS, RSS_SUMMARY):
            tkMessageBox.showwarning(TITLE, 'cannot post to RSS channel')
            return

        return TextDialog(self, title, init_text).result

    def post_status(self):
        text = self.get_post_text('Post to channel %s' % self.channel)
        if text:
            sp[self.channel].update(text)

    def reply_status(self, status):
        text = self.get_post_text('Reply to This Status')
        if text:
            sp[status.ID.channel].reply(status.ID, text)

    def forward_status(self, status):
        text = self.get_post_text('Forward Status to %s' % self.channel, 'forward')
        if text:
            sp[self.channel].forward(status, text)


def main():
    global gui, config
    config = SNSGuiConfig()
    root = Tkinter.Tk()
    gui = SNSGui(root)
    gui.pack(expand = True, fill = Tkinter.BOTH)
    root.title(TITLE)
    root.mainloop()


if __name__ == '__main__':
    main()


