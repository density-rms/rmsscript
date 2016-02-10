#!/usr/bin/python
import time
import re, csv
import os, sys
import subprocess
import zdcli
from netaddr import *
import parserscript

months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def zd_aps(zdip, zduser, zdpass):
    zd = zdcli.ZDCLI(zdip)
    zd.connect(zduser, zdpass, timeout=3600,sesame_key="!v54!")
    zd.to_shell()
    iplist = zd.get_aplist()
    zd.close()
    return iplist

def zd_macs(zdip, zduser, zdpass):
    zd = zdcli.ZDCLI(zdip)
    zd.connect(zduser, zdpass, timeout=3600,sesame_key="!v54!")
    zd.to_shell()
    maclist = zd.get_apmaclist()
    zd.close()
    return maclist

apDict = {}
iplist = []

def create_apDict(maclist):
    for m in maclist:
        apDict[m[0].upper()] = m[1]
        iplist.append(m[1]) 
    return (apDict, iplist)

def macs(s):
    return "".join([i for i in s if i != ":" and i !="-"])

def newping(target_ip):
    pingable = 0
    buff = os.popen(r'ping %s -c 4' % target_ip.rstrip()).read()
    #print buff
    res = re.search('.*?transmitted,\s+(\d+)\s+received,',buff)
    if res:
        if int(res.group(1)) >1:
            pingable = 1
    return pingable
def csvfile_writer(clientDict,tstamp):
    csvfile2 = 'client_capability_%s.csv' % tstamp
    csvPtr2 = open(csvfile2,"w")
    fieldnames2 = ['client','org','client_rssi','client_capability']
    dwriter2= csv.DictWriter(csvPtr2,fieldnames2, dialect = 'excel', delimiter= ',', extrasaction='ignore')
    csvPtr2.write(','.join(fieldnames2)+'\r\n')
    for key in clientDict.keys():
        dwriter2.writerow(clientDict[key])
    csvPtr2.close()
    print "Clients capability details are saved in file %s \n" % (csvfile2)
    return ( csvfile2)

def client_file_parser(apDict,ts):
#def client_file_parser():

    clientDict = {}
    clientfilelist = []
    pattern1 = "^(([a-zA-Z0-9:]+){5}[[A-Za-z0-9])+\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\n"
    filelist = os.listdir('writable/.')
    for f in filelist:
        if f.startswith('clientdata'):
            clientfilelist.append(f)

    for f in clientfilelist:

        fp = open("writable/%s" % f, "r")
        for line in fp:
            res1 = re.search(pattern1,line)
            if res1:
                client = res1.group(1)
                mac = EUI(client)
                try:
                    org = mac.oui.registration().org
                except:
                    org = "unknown"
                cap = re.sub("\s+"," ",res1.group(9))

                clientDict[client] = {}
                clientDict[client]['client'] =client 
                clientDict[client]['org'] = org 
                clientDict[client]['client_rssi'] = res1.group(6)
                clientDict[client]['client_capability'] = cap 
                
    print clientDict.keys()
    for key in clientDict.keys():
        print clientDict[key]['org']

    csv1 = csvfile_writer(clientDict,ts)
    return(csv1)

    
if __name__ =='__main__': 
    client_file_parser()   
