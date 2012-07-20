#!/bin/bash

if [[ $# == 1 ]] ; then
	url=$1
else
	echo "usage:$0 {url}"
	exit 255
fi

fn=`basename $0`
dir=`dirname $0`
tmp="$dir/tmp"
cookies="$dir/cookies.txt"

mkdir -p $tmp
wget --load-cookies $cookies "$url" -O $tmp/request_url.html > $tmp/request_url.stdout 2> $tmp/request_url.stderr
grep -P '^Location: http:.* \[following\]' $tmp/request_url.stderr | sed -e 's/^Location: //g' -e 's/ \[following\]//g' > $tmp/auth.code
cat $tmp/auth.code

exit 0
