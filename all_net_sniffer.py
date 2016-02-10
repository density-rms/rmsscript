#!/usr/bin/python
import time
import re, csv
import os, sys
import zdcli
zd_ip = "172.16.20.3"
zduser = "admin"
zdpass ="video54java"

while True:

        timestamp = int(time.time())
        print timestamp
        print "\nSetting sniffer AP channel:\n"
        zd = zdcli.ZDCLI(zd_ip)
        zd.connect(zduser, zdpass, timeout=3600,sesame_key="!v54!")
        ok = zd.set_snifferchan()
        zd.close()
        time.sleep(200)
