#!/bin/bash

mkdir -p _build/
mkdir -p _static/
mkdir -p _templates/

cur_dir=`pwd`
export PYTHONPATH=$PYTHONPATH:$cur_dir:$cur_dir/../

echo "begin ============================" >> _build/log

make html > .stdout 2> .stderr
#make html 
cat .stdout >> _build/log
cat .stderr >> _build/log
echo "Last Build Date: " `date` >> _build/log

echo "end ============================" >> _build/log
