#!/bin/bash

rm -rf _build/
mkdir -p _build/
mkdir -p _static/
mkdir -p _templates/
mkdir -p _build/todo/

cur_dir=`pwd`
export PYTHONPATH=$PYTHONPATH:$cur_dir:$cur_dir/../

echo "begin Sphinx ============================" >> _build/log

$HOME/.local/bin/sphinx-build -b html -d _build/doctrees . _build/html > .stdout 2> .stderr

#make html > .stdout 2> .stderr
#make html 
cat .stdout >> _build/log
cat .stderr >> _build/log
echo "Last Build Date: " `date` >> _build/log

echo "end Sphinx ============================" >> _build/log


echo "begin TODO ============================" >> _build/log

./gentodo.pl > _build/todo/index.html

echo "end TODO ============================" >> _build/log
