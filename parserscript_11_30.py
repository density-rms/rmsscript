#!/usr/bin/python2.7

import re, csv
import sys, os
import  time 
import datetime
import calendar
import pandas as pd
import fileinput

TIME_FORMAT = '%Y-%m-%d-%H:%M:%S'
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
txdescstuck_ap_list = []
def get_year():
    cmd = 'date -d "today" \'+%Y %b %d\''
    mydate = os.popen(cmd).read()
    current_year = mydate.split()[0]
    return current_year 

def get_todaydate_clientfile():
    ### get today's date and filter the log
    cmd = 'date -d "today" \'+%b %d\''
    mydate = os.popen(cmd).read()
    print mydate
    if mydate[4] == '0':
        todaydate = (mydate[:3]+' '+mydate[5]).rstrip()
    else:
        todaydate = mydate.rstrip()
    print todaydate
    
    return(todaydate)
def get_todaydate_aplog():
    ### get today's date and filter the log
    cmd = 'date -d "today" \'+%b %d\''
    #cmd = 'date -d " days ago" \'+%b %d\''
    mydate = os.popen(cmd).read()
    #print mydate
    if mydate[4] == '0':
        todaydate = (mydate[:4]+' '+mydate[5]).rstrip()
    else:
        todaydate = mydate.rstrip()
    print todaydate
    return(todaydate)
def walcsv_writer(ap_walDict,tstamp):
    csvfile1 = 'wal_stats_%s.csv' % tstamp 
    csvPtr1 = open(csvfile1,"w") 
    fieldnames1 = ['ap','ts','action']
    dwriter1= csv.DictWriter(csvPtr1,fieldnames1, dialect = 'excel', delimiter= ',', extrasaction='ignore')
    csvPtr1.write(','.join(fieldnames1)+'\r\n')
    for ap in ap_walDict.keys():
        for ts in sorted(ap_walDict[ap].keys()):
            dwriter1.writerow(ap_walDict[ap][ts])
    csvPtr1.close()
    print "WAL stats are saved in file %s\n" % (csvfile1)
    return (csvfile1) 

def switchcsv_writer(ap_switchDict,tstamp):
    csvfile1 = 'switching_stats_%s.csv' % tstamp 
    csvPtr1 = open(csvfile1,"w") 
    fieldnames1 = ['ap','ts','action']
    dwriter1= csv.DictWriter(csvPtr1,fieldnames1, dialect = 'excel', delimiter= ',', extrasaction='ignore')
    csvPtr1.write(','.join(fieldnames1)+'\r\n')
    for ap in ap_switchDict.keys():
        for ts in sorted(ap_switchDict[ap].keys()):
            dwriter1.writerow(ap_switchDict[ap][ts])
    csvPtr1.close()
    print "AP channel switching stats are saved in file %s\n" % (csvfile1)
    #file2 ="switching_stats.csv"
    #cmd = 'cp %s /var/www/densitystatus/dailystaus/%s' % (csvfile1,file2)
    #os.system(cmd)
    return (csvfile1) 

def airutility_writer(utilitylist,dtype,wing):

    csvname = "air_utilization_%s_%s.csv" % (dtype,wing)
    file_exists = os.path.isfile(csvname)
    try:
        staCsvPtr= open('%s' % csvname,"ab")
    except IOError:
        print "cannot open CSV file, exiting\n"
        sys.exit(1)
    fieldnames = ['newDate', 'Total Air Utilization @time']
    dwriter= csv.writer(staCsvPtr,fieldnames, delimiter= ',')
    
    if file_exists:
        dwriter.writerow(utilitylist)
    else:

        staCsvPtr.write(','.join(fieldnames)+'\r\n')  
        dwriter.writerow(utilitylist)
    
    staCsvPtr.close()
    return (csvname)

def newairutility_writer(utilitylist):

    csvname = "hourly_air_utilization.csv" 
    file_exists = os.path.isfile(csvname)
    try:
        staCsvPtr= open('%s' % csvname,"ab")
    except IOError:
        print "cannot open CSV file, exiting\n"
        sys.exit(1)
    fieldnames = ['newDate','east_2g_avg_air_util','east_5g_avg_air_util','west_2g_avg_air_util','west_5g_avg_air_util' ]
    dwriter= csv.writer(staCsvPtr,fieldnames, delimiter= ',')
    
    if file_exists:
        dwriter.writerow(utilitylist)
    else:

        staCsvPtr.write(','.join(fieldnames)+'\r\n')  
        dwriter.writerow(utilitylist)
    
    staCsvPtr.close()
    return (csvname)

def get_client_count(csv1,timestamp):
    ## this adds a row to the moving_client.csv file 
    ## Add the current value for client sum and channel change
    report_dir = '/var/www/densitystatus/dailystatus/'
    df = pd.read_csv('%s' % (csv1))
    g_sum = df['g_client_count'].sum() 
    a_sum = df['a_client_count'].sum() 
    g_ch_switch_sum = df['2g_ch_switch_count'].sum() 
    a_ch_switch_sum = df['5g_ch_switch_count'].sum()     
    df1 = pd.read_csv('%s/moving_client.csv' % (report_dir))
    tt= df1.drop(df1.index[0])  ## remving the first row
    t = time.strftime('%H:%M', time.localtime(timestamp))
    df2 = pd.DataFrame({'eventtime':t,
                        'sum_gclient':g_sum,
                        'sum_aclient':a_sum,
                        'sum_a_ch_switch':g_ch_switch_sum,
                        'sum_g_ch_switch':a_ch_switch_sum}, index=[0])
    #print df2.values
    tt1 = tt.append(df2)   ## adding a new row
    #print tt1.values   
    tt1.to_csv('%s/moving_client.csv' % report_dir,index=False,header=True)
