#!/bin/bash
ps -ef|grep amon.py |grep -v grep|awk '{print $2}'|xargs kill -9
