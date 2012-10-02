#!/usr/bin/env bash

find ../ -name "*.py" | grep -v "third" | grep -v "back" | xargs  wc -l

