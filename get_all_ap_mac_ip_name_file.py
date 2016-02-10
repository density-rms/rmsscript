#!/usr/bin/python
import time
import re, csv
import os, sys
import zdcli

def zd_macs_name(zdip, zduser, zdpass,tftp_addr):
    
    zd = zdcli.ZDCLI(zdip)
    zd.connect(zduser, zdpass, timeout=3600,sesame_key="!v54!")
    #zd.to_shell()
    
    maclist = zd.get_zdapmac(tftp_addr)
    return zd
def ap_name(zd,macfile):
    maclistnew = []
    fp = open("%s" % macfile, "r")
    for line in fp:
        (ap,ip) = line.split(',')
        buff = zd.get_apname(ap)
        pattern = 'Command.*?\n(.*?)\nruckus'
        res=  re.search(pattern,buff)
        if res:
            name = res.group(1).rstrip()
        else:
            name = 'Ruckus AP'
        #aptime = zd.get_aptime(ap)
        new_t = (ap,ip.rstrip(),name)
        maclistnew.append(new_t)
    zd.close()
    return maclistnew

def apDict_writer(apDict):
    csvfile1 = 'ap_mac_ip_name.csv'
    csvPtr1 = open(csvfile1,"w")
    fieldnames = ['apmac','apip','apname','aptime']
    dwriter1= csv.DictWriter(csvPtr1,fieldnames, dialect = 'excel', delimiter= ',', extrasaction='ignore')
    csvPtr1.write(','.join(fieldnames)+'\r\n')
    for key in apDict.keys():
        dwriter1.writerow(apDict[key])
    csvPtr1.close()


apDict = {}
iplist = []
namelist = []
def create_apDict(maclist):
    for m in maclist:
        apDict[m[0].upper()] = {}
        apDict[m[0].upper()]['apmac'] = m[0] 
        apDict[m[0].upper()]['apip'] = m[1] 
        apDict[m[0].upper()]['apname'] = m[2] 
        #apDict[m[0].upper()]['aptime'] = m[3] 
  
        iplist.append(m[1]) 
        namelist.append(m[2])
    return (apDict, iplist, namelist)

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
def main(zd_ip,zduser,zdpass,tftp_addr,tftp_dir,current_dir):
    '''current_dir = os.getcwd()
    tftp_dir = '/opt/tftpboot/'
    zd_ip = sys.argv[1] 
    zduser = sys.argv[2] 
    zdpass = sys.argv[3] 
    tftp_addr = '10.150.13.7'  '''
    zd = zd_macs_name(zd_ip,zduser,zdpass,tftp_addr) 
    #print mlist
    s_files = tftp_dir+"maclist" 
    d_files = current_dir+"/maclist" 
    cmd = 'cp %s %s' % (s_files, d_files)
    ok = os.system(cmd) 
    if ok == 0: 
        macList = ap_name(zd,d_files)
        (apDict, apiplist,apnamelist) = create_apDict(macList)
    apDict_writer(apDict)
    
    
if __name__ =='__main__': 
    main()
