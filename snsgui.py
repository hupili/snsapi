#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# snsgui.py
# a simple gui for snsapi using Tkinter
#
# Author: Alex.wang
# Create: 2013-02-11 15:51


import Tkinter
import tkMessageBox
import tkSimpleDialog
import webbrowser
from snsapi.snspocket import SNSPocket
from snsapi.snstype import Message
from snsapi.utils import utc2str


# supported platform
EMAIL = 'Email' # gmail only
RSS = 'RSS'
RSS_RW = 'RSS2RW'
RENREN_SHARE = 'RenrenShare'
RENREN_STATUS = 'RenrenStatus'
SQLITE = 'SQLite'
SINA_WEIBO = 'SinaWeiboStatus'
TENCENT_WEIBO = 'TencentWeiboStatus'
TWITTER = 'TwitterStatus'


TITLE = 'snsapi'


sp = SNSPocket()
gui = None


class NewChannel(tkSimpleDialog.Dialog):
    '''Dialog to create new Channel'''
    def __init__(self, master, platform):
        self.platform = platform
        tkSimpleDialog.Dialog.__init__(self, master, 'Add %s Channel' % platform)
    def body(self, master):
        row = 0

        self.channel_name = Tkinter.StringVar(master)
        Tkinter.Label(master, text = 'Channel Name:').grid(row = row, column = 0, sticky = Tkinter.E)
        channelEntry = Tkinter.Entry(master, textvariable = self.channel_name).grid(row = row, column = 1)
        row += 1

        if self.platform in (RENREN_SHARE, RENREN_STATUS, SINA_WEIBO, TENCENT_WEIBO, TWITTER):
            self.app_key = Tkinter.StringVar(master)
            Tkinter.Label(master, text = 'App Key:').grid(row = row, column = 0, sticky = Tkinter.E)
            Tkinter.Entry(master, textvariable = self.app_key).grid(row = row, column = 1)
            row += 1

            self.app_secret = Tkinter.StringVar(master)
            Tkinter.Label(master, text = 'App Secret:').grid(row = row, column = 0, sticky = Tkinter.E)
            Tkinter.Entry(master, textvariable = self.app_secret).grid(row = row, column = 1)
            row += 1

        if self.platform in (EMAIL, RSS_RW, SQLITE):
            self.username = Tkinter.StringVar(master)
            Tkinter.Label(master, text = 'User Name:').grid(row = row, column = 0, sticky = Tkinter.E)
            Tkinter.Entry(master, textvariable = self.username).grid(row = row, column = 1)
            row += 1

        if self.platform in (EMAIL, ):
            self.password = Tkinter.StringVar(master)
            Tkinter.Label(master, text = 'Password:').grid(row = row, column = 0, sticky = Tkinter.E)
            Tkinter.Entry(master, textvariable = self.password).grid(row = row, column = 1)
            row += 1

        if self.platform in (TWITTER, ):
            self.access_key = Tkinter.StringVar(master)
            Tkinter.Label(master, text = 'Access Key:').grid(row = row, column = 0, sticky = Tkinter.E)
            Tkinter.Entry(master, textvariable = self.access_key).grid(row = row, column = 1)
            row += 1

            self.access_secret = Tkinter.StringVar(master)
            Tkinter.Label(master, text = 'Access Secret:').grid(row = row, column = 0, sticky = Tkinter.E)
            Tkinter.Entry(master, textvariable = self.access_secret).grid(row = row, column = 1)
            row += 1

        if self.platform in (RSS, RSS_RW, SQLITE):
            self.url = Tkinter.StringVar(master)
            Tkinter.Label(master, text = 'Url:').grid(row = row, column = 0, sticky = Tkinter.E)
            Tkinter.Entry(master, textvariable = self.url).grid(row = row, column = 1)
            row += 1

        return channelEntry

    def validate(self):
        if not self.channel_name.get():
            return False

        if self.platform in (RENREN_SHARE, RENREN_STATUS, SINA_WEIBO, TENCENT_WEIBO, TWITTER):
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

        if self.platform in (RSS, RSS_RW, SQLITE):
            if not self.url.get():
                return False

        return True

    def apply(self):
        channel = sp.new_channel(self.platform)
        channel['channel_name'] = self.channel_name.get()

        # app_key and app_secret
        if self.platform in (RENREN_SHARE, RENREN_STATUS, SINA_WEIBO, TENCENT_WEIBO, TWITTER):
            channel['app_key'] = self.app_key.get()
            channel['app_secret'] = self.app_secret.get()

        # username is optional for sqlite
        if self.platform == SQLITE and self.username.get():
            channel['username'] = self.username.get()

        if self.platform == RSS_RW:
            channel['author'] = self.username.get()

        if self.platform == EMAIL:
            channel['username'] = self.username.get()
            channel['address'] = '%s@gmail.com' % self.username.get()

        # password
        if self.platform in (EMAIL, ):
            channel['password'] = self.password.get()

        # access_key and access_secret
        if self.platform in (TWITTER, ):
            channel['access_key'] = self.access_key.get()
            channel['access_secret'] = self.access_secret.get()

        # url
        if self.platform in (RSS, RSS_RW, SQLITE):
            channel['url'] = self.url.get()

        self.result = channel


class StatusList(Tkinter.Text):
    '''Text widget to show status'''
    def __init__(self, master):
        self.allStatus = []
        Tkinter.Text.__init__(self, master, width = 50, height = 27, relief = Tkinter.FLAT)
        self.__misc()
        self.show_status(5)
    def __misc(self):
        # common used tags
        self.tag_config('link', foreground = "blue", underline = 1)
        self.tag_config('text', justify = Tkinter.LEFT)
        self.tag_config('username', foreground = '#885a62')
        self.tag_config('time', foreground = '#cf9e8b')
        self.tag_config('other', foreground = '#808080')

        # `Show More button'
        self.tag_config('center', justify = Tkinter.CENTER)
        self.tag_config('top', foreground = 'gray', spacing1 = 5, spacing3 = 5)
        self.tag_bind('top', '<Button-1>', self.top_more)
        self.tag_config('bottom', foreground = 'gray', spacing1 = 5, spacing3 = 5)
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
        if data.has_key('link'):
            self.insert(mark_end, text, (tag_text, 'link'))
            self.tag_bind(tag_text, '<Button-1>', lambda e, link = data.link: webbrowser.open(link))
        else:
            self.insert(mark_end, text, 'text')
        self.insert(mark_end, '\n', 'text')

        self.configure(state = Tkinter.DISABLED)

    def insert_status(self, status):
        if status in self.allStatus: return

        self.allStatus.append(status)
        self.allStatus.sort(key = lambda v: v.parsed.time, reverse = True)
        self.__insert_status(self.allStatus.index(status), status)

    def show_status(self, n):
        '''show N status'''
        for s in sp.home_timeline(n):
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

    def post_status(self):
        if not self.channel:
            tkMessageBox.showwarning(TITLE, 'switch to a channel first')
            return
        if sp[self.channel].platform == RSS:
            tkMessageBox.showwarning(TITLE, 'cannot post to RSS channel')
            return
        # TODO
        pass


def main():
    global gui
    root = Tkinter.Tk()
    gui = SNSGui(root)
    gui.pack(expand = True, fill = Tkinter.BOTH)
    root.title(TITLE)
    root.mainloop()


if __name__ == '__main__':
    main()

