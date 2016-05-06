#!/bin/bash
ps -ef|grep df.py |grep -v grep|awk '{print $2}'|xargs kill -9
