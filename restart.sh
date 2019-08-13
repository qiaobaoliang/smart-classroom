#!/usr/bin/bash

ps aux|grep python|grep "start_server"|awk '{print $2}'|xargs kill -9
source /home/classroom-env/bin/activate
mkdir -p log
nohup python start_server.py 2>&1 | cronolog log/%Y%m%d/%Y%m%d_%H.err &