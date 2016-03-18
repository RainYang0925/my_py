#!/bin/bash
ps -ef|grep amon.pl |grep -v grep|awk '{print $2}'|xargs kill -9
