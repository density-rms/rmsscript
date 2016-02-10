#!/usr/bin/python
import time
import re, csv
import os, sys
import subprocess
import zdcli
import parserscript_11_30
import get_all_ap_mac_ip_name_file

from datetime import datetime
from threading import Timer

months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
#working_dir = "/home/wspbackup/newdir/latestscript"
#report_dir = "/var/www/densitystatus/dailystatus"

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

def client_process_logs(ts, tftp_dir):
        flist = []
        os.system('mkdir clientstats-%s' % ts)
        savedir = 'clientstats-%s' % ts
        #tftp_dir = '/opt/tftpboot/'
        current_dir = os.getcwd()
        s_files = tftp_dir+"clientdata*.tgz"
        d_files = current_dir+"/."
        cmd = 'cp %s %s' % (s_files, d_files)
        ok = os.system(cmd)
        f = "clientdataall.tgz"
        os.system('tar -xzvf %s' % f)

        os.system('mv  clientdata*.tgz %s/.' % savedir)
        os.system('mv  %s /var/www/densitystatus/clientcapability/.' % savedir)



def process_logs(ts, tftp_dir,clientstats_dir):
        flist = []
        os.system('mkdir stats-%s' % ts)
        savedir = 'stats-%s' % ts
        #tftp_dir = '/opt/tftpboot/'
        current_dir = os.getcwd()
        s_files = tftp_dir+"athstatswifi0.tgz"
        d_files = current_dir+"/athstatswifi0.tgz"
        cmd = 'cp %s %s' % (s_files, d_files)
        ok = os.system(cmd) 
        s_files = tftp_dir+"athstatswifi1.tgz"
        d_files = current_dir+"/athstatswifi1.tgz"
        cmd = 'cp %s %s' % (s_files, d_files)
        ok = os.system(cmd) 
        s_files = tftp_dir+"logreadall.tgz"
        d_files = current_dir+"/logreadall.tgz"
        cmd = 'cp %s %s' % (s_files, d_files)
        ok = os.system(cmd) 
        s_files = tftp_dir+"datafileall.tgz"
        d_files = current_dir+"/datafileall.tgz"
        cmd = 'cp %s %s' % (s_files, d_files)
        ok = os.system(cmd)  
        if ok == 0:
            filelist = os.listdir('.')
            for f in filelist:
                if f.startswith('datafile'):
                    flist.append(f)
            for f in filelist:
                if f.startswith('logread'):
                    flist.append(f)
            for f in filelist:
                if f.startswith('athstats'):
                    flist.append(f)  
            if flist:
                for f in flist:
                    os.system('tar -xzvf %s' % f)   

        s_files = tftp_dir+"ap.log"
        d_files = current_dir+"/."
        cmd = 'cp %s %s' % (s_files, d_files)
        ok = os.system(cmd) 
        s_files = tftp_dir+"allmessages.gz"
        d_files = current_dir+"/."
        cmd = 'cp %s %s' % (s_files, d_files)
        ok = os.system(cmd)         
        os.system('mv  datafileall.tgz %s/.' % savedir)
        os.system('mv  logreadall.tgz %s/.' % savedir)
        os.system('mv  athstatswifi0.tgz %s/.' % savedir)
        os.system('mv  athstatswifi1.tgz %s/.' % savedir)
        os.system('cp  ap.log %s/.' % savedir)
        os.system('cp  allmessages.gz %s/.' % savedir)
        os.system('mv  %s %s/.' % (savedir, clientstats_dir))     
def get_ap_support(aplist,tftp_addr):
    zd = zdcli.ZDCLI(zd_ip)
    zd.connect(zduser, zdpass, timeout=3600,sesame_key="!v54!")
    #zd.to_shell()
    logs_ok = zd.get_supportfile(aplist,tftp_addr)
    zd.close()      
    
def get_ap_dramdump(aplist,tftp_addr):
    zd = zdcli.ZDCLI(zd_ip)
    zd.connect(zduser, zdpass, timeout=3600,sesame_key="!v54!")
    #zd.to_shell()
    logs_ok = zd.get_dramdump(aplist,tftp_addr)
    zd.close()     
def get_zd_details(working_dir):
    iniDict = {}
    with open('%s/initialize_file' % working_dir,'r') as ini_fp:
        for line in ini_fp:
            ini_list = line.split()
            iniDict["%s" % ini_list[0]] = ini_list[1].rstrip()
    return iniDict


