#!/bin/bash

nohup python forwarder.py &
PID=$!
echo $PID > mypid

exit 0
