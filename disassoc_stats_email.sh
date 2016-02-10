#!/bin/sh
rec="anney.morris@ruckuswireless.com prem.kanumuri@ruckuswireless.com"
mfile=$1
yest=$(date --date="yesterday" +"%m/%d/%Y")
subject="Daily_report_for_client_disassoc_in_densitynetwork_for_$yest"
mutt -s $subject -x  -a $mfile -- $rec < /home/wspbackup/newdir/latestscript/disassocmessage 