def csvfile_writer(apDict,ap_clientDict,tstamp):
    csvfile1 = 'ap_stats_%s.csv' % tstamp 
    csvfile2 = 'client_stats_%s.csv' % tstamp 
    csvPtr1 = open(csvfile1,"w")
    csvPtr2 = open(csvfile2,"w")
    fieldnames1 = ['ap','ip','ap_name','uptime','g_client_count','a_client_count','cpuUse','per_memoryUsage', '2g_ch_switch_count','5g_ch_switch_count','heartbeatlost_count','heartbeatlost_time','reboot_count','upgrade_reboot_count','reboot_reason','target_assert_count','target_assert_times','tx_desc_stuck_count','tx_desc_stuck_times','wmi_stuck_count','wmi_lasttime_reported','target_inactive_count','target_inactive_times','beacon_stuck','2g_ch_util_Busy','2g_ch_util_RX','2g_ch_util_TX','2g_ch_util_Total','5g_ch_util_Busy','5g_ch_util_RX','5g_ch_util_TX','5g_ch_util_Total','2g_channel','5g_channel']
    fieldnames2 = ['station','ts','action','name','radio','auth_difficult_wlan','hint','rx_rssi','ack_rssi','reason','freq','chan','stats','ap','ip','total_bytes','elapsed_time_sec']    
    dwriter1= csv.DictWriter(csvPtr1,fieldnames1, dialect = 'excel', delimiter= ',', extrasaction='ignore')
    dwriter2= csv.DictWriter(csvPtr2,fieldnames2, dialect = 'excel', delimiter= ',', extrasaction='ignore')
    csvPtr1.write(','.join(fieldnames1)+'\r\n')
    for key in apDict.keys():
        #print key
        if 'ip' not in apDict[key].keys() or apDict[key]['ip'] == 'unknown':
            continue
        dwriter1.writerow(apDict[key])
    csvPtr1.close()
    csvPtr2.write(','.join(fieldnames2)+'\r\n')
    for mac in ap_clientDict.keys():
        for ts in sorted(ap_clientDict[mac].keys()):
            dwriter2.writerow(ap_clientDict[mac][ts])
    csvPtr2.close()
    print "Network stats are saved in files %s  and %s \n" % (csvfile1,csvfile2)
    return (csvfile1, csvfile2)
    
def utc_localtime_conversion(year,ts,todaydate):
    (m,d,t) = ts.split()
    if m in months:
        m_index = months.index(m) 
    utc_str ='-'.join([year,str(m_index+1),d,t])  
    #print utc_str
    timestamp = calendar.timegm(datetime.datetime.strptime(utc_str,TIME_FORMAT).timetuple())
    local = datetime.datetime.fromtimestamp(timestamp).strftime(TIME_FORMAT)
    #print local
    (a,b,c,e) = local.split('-')
    if b[0] == '0':
        nb = b[1]
    else:
        nb = b
    if nb == str(m_index+1) or nb == str(m_index) :
            if c[0] == '0':
                nd = c[1]
            else:
                nd = c
            #if nd == d:

            ts_new = ' '.join([months[int(nb)- 1],nd,e])  
            #print ts_new
            #print todaydate
            #ts  = "Mar 23"
            if todaydate in ts_new:
                #local_time = ' '.join(s for s in local.split('-'))
                return ts_new
            else:
                return False