if __name__ =='__main__': 
    current_dir = os.getcwd()  
    zdDict = get_zd_details(current_dir)
    if zdDict:
        
        zd_ip = zdDict['zd_ip']
        zduser = zdDict['zduser']
        zdpass = zdDict['zdpass']
        frequency =  zdDict['monitor_interval']
        tftp_addr = zdDict['tftp_addr']
        tftp_dir = zdDict['tftp_dir']
        working_dir = zdDict['working_dir']
        report_dir  = zdDict['report_dir']
        apstats_dir = zdDict['apstats_dir']
        clientstats_dir = zdDict['clientstats_dir']
        html_dir =zdDict['html_dir']
        http_addr = zdDict['http_addr']
    else:
        print "Not able to get ZD details, make sure to update details in  initilize_file, exiting"
        sys.exit(1)
    

    get_all_ap_mac_ip_name_file.main(zd_ip,zduser,zdpass,tftp_addr,tftp_dir,current_dir)
    while True:

        timestamp = int(time.time())
        #timestamp = int(1450832272)
        print timestamp
        print "\nCollecting AP logs starts:\n"
        zd = zdcli.ZDCLI(zd_ip)
        zd.connect(zduser, zdpass, timeout=3600,sesame_key="!v54!")
        #zd.to_shell()
        logs_ok = zd.get_zdallmonitor(tftp_addr)
        zd.close()  
        #### the following process the AP logs collected
        print "All collected files are being processed........"   
        process_logs(timestamp, tftp_dir,clientstats_dir)    
        #client_process_logs(timestamp, tftp_dir)      
        print "Parsing is taking place .... it takes more than 30 sec for each AP" 
        email_flag = 'no'  
        #(csv1,csv2,csv3,csv4, email_flag,heartbeat_ap_list) = parserscript_05_02.file_parser(timestamp, email_flag) 
        #(csv1,csv2,csv4, email_flag,heartbeat_ap_list) = parserscript_tx_desc_06_24.file_parser(timestamp, email_flag) 
        #csv3 = client_capability.client_file_parser(apDict,timestamp) 
        #(csv1,csv2, email_flag,heartbeat_ap_list) = parserscript_tx_desc_upgrade_count.file_parser(timestamp, email_flag) 
        #email_flag = 'no' 
        (csv1,csv2,email_flag,heartbeat_ap_list,txdescstuck_ap_list) = parserscript_11_30.file_parser(timestamp, email_flag)
        #csv3 = "hourly_air_utilization.csv"
        #csv4 = "air_utilization_5g_east.csv"
        #sv5 = "air_utilization_2g_west.csv"
        #csv6 = "air_utilization_5g_west.csv"        
        #print "email_flag", email_flag   

        if email_flag == 'yes' and txdescstuck_ap_list:
            print "getting  dram dump"
            get_ap_dramdump(txdescstuck_ap_list,tftp_addr)        
        if email_flag == 'yes' and heartbeat_ap_list:
            print "getting  support file"
            get_ap_support(heartbeat_ap_list,tftp_addr)
            current_dir = os.getcwd()
            #os.system('tar -czvf /opt/tftpboot/supportall.tgz /opt/tftpboot/support*.txt')
            s_files = tftp_dir+"support*.txt"
            d_files = current_dir+"/."
            cmd = 'mv %s %s' % (s_files, d_files)
            os.system(cmd)
            if len(heartbeat_ap_list) > 1:
                os.system('tar -czvf supportall.tgz support*.txt')
                time.sleep(5)
                filename = "supportall.tgz"
            else:
                filename = "support_%s.txt" % heartbeat_ap_list[0]
            subprocess.call(['%s/monitor_email.sh' % current_dir, "%s" % csv1, "%s" % filename])
            cmd = "rm -f support*"
            os.system(cmd)
        elif email_flag == 'yes':
            subprocess.call(['%s/monitor_email.sh' % current_dir, "%s" % csv1])      
        cmd1 = 'mv %s/%s %s/%s' % (current_dir, csv1,apstats_dir,csv1)
        cmd2 = 'mv %s/%s %s/%s' % (current_dir,csv2,clientstats_dir,csv2)
        #cmd3 = 'cp %s/%s %s/%s' % (current_dir,csv3,report_dir,csv3)
        #cmd4 = 'cp %s/%s %s/%s' % (current_dir,csv4,report_dir,csv4)  
        #cmd5 = 'cp %s/%s %s/%s' % (current_dir,csv5,report_dir,csv5)
        #cmd6 = 'cp %s/%s %s/%s' % (current_dir,csv6,report_dir,csv6)          

        os.system(cmd1)
        os.system(cmd2)  
        #os.system(cmd3) 
        #os.system(cmd4)    
        #os.system(cmd5) 
        #os.system(cmd6)            

        print " Waiting for %s sec to start the next Monitoring ..." % frequency   
        time.sleep(int(frequency))  
