#!/bin/bash
#delete the directories older than 45 days in clientstats dir
find /var/www/densitystatus/clientstats -mtime +30 -exec rm -rf {} \;
find /var/www/densitystatus/apstats -mtime +30 -exec rm -rf {} \;
