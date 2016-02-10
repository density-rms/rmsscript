#!/bin/sh
#rec="anney.morris@ruckuswireless.com"
rec="gagan.jain@ruckuswireless.com,koti.mellachervu@ruckuswireless.com,ilango@ruckuswireless.com,venkat.chirreddy@ruckuswireless.com,henry.zeng@ruckuswireless.com,wchen@ruckuswireless.com,anney.morris@ruckuswireless.com sang.le@ruckuswireless.com prem.kanumuri@ruckuswireless.com amrit.lamba@ruckuswireless.com"
subject="DENSITY-NETWORK-AP-status"
if [ $# -eq 2 ]
  then 
     mfile1=$1
     mfile2=$2
    mutt -s $subject -x  -a $mfile1 -a $mfile2 -- $rec < mymessage 
 else
    mfile1=$1
    mutt -s $subject -x  -a $mfile1 -- $rec < mymessage 
fi

