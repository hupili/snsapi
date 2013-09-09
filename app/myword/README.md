myword
====

Introduction
----

myword is a demo app modified from mysofa
myword reads the timeline and check if someone "at" him.
If someone "at" myword with a word, it will reply the message with the word's translation.
                                    ---hzhua 2013.2.25
															
Dictionary API is provided by "dic.zhan-dui.com"

Steps:
----

1.Please fill in your app_key and app_secret in conf/channel.json. (You can read the introduction in demo mysofa for help)

2.Replace MY_NAME in myword.py with your own user name

3.(Optional) Change REPLY_GAP as your will. REPLY_GAP is to control time between two replies.

4.(Optional) Change NEWS_QUERY_COUNT as your will. NEWS_QUERY_COUNT is to control the number of statuses are read in one execution

Warning:
----
Only the message like "@your_name word" can be translated successfully. Any addtional spaces or other characters are not allowed.
Some correct examples:
"@peter china"
"@peter new year"

Some incorrect examples:
" @peter china" (There is a space before)
"@peter  china" (There are two space between "@peter" and "china")
"@peter ---- china ----" (Too many illegal characters and space)

You can improve the demo with higher resolution capability (find out the word even the message is obscure).


