#!/bin/bash
#
# Fetch code from local storage
# 
# INPUT:
#    * {last_request_time}. 
#      This value is used to check the whether the code
#      seen by the script is the one just requested. 
# 
# OUTPUT:
#    * write the auth'ed url to stdout. 
# 
# Pre-condition:
#    * This script assumes "tmp/auth.code" relative to 
#      the location of it contains the auth'ed url. 

if [[ $# == 1 ]] ; then
	last_request_time=$1
else
	echo "usage:$0 {last_request_time}"
	exit 255
fi

#only keep the integer part of $last_request_time
last_request_time=`echo $last_request_time | sed 's/.[0-9]*$//g'`
last_request_time=`echo -n "$last_request_time"`

fn=`basename $0`
dir=`dirname $0`
tmp="$dir/tmp"
fn_code="$tmp/auth.code"

update_time=`stat $fn_code | grep "Modify" | sed -e 's/Modify: //g' -e 's/\.\d* //g' | xargs -i date -d"{}" +%s`
if [[ $update_time < $last_request_time ]] ; then
	echo "null"
else 
	cat $fn_code
fi

exit 0 
