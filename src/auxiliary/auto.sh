#!/bin/bash

echo "======================================" >> log 
echo "begin:" `date` >> log 
echo "======================================" >> log 
#TODO: Here comes your command
#      Following is an example of our forwarder app
#python ./forwarder.py 2>&1 >> log
echo "======================================" >> log 
echo "end:" `date` >> log 
echo "======================================" >> log 


exit 0 