def ap_reboot_dict(timestamp,email_flag,apDict,message_fp,heartbeat_ap_list):
 
    #heartbeat_ap_list = []
    start_time = timestamp 
    rebootDict = apDict 
    #Jul 25 23:03:49 density-zd3k-1 stamgr: stamgr_update_reboot_info():AP[f0:b0:52:23:8a:80] reboot detail:apmgr, Update AP's Firmware completely 
    #Nov 24 06:18:30 density-zd-3k syslog: eventd_to_syslog():AP[W08A-Collie-R710@2c:c5:d3:01:82:30] joins with uptime [79] s and last disconnected reason [AP Restart : application reboot]
    pattern8 = "([a-zA-Z]+\s+\d+\s+[\d:]+)\s+.*?eventd_to_syslog\(\):AP\s+.*?@(.*?)\s+joins.*?(AP\s+Restart\s+:\s+.*)"
    pattern9 ="([a-zA-Z]+\s+\d+\s+[\d:]+)\s+.*?eventd_to_syslog\(\):AP\s+.*?@(.*?)\s+joins.*?Heartbeat\s+Loss"
    pattern8a ="([a-zA-Z]+\s+\d+\s+[\d:]+)\s+.*?stamgr_update_reboot_info\(\):AP\s+(.*?)\s+reboot\s+detail:apmgr,\s+Update.*?Firmware\s+completely"
    todaydate = get_todaydate_aplog()
    print todaydate
    ### reading the ap.log file and grep only reboot and heartbeat
    c_dir = os.getcwd() 
    print c_dir
    os.system('cat %s/ap.log |grep -i uptime | grep \"%s\" > apreboot' % (c_dir,todaydate))
    os.system('cat %s/ap.log |grep -i "reboot detail:apmgr," | grep \"%s\" >> apreboot' % (c_dir,todaydate))
    fp_input = open("apreboot" , "r")

    for line in fp_input.readlines():

        line = line.replace('[',' ').replace(']',' ')
        res8 = re.search(pattern8,line)
        res9 = re.search(pattern9,line)
        res8a = re.search(pattern8a,line)
        if res8:
            AP = res8.group(2)
            AP = AP.replace(':','_')
            if AP in rebootDict.keys():
                if 'ap_name' not in rebootDict[AP].keys():
                    continue
                ts = res8.group(1)
                (m,d,t) = ts.split()
                if m in months:
                    m_index = months.index(m)
                slist = [int(x) for x in t.split(':')]
                tlist = [2016, m_index+1, int(d)]
                tlist.extend(slist)
                tlist.extend([1,1,1])
                time_insec = int(time.mktime(tuple(tlist)))
                #print start_time, time_insec
                #print start_time-time_insec
                #1448352936
                if (start_time - time_insec) < 2500+3600:
                    #print line
                    email_flag = 'yes'
                    heartbeat_ap_list.append(AP)
                    message_fp.write("ap %s (%s)  rebooted.\n" % (rebootDict[AP]['ap_name'],rebootDict[AP]['ip']))
                reason = res8.group(3)
                if 'reboot_count' not in rebootDict[AP].keys():
                    rebootDict[AP]['reboot_count'] = 0 
                if 'reboot_reason' not in rebootDict[AP].keys():
                    rebootDict[AP]['reboot_reason'] = [] 
                rebootDict[AP]['reboot_count'] += 1
                rebootDict[AP]['reboot_reason'].append((ts,reason))
                #rebootDict[AP]['ts'] = ts 
                
        if res8a:
            AP = res8a.group(2)
            AP = AP.replace(':','_')
            if AP in rebootDict.keys():
                if 'ap_name' not in rebootDict[AP].keys():
                    continue
                ts = res8a.group(1)
                (m,d,t) = ts.split()
                if m in months:
                    m_index = months.index(m)
                slist = [int(x) for x in t.split(':')]
                tlist = [2016, m_index+1, int(d)]
                tlist.extend(slist)
                tlist.extend([1,1,1])
                time_insec = int(time.mktime(tuple(tlist)))
                #print start_time, time_insec
                #print start_time-time_insec
                if (start_time - time_insec) < 2500+3600:
                    #print line
                    #email_flag = 'yes'
                    #heartbeat_ap_list.append(AP)
                    message_fp.write("ap %s (%s)  upgraded.\n" % (rebootDict[AP]['ap_name'],rebootDict[AP]['ip']))
                if 'upgrade_reboot_count' not in rebootDict[AP].keys():
                    rebootDict[AP]['upgrade_reboot_count'] = 0 
                rebootDict[AP]['upgrade_reboot_count'] += 1

        elif res9:
            AP = res9.group(2)
            AP = AP.replace(':','_')
            if AP in rebootDict.keys():
                if 'ap_name' not in rebootDict[AP].keys():
                    continue                
                ts = res9.group(1)
                (m,d,t) = ts.split()
                if m in months:
                    m_index = months.index(m)
                slist = [int(x) for x in t.split(':')]
                tlist = [2016, m_index+1, int(d)]
                tlist.extend(slist)
                tlist.extend([1,1,1])
                time_insec = int(time.mktime(tuple(tlist)))
                #print start_time, time_insec
                #print start_time-time_insec            
                if (start_time - time_insec) < 2500+3600:
                    email_flag = 'yes'
                    heartbeat_ap_list.append(AP)
                    message_fp.write("heartbeat Loss for ap %s   ( %s ).\n" % (rebootDict[AP]['ap_name'],rebootDict[AP]['ip']))
                    #dayDict['total_no_of_AP_heartbeat_loss'] += 1
    
                ts = res9.group(1)
                if 'heartbeatlost_count' not in rebootDict[AP].keys():
                    rebootDict[AP]['heartbeatlost_count'] = 0 
                rebootDict[AP]['heartbeatlost_count'] += 1
                if 'heartbeatlost_time' not in rebootDict[AP].keys():
                    rebootDict[AP]['heartbeatlost_time'] = [] 
                rebootDict[AP]['heartbeatlost_time'].append(ts)
    message_fp.close()
    return(rebootDict,email_flag,heartbeat_ap_list)
# This module computes the sum of airtime for the time stamp
def apStatsSum(csv1):
    
    headers = '2g_ch_util_Busy,2g_ch_util_RX,2g_ch_util_TX,2g_ch_util_Total,5g_ch_util_Busy,5g_ch_util_RX,5g_ch_util_TX,5g_ch_util_Total'.split(',')

    lastfile = csv1
    east_ap_list = ['172.16.22.55','172.16.22.158','172.16.21.120','172.16.21.93','172.16.22.52','172.16.21.168','172.16.22.156','172.16.22.122','172.16.22.157','172.16.21.128','172.16.21.122','172.16.22.8','172.16.22.60','172.16.22.153','172.16.21.235','172.16.21.131','172.16.20.86']
    west_ap_list = ['172.16.22.54','172.16.22.95','172.16.21.254','172.16.20.97','172.16.22.132','172.16.21.189','172.16.21.35','172.16.21.124','172.16.22.34','172.16.22.22','172.16.21.221','172.16.21.126','172.16.21.247']
    if lastfile:
        f1 = 'east_out.csv'
        f2 = 'west_out.csv'
        # separating the list for east and west wing                            
        df = pd.read_csv('%s' % (lastfile))
        df_new = df[df['ip'].isin(east_ap_list)]
        df_new.to_csv('%s' % f1, cols=headers,index=None)
        
        df = pd.read_csv('%s' % (lastfile))
        df_new = df[df['ip'].isin(west_ap_list)]
        df_new.to_csv('%s' % f2, cols=headers,index=None)        
       
    if f1:
        df = pd.read_csv('%s' % (f1)) 
 
        east_g_Total_mean = df['2g_ch_util_Total'].mean().round()
        east_a_Total_mean = df['5g_ch_util_Total'].mean().round()

    
    if f2:
        df = pd.read_csv('%s' % (f2))
        west_g_Total_mean = df['2g_ch_util_Total'].mean().round()
        west_a_Total_mean = df['5g_ch_util_Total'].mean().round()
       
    cmd = 'date -d "today" \'+%H:00\''
    #cmd = 'date -d "today" \'+%b %d %H:%M\''
    mydate = os.popen(cmd).read().rstrip() 
    utilization_list = [mydate,east_g_Total_mean,east_a_Total_mean,west_g_Total_mean,west_a_Total_mean]
    csv3 = newairutility_writer(utilization_list)
    return csv3  
 
