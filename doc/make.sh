#!/bin/bash

rm -rf _build/
mkdir -p _build/
mkdir -p _static/
mkdir -p _templates/
mkdir -p _build/todo/

cur_dir=`pwd`
export PYTHONPATH=$PYTHONPATH:$cur_dir:$cur_dir/../

if [[ -e "$HOME/.local/bin/sphinx-build" ]] ; then 
	SPHINX_BUILD=$HOME/.local/bin/sphinx-build
elif [[ `command -v sphinx-build` == 0 ]] ; then
	SPHINX_BUILD=sphinx-build
else
	echo "Can not locate 'sphinx-build' command"
	exit 255
fi

echo SPHINX_BUILD: $SPHINX_BUILD

echo "begin Sphinx ============================" >> _build/log

$SPHINX_BUILD -b html -d _build/doctrees . _build/html > .stdout 2> .stderr

#make html > .stdout 2> .stderr
#make html 
cat .stdout >> _build/log
cat .stderr >> _build/log
echo "Last Build Date: " `date` >> _build/log

echo "end Sphinx ============================" >> _build/log


echo "begin TODO ============================" >> _build/log

./gentodo.pl > _build/todo/index.html

echo "end TODO ============================" >> _build/log
