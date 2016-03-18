#!/bin/bash
ps -ef|grep sf.py |grep -v grep|awk '{print $2}'|xargs kill -9
