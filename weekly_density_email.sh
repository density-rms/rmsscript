#!/bin/sh
rec="henry.zeng@ruckuswireless.com,viola.chin@ruckuswireless.com,DL-R710-Wireless@ruckuswireless.com,DL-R710-NonWireless@ruckuswireless.com,wchen@ruckuswireless.com,anney.morris@ruckuswireless.com sang.le@ruckuswireless.com prem.kanumuri@ruckuswireless.com amrit.lamba@ruckuswireless.com,dkaiser@ruckuswireless.com"
mfile=$1
yest=$(date --date="today" +"%m/%d/%Y")
fest=$(date --date="7 days ago" +"%m/%d/%Y")
subject="Weekly_report_for_Density_network_starting_from_$fest"
mutt -s $subject -x  -a $mfile -- $rec < /home/wspbackup/newdir/latestscript/weeklymessage 