def file_parser(timestamp,email_flag):
    todaydate = get_todaydate_clientfile()
    year = get_year()
    heartbeat_ap_list = []
    txdescstuck_ap_list = []
    message_fp = open('mymessage','w')
    message_fp.write('The following events happened on DENSITY NETWORK in the last half hour\n\n')
    #(apDict,email_flag) = ap_reboot_dict(tstamp,email_flag) 
    apDict = {} 
    logfilelist,datafilelist,wifi0list,wifi1list = [],[],[],[]
    start_time = timestamp
    pattern1 = '.*?Mem:\s+(\d+)K.*?(\d+)K.*?CPU:\s+(\d+).*?Command.*?up\s+(.*?)load'
    #pattern2 = '^\s+(\d+)\s+(\d+)\s+(([a-zA-Z0-9:]+){5}[A-Za-z0-9]+)\s+'
    pattern2 = '\s+(\d+)\s+(\d+)\s+[a-zA-Z0-9]+:[a-zA-Z0-9]+:'
    pattern21 =  'Dev:wifi(\d)\s+has\s+(\d+)\s+nodes' 
    #pattern10 = 'VDEVs\s+beacon\s+stuck\s+period'
    pattern10 = '.*\[(.*?)\]\s+\[Uptime.*?\]\s+(Wifi\d)\s+Beacon Tx seems stalled\s+\['
    pattern11 = '.*\[(.*?)\]\s+\[.*?\].*?stuck count:\s+(\d+).*?WMI:\s+halted:\s+(\d+)'
    pattern12 = '.*\[(.*?)\]\s+\[.*\].*?XXX\s+TARGET\s+ASSERTED\s+XXX'
    #[2015/10/30 12:53:18] [Uptime : 6195 min] Wifi1 No Activity from target [ Idle_count : 61 threshold : 60 ]
    pattern14 = '.*\[(.*?)\]\s+\[Uptime.*?\]\s+(Wifi\d)\s+No Activity from target\s+\['
    pattern24 = '.*\[(.*?)\]\s+\[Uptime.*?\]\s+(Wifi\d)\s+Tx Desc Stuck:'
    pattern13 = '.*?Busy:\s+(\d+)\s+RX:\s+(\d+)\s+TX:\s+(\d+)\s+Total:\s+(\d+)'
    pattern3 = '\n([a-zA-Z]+\s+\d+\s+[\d:]+)\s+.*?channel-wifi(\d): channelfly'
    pattern4 = 'Command \'uptime \' executed.*?\n(.*?)\n.*?Command \'hostname \' executed'
    #pattern5 = '([a-zA-Z]+\s+\d+\s+[\d:]+)\s+.*?begin to process roaming from.*?station.*?:(.*?)\n.*?AP\s+IPv4.*?roam from.*?:(.*?)\n.*?AP\s+IPv4.*?roam to.*?:(.*?)\n'
    #pattern5 = '\n([a-zA-Z]+\s+\d+\s+[\d:]+)\s+.*?begin to process roaming from.*?station mac:(.*?)\n.*?AP\s+mac.*?roam from.*?:(.*?)\n.*?AP\s+mac.*?roam to.*?:(.*?)\n'
    pattern6 ='\n([a-zA-Z]+\s+\d+\s+[\d:]+)\s+.*?Eved:\s+STA-DISASSOC-REASON,nimac=(.*?),.*?hint=(.*?),.*?rx_rssi=(\d+),ack_rssi=(\d+),reason=(\d+),freq=(\d+),chan=(\d+),stats=(.*?)\n'
    pattern7 ='\n([a-zA-Z]+\s+\d+\s+[\d:]+)\s+.*?(wlan\d+)\s+(.*?\s+):\s+Authentication Difficulty'
    #pattern15 = '\n([a-zA-Z]+\s+\d+\s+[\d:]+)\s+.*?(WAL DEV reset), rx\s+\d+, tx\s+\d+, reset =\d+ reason\s+\d+'
    #pattern16 = '\n([a-zA-Z]+\s+\d+\s+[\d:]+)\s+.*?(WAL TX timeout) sig.*?txq\s+'
    #pattern18 = '\n([a-zA-Z]+\s+\d+\s+[\d:]+)\s+.*?(WAL RX timeout) tsf\s+'

    filelist = os.listdir('writable/.')
    for f in filelist:
        if f.startswith('datafile'):
            datafilelist.append(f)
        elif f.startswith('logread'):
            logfilelist.append(f)
        elif f.startswith('athstats_wifi0'):
            wifi0list.append(f)
        elif f.startswith('athstats_wifi1'):
            wifi1list.append(f)
    # Creating the AP dictionary for name, ip, mac        
    names = pd.read_csv('ap_mac_ip_name.csv')
    aps = names[['apmac','apip','apname']]
    ap_ip_list = [] 
    apipDict = {}
    apmacDict = {}
    for i in range (0,len(aps)):
        ap_ip_list.append(aps['apip'][i])
        apipDict[aps['apip'][i]] = aps['apname'][i]
        apmacDict[aps['apmac'][i].upper()] = aps['apip'][i]

    for f in datafilelist:
        ap = f.split('.')[-1]
        if ap =='py' or ap == 'swp':
            continue
              
        ap_mac = ap.replace('_',':').upper()
        if ap_mac in apmacDict.keys():
            ip = apmacDict[ap_mac]
            ap_name = apipDict[ip]
        else:
            ip = 'unknown'
            continue
        if ap not in apDict.keys():
            apDict[ap] = {}
        fp = open('writable/%s' % f, 'r')
        buff = fp.read()
        #print buff
        res1 = re.search(pattern1,buff,re.DOTALL)
        if res1:
            apDict[ap]['ap'] = ap 
            apDict[ap]['ip'] = ip 
            apDict[ap]['ap_name'] = ap_name
            apDict[ap]['uptime'] = res1.group(4).replace(',', ' ') 
            freemem = int(res1.group(2))
            usedmem = int(res1.group(1))
            cpuuse = int(res1.group(3))            
            apDict[ap]['FreeMem'] = freemem
            apDict[ap]['UsedMem'] = usedmem
            apDict[ap]['cpuUse'] = cpuuse
            
            if  cpuuse > 75:
                email_flag = 'yes'
                message_fp.write("CPU use  in ap %s  ( %s ) is %s%s .\n" % (ap_name,ip,cpuuse,'%'))
                heartbeat_ap_list.append(ap)
            x = (freemem + usedmem)
            memory_per = float(usedmem) /(freemem + usedmem) * 100
            new_mem = int(memory_per)
            apDict[ap]['per_memoryUsage'] = new_mem
            if memory_per > 75:
                #email_flag = 'yes'
                email_flag = 'no'
                heartbeat_ap_list.append(ap)
                message_fp.write("Used memory  in ap %s  ( %s ) is %s%s of total memory\n" % (ap_name,ip,new_mem,'%')) 
                message_fp.write("\n")

        ## new client count
     
        res21 = re.findall(pattern21,buff)
        res2 = re.findall(pattern2,buff)
        g_client_ct = 0
        a_client_ct = 0
        
        if res21:
                if len(res21) == 2:
                    g_count = int(res21[0][1])               
                    a_count = int(res21[1][1])
                    
                elif len(res21) == 1:
                    if res21[0][0] == '0':
                        g_count = int(res21[0][1])
                        a_count = 0
                    else:
                        a_count = int(res21[0][1]) 
                        g_count = 0            
                #g_count = int(res21[0][1])
                #a_count = int(res21[1][1])
        if res2:
            g_list = res2[:g_count]
            
            a_list = res2[g_count:]
            
            for t in g_list:
             
                if int(t[1]) > 0:
                    #client = t[2]
                    g_client_ct += 1
                    
            for t in a_list:
                if int(t[1]) > 0:
                    #client = t[2]
                    a_client_ct += 1
            apDict[ap]['g_client_count'] = g_client_ct
            apDict[ap]['a_client_count'] = a_client_ct
       
        res11 = re.search(pattern11,buff)
        if res11:
            
            ts = res11.group(1)
            wmi_count = res11.group(3)
            (m,d,t) = ts.replace('/',' ').split()
            month = months[int(m)-1]
            adate = " ".join([month,d,t])
            ts_new = utc_localtime_conversion(year,adate,todaydate)
            if ts_new:
                (m,d,t) = ts_new.split()
                slist = [int(x) for x in t.split(':')]
                tlist = [int(y), int(months.index(m))+1, int(d)]
                tlist.extend(slist)
                tlist.extend([1,1,1])
                time_insec = int(time.mktime(tuple(tlist)))
                #print start_time, time_insec
                if (start_time - time_insec) < 2500+3600:
                    email_flag = 'yes'
                    message_fp.write("wmi stuck in ap %s  ( %s ).\n" % (ap_name,ip)) 
                    heartbeat_ap_list.append(ap)
                if ap not in apDict.keys():
                    apDict[ap] = {}
                    apDict[ap]['ap'] = ap
                    apDict[ap]['ip'] = ip
                    apDict[ap]['ap_name'] = ap_name
                apDict[ap]['wmi_stuck_count'] = wmi_count
                apDict[ap]['wmi_lasttime_reported'] = ts_new


        res12 =  re.findall(pattern12,buff)

        if res12:
            target_assert_time = []
            for ts in res12:
             
                (y,m,d,t) = ts.replace('/',' ').split()
                month = months[int(m)-1]
                adate = " ".join([month,d,t])
                ts_new = utc_localtime_conversion(year,adate,todaydate)
                if ts_new:
                    (m,d,t) = ts_new.split()
                    slist = [int(x) for x in t.split(':')]
                    tlist = [int(y), int(months.index(m))+1, int(d)]
                    tlist.extend(slist)
                    tlist.extend([1,1,1])
                    time_insec = int(time.mktime(tuple(tlist)))
                    #print start_time, time_insec
                    target_assert_time.append(ts_new)
                    if (start_time - time_insec) < 2500+3600:
                        email_flag = 'yes'
                        message_fp.write("target assert in ap %s  ( %s ).\n" % (ap_name,ip))
                        heartbeat_ap_list.append(ap)

                    if ap not in apDict.keys():
                        apDict[ap] = {}
                        apDict[ap]['ap'] = ap
                        apDict[ap]['ip'] = ip
                        apDict[ap]['ap_name'] = ap_name
                
                    apDict[ap]['target_assert_times'] = target_assert_time             
                    apDict[ap]['target_assert_count'] = len(target_assert_time) 
   
        res10 =  re.findall(pattern10,buff)
        beacon_stuck_time = []
        if res10:
            for t in res10:
                ts = t[0] 
                interface = t[1]
                (y,m,d,t) = ts.replace('/',' ').split()
                month = months[int(m)-1]
                adate = " ".join([month,d,t])
                ts_new = utc_localtime_conversion(year,adate,todaydate)
                if ts_new:
                    (m,d,t) = ts_new.split()                
                    slist = [int(x) for x in t.split(':')]
                    tlist = [int(y), int(months.index(m))+1, int(d)]
                    tlist.extend(slist)
                    tlist.extend([1,1,1])
                    time_insec = int(time.mktime(tuple(tlist)))
                    #print start_time, time_insec
                    if (start_time - time_insec) < 2500+3600:
                        email_flag = 'yes'    
                        message_fp.write("beacon stuck in ap %s  ( %s ).\n" % (ap_name,ip))
                        heartbeat_ap_list.append(ap)            

                        if ap not in apDict.keys():
                            apDict[ap] = {}
                            apDict[ap]['ap'] = ap
                            apDict[ap]['ip'] = ip
                            apDict[ap]['ap_name'] = ap_name
                        beacon_stuck_time.append(ts_new)
                    apDict[ap]['beacon_stuck'] = beacon_stuck_time 
                    apDict[ap]['beacon_stuck_count'] = len(beacon_stuck_time) 

        res14 =  re.findall(pattern14,buff)
        if res14:
            target_inactive_time = []
            for t in res14:
                ts = t[0] 
                interface = t[1]
                (y,m,d,t) = ts.replace('/',' ').split()
                month = months[int(m)-1]
                adate = " ".join([month,d,t])
                ts_new = utc_localtime_conversion(year,adate,todaydate)
                if ts_new:
                    (m,d,t) = ts_new.split()                
                    slist = [int(x) for x in t.split(':')]
                    tlist = [int(y), int(months.index(m))+1, int(d)]
                    tlist.extend(slist)
                    tlist.extend([1,1,1])
                    time_insec = int(time.mktime(tuple(tlist)))
                    #print start_time, time_insec
                    if (start_time - time_insec) < 2500+3600:
                        email_flag = 'yes'    
                        message_fp.write("target inactivity in ap %s  ( %s ).\n" % (ap_name,ip))
                        heartbeat_ap_list.append(ap)
                    
                        if ap not in apDict.keys():
                            apDict[ap] = {}
                            apDict[ap]['ap'] = ap
                            apDict[ap]['ip'] = ip
                            apDict[ap]['ap_name'] = ap_name
                        target_inactive_time.append(ts_new)
                    apDict[ap]['target_inactive_times'] = target_inactive_time 
                    apDict[ap]['target_inactive_count'] = len(target_inactive_time)             
