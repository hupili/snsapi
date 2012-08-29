#!/bin/bash

mkdir -p _build/
mkdir -p _static/
mkdir -p _templates/

cur_dir=`pwd`
export PYTHONPATH=$PYTHONPATH:$cur_dir:$cur_dir/../

make html
