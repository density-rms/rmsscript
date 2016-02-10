#!/bin/sh
#rec="anney.morris@ruckuswireless.com"
#rec="DL-R710-QA@ruckuswireless.com,ol-anindya-org@ruckuswireless.com,anney.morris@ruckuswireless.com sang.le@ruckuswireless.com prem.kanumuri@ruckuswireless.com amrit.lamba@ruckuswireless.com,dkaiser@ruckuswireless.com,rhudnut@ruckuswireless.com"
rec="ming.tsang@ruckuswireless.com  anney.morris@ruckuswireless.com amrit.lamba@ruckuswireless.com   prem.kanumuri@ruckuswireless.com koti.mellachervu@ruckuswireless.com ilango@ruckuswireless.com venkat.chirreddy@ruckuswireless.com" 
mfile=$1
#mfile1=$2
yest=$(date --date="today" +"%m/%d/%Y")
subject="hourly_report_for_Density_network_for_$yest"
mutt -s $subject -x  -a $mfile   -- $rec < /home/rms/density_rms/dailymessage 