##Tx Descr stuck
        res24 =  re.findall(pattern24,buff)
        #print ap
        if res24:
            tx_desc_stuck_time = []
            for t in res24:
                ts = t[0] 
                interface = t[1]

                (y,m,d,t) = ts.replace('/',' ').split()
                month = months[int(m)-1]
                adate = " ".join([month,d,t])
                ts_new = utc_localtime_conversion(year,adate,todaydate)
                if ts_new:
                    (m,d,t) = ts_new.split()
                    slist = [int(x) for x in t.split(':')]
                    tlist = [int(y), int(months.index(m))+1, int(d)]
                    tlist.extend(slist)
                    tlist.extend([1,1,1])
                    time_insec = int(time.mktime(tuple(tlist)))
                    #print start_time, time_insec
                    if (start_time - time_insec) < 2500+3600:
                        email_flag = 'yes'
                        message_fp.write("TX descriptor stuck in ap %s  ( %s ) interface %s.\n" % (ap_name,ip,interface))
                        heartbeat_ap_list.append(ap)
                        txdescstuck_ap_list.append((ap,interface))
                    if ap not in apDict.keys():
                        apDict[ap] = {}
                        apDict[ap]['ap'] = ap
                        apDict[ap]['ip'] = ip
                        apDict[ap]['ap_name'] = ap_name
                    tx_desc_stuck_time.append(ts_new)
                    apDict[ap]['tx_desc_stuck_times'] = tx_desc_stuck_time
                    apDict[ap]['tx_desc_stuck_count'] = len(tx_desc_stuck_time)
            
    
        if re.search('Busy',buff):     
            res13 =  re.findall(pattern13,buff)
        
            if res13:
                if ap not in apDict.keys():
                    apDict[ap] = {}
                    apDict[ap]['ap'] = ap
                    apDict[ap]['ip'] = ip
                    apDict[ap]['ap_name'] = ap_name
                apDict[ap]['2g_ch_util_Busy'] = res13[0][0]
                apDict[ap]['2g_ch_util_RX'] = res13[0][1]
                apDict[ap]['2g_ch_util_TX'] = res13[0][2]
                apDict[ap]['2g_ch_util_Total'] = res13[0][3]
                if len(res13) > 1:
                    apDict[ap]['5g_ch_util_Busy'] = res13[1][0]
                    apDict[ap]['5g_ch_util_RX'] = res13[1][1]
                    apDict[ap]['5g_ch_util_TX'] = res13[1][2]
                    apDict[ap]['5g_ch_util_Total'] = res13[1][3]

    ap_clientDict = {}    ### This is for saving client details for each AP
    ap_walDict = {}
    ap_switchDict = {}
    
    for f in logfilelist:
        
        ap = f.split('.')[-1]
        ap_mac = ap.replace('_',':').upper()
        if ap_mac in apmacDict.keys():
            ip = apmacDict[ap_mac]
            ap_name = apipDict[ip]
        else:
            ip = 'unknown'        

        ap_clientDict[ap] = {}
        ap_walDict[ap] = {}
        fp = open('writable/%s' % f,'r')
        buff = fp.read()
        res3 = re.findall(pattern3,buff)
        res4 = re.findall(pattern4,buff)
        #res5 = re.findall(pattern5,buff, re.DOTALL)
        res6 = re.findall(pattern6,buff)
        res7 = re.findall(pattern7,buff)

        g_ch_switch_count = 0
        a_ch_switch_count = 0
        if res3:
            for t in res3:

                ts_utc = t[0]
                ts_new = utc_localtime_conversion(year,ts_utc,todaydate)
                if ts_new:
                    if int(t[1]) == 0:
                        g_ch_switch_count += 1
                    elif int(t[1]) == 1:
                        a_ch_switch_count += 1
            if ap not in apDict.keys():
                apDict[ap] = {}
                apDict[ap]['ap'] = ap
                apDict[ap]['ip'] = ip
                apDict[ap]['ip'] = ip
            apDict[ap]['2g_ch_switch_count'] = g_ch_switch_count 
            apDict[ap]['5g_ch_switch_count'] = a_ch_switch_count 
        else:
            if ap not in apDict.keys():
                apDict[ap] = {}
                apDict[ap]['ap'] = ap
                apDict[ap]['ip'] = ip
                apDict[ap]['ip'] = ip
            apDict[ap]['2g_ch_switch_count'] = 0 
            apDict[ap]['5g_ch_switch_count'] = 0    
                                          


        if res7:
            for t in res7:
                ts_utc = t[0]
                ts = utc_localtime_conversion(year,ts_utc,todaydate)
                if ts:              
                    wlan = t[1]
                    station = t[2]
                    if station:
                        if station not in ap_clientDict.keys():
                            ap_clientDict[station] = {}
                        if ts not in ap_clientDict[station].keys():
                            ap_clientDict[station][ts] = {}    
                        #ap_clientDict[station][ts] = {}
                        ap_clientDict[station][ts]['ap'] = ap
                        ap_clientDict[station][ts]['ip'] = ip
                        ap_clientDict[station][ts]['ts'] = ts
                        ap_clientDict[station][ts]['action'] = 'Authentication Difficulty'
                        ap_clientDict[station][ts]['station'] = station
                        ap_clientDict[station][ts]['auth_difficult_wlan'] = wlan 
    

        if res6:
                print "\nParsing disassoc details "

                for t in res6:
                    ts_utc = t[0]
                    ts = utc_localtime_conversion(year,ts_utc,todaydate)
                    if ts:  
                        station = t[1]
                        if not station:
                            continue
                        if station not in ap_clientDict.keys():
                            ap_clientDict[station] = {}
                        if ts not in ap_clientDict[station].keys():
                            ap_clientDict[station][ts] = {}                            
                        #ap_clientDict[ap][ts] = {}
                        ap_clientDict[station][ts]['ap'] = ap 
                        ap_clientDict[station][ts]['ip'] = ip 
                        ap_clientDict[station][ts]['ts'] = ts 
                        ap_clientDict[station][ts]['ap_name'] = ap_name
                        ap_clientDict[station][ts]['action'] = 'disassoc'
                        ap_clientDict[station][ts]['station'] = t[1] 
                        ap_clientDict[station][ts]['hint'] = t[2] 
                        ap_clientDict[station][ts]['rx_rssi'] = t[3] 
                        ap_clientDict[station][ts]['ack_rssi'] = t[4] 
                        ap_clientDict[station][ts]['reason'] = t[5] 
                        ap_clientDict[station][ts]['freq'] = t[6] 
                        ap_clientDict[station][ts]['chan'] = t[7] 
                        ap_clientDict[station][ts]['stats'] = t[8] 
 
    #for channel number
    pattern80 = 'Current Channel=(\d+)'
    for f in wifi0list:
        
        ap = f.split('.')[-1]
        ap_mac = ap.replace('_',':').upper()
        if ap_mac in apmacDict.keys():
            ip = apmacDict[ap_mac]
            ap_name = apipDict[ip]
        else:
            ip = 'unknown'        

        fp = open('writable/%s' % f,'r')
        buff = fp.read()
        res80 = re.search(pattern80,buff)
        if res80:
            gchannel = res80.group(1)
        
            if ap not in apDict.keys():
                apDict[ap] = {}
                apDict[ap]['ap'] = ap
                apDict[ap]['ip'] = ip
                apDict[ap]['ap_name'] = ap_name
            apDict[ap]['2g_channel'] = gchannel  
            
    for f in wifi1list:

        ap = f.split('.')[-1]
        ap_mac = ap.replace('_',':').upper()
        if ap_mac in apmacDict.keys():
            ip = apmacDict[ap_mac]
            ap_name = apipDict[ip]
        else:
            ip = 'unknown'        

        fp = open('writable/%s' % f,'r')
        buff = fp.read()
        res80 = re.search(pattern80,buff)
        if res80:
            achannel = res80.group(1)

            if ap not in apDict.keys():
                apDict[ap] = {}
                apDict[ap]['ap'] = ap
                apDict[ap]['ip'] = ip
                apDict[ap]['ap_name'] = ap_name
            apDict[ap]['5g_channel'] = achannel      
 
    ### This gets the roaming details
    #Apr 28 08:05:19 density-zd3k.video54.local syslog: eventd_to_syslog():AP[R710-Breakroom@d4:68:4d:1a:1f:30] radio [11a/n/ac] detects User[yvette.guzman@84:38:35:ed:bd:dc] in WLAN[DENSITY] roams from AP[R710_WestPatio_cube144@84:18:3a:3f:90:10]
    #pattern22 = "([a-zA-Z]+\s+\d+\s+[\d:]+)\s+.*?AP.*?radio/s+(.*?)detects\s+User\s+(.*?)\s+in"
    #pattern9 ="([a-zA-Z]+\s+\d+\s+[\d:]+)\s+.*?eventd_to_syslog\(\):AP\s+.*?@(.*?)\s+joins.*?Heartbeat\s+Loss"
    #May  1 19:25:52 Density-ZD3K syslog: eventd_to_syslog():User[frank@e4:98:d6:1a:e0:9a] leave WLAN[DENSITY] at AP[R710_Dalmatian_CR@84:18:3a:3f:90:c0] with Session Time[35.44 sec] RX Bytes[5035] TX Bytes[101580]
    pattern22 = "([a-zA-Z]+\s+\d+\s+[\d:]+)\s+.*?radio\s+(.*?)detects\s+User\s+(.*?)\s+in.*?roams from\s+"
    #pattern23 = "([a-zA-Z]+\s+\d+\s+[\d:]+)\s+.*?User\s+(.*?)\s+leave\s+.*?with\s+Session\s+Time\s+(.*?)\s+sec\s+RX\s+Bytes\s+(\d+)\s+TX\s+Bytes(\d+)\s+"
    pattern23 = "([a-zA-Z]+\s+\d+\s+[\d:]+)\s+.*?User\s+(.*?)\s+leave\s+.*?with\s+Session\s+Time\s+(.*?)\s+sec\s+RX\s+Bytes\s+(\d+)\s+TX\s+Bytes\s+(\d+)"
    tdate = get_todaydate_aplog()    

    ### reading the ap.log file and grep only reboot and heartbeat
    c_dir = os.getcwd() 
    #print c_dir
    cmd1 = 'gunzip -c %s/allmessages.gz > %s/all.txt' % (c_dir,c_dir)
    cmd2 = 'sort %s/all.txt |uniq -u > %s/new.txt' % (c_dir,c_dir)
    os.system(cmd1)
    os.system(cmd2)
    os.system('cat %s/all.txt |grep -i "roams from" | grep \"%s\" > roaming' % (c_dir,tdate))
    os.system('cat %s/all.txt |grep -i "with Session Time" | grep \"%s\" > leaving' % (c_dir,tdate))
    ## parsing the YX/RX bytes
    fp_input = open("leaving" , "r")
    for line in fp_input.readlines():
    
        line = line.replace('[',' ').replace(']',' ').rstrip()
        #print line
        res23 = re.search(pattern23,line)
            
        if res23:      
            ts = res23.group(1)
            elapsed_time = res23.group(3)
            station = res23.group(2) 
            rx_bytes = res23.group(4)
            tx_bytes = res23.group(5)
            total_bytes = int(rx_bytes)+ int(tx_bytes)
            if not station:
                continue            
            st_list = station.split('@')
            if len(st_list) == 2:
                station_name = station.split('@')[0]
                station_mac = station.split('@')[1]
            else:
                station_mac = station
                station_name = ''
            if station_mac not in ap_clientDict.keys():
                ap_clientDict[station_mac] = {}
            if ts not in ap_clientDict[station_mac].keys():
                ap_clientDict[station_mac][ts] = {}                            
            ap_clientDict[station_mac][ts]['ts'] = ts                 
            ap_clientDict[station_mac][ts]['action'] = 'leaving'
            ap_clientDict[station_mac][ts]['station'] = station_mac 
            ap_clientDict[station_mac][ts]['name'] = station_name 
            ap_clientDict[station_mac][ts]['elapsed_time_sec'] = elapsed_time
            ap_clientDict[station_mac][ts]['total_bytes'] = total_bytes
            #ap_clientDict[station_mac][ts]['tx_bytes'] = tx_bytes
                
    
    fp_input = open("roaming" , "r")

    for line in fp_input.readlines():

        line = line.replace('[',' ').replace(']',' ')
        #print line
        res22 = re.search(pattern22,line)
        
        if res22: 
            #print res22
            ts = res22.group(1)
            radio = res22.group(2)
            station = res22.group(3)
            if not station:
                continue            
            st_list = station.split('@')
            if len(st_list) == 2:
                station_name = station.split('@')[0]
                station_mac = station.split('@')[1]
            else:
                station_mac = station
                station_name = ''
            if station_mac not in ap_clientDict.keys():
                ap_clientDict[station_mac] = {}
            if ts not in ap_clientDict[station_mac].keys():
                ap_clientDict[station_mac][ts] = {}                            
            #ap_clientDict[station][ts] = {}

            ap_clientDict[station_mac][ts]['ts'] = ts 

            #ap_clientDict[ap][ts]['ap_name'] = ap_name
            ap_clientDict[station_mac][ts]['action'] = 'roaming'
            ap_clientDict[station_mac][ts]['station'] = station_mac 
            ap_clientDict[station_mac][ts]['name'] = station_name 
            ap_clientDict[station_mac][ts]['radio'] = radio
             
            
            
    (apDict,email_flag,heartbeat_ap_list) = ap_reboot_dict(timestamp,email_flag,apDict,message_fp,heartbeat_ap_list) 
    #print apDict
    #print ap_clientDict 
    #os.system('rm writable/datafile*')
    #os.system('rm -r writable')

    (csv1,csv2) = csvfile_writer(apDict,ap_clientDict,timestamp)
    #copying the ap_stats file to hourly_stats.csv file for air utilization stats run by parser_for_hourly_stats.py
    fname = "hourly_stats.csv"
    os.system('cp %s %s' % (csv1,fname))
    #csv3 = apStatsSum(fname)
    #print ap_walDict
    #csv3 = walcsv_writer(ap_walDict,timestamp)
    #csv4 = switchcsv_writer(ap_switchDict,timestamp)
    #get_client_count(csv1,timestamp)
    #return(csv1,csv2,csv3,csv4,email_flag,heartbeat_ap_list)
    return(csv1,csv2,email_flag,heartbeat_ap_list,txdescstuck_ap_list)
             
if  __name__ =='__main__':
 
    year = get_year()
    file_parser()
