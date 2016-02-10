#!/bin/bash
now="$(date +'%m-%d-%y-%H-%M')"
printf "$now"
cp /var/log/syslog /media/bkup-drive/syslog-"$now"
