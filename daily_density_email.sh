#!/bin/sh
rec="DL-R710-QA@ruckuswireless.com,ol-anindya-org@ruckuswireless.com,anney.morris@ruckuswireless.com sang.le@ruckuswireless.com prem.kanumuri@ruckuswireless.com amrit.lamba@ruckuswireless.com,rhudnut@ruckuswireless.com"
mfile=$1
yest=$(date --date="yesterday" +"%m/%d/%Y")
subject="Daily_report_for_Density_network_for_$yest"
mutt -s $subject -x  -a $mfile -- $rec < /home/rms/density_rms/dailymessage 

