#!/bin/sh
now="$(date +'%m-%d-%y-%H-%M')"
cp $1 $1-"$now"
rec="dave.lin@ruckuswireless.com"
yest=$(date --date="today" +"%m/%d/%Y")
subject="AP_support_report_$yest"
mutt -s $subject -x  -a $1 -- $rec  < newapmessage

