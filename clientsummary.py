#!/usr/bin/python
import csv
import fileinput
import os,sys
import pandas as pd
import subprocess
import zdcli
current_dir = '/home/wspbackup/newdir/latestscript'

def summary_writer(cntDict,dtype):
    
    #os.chdir('/var/www/densitystatus/dailystatus')
    os.chdir('%s' % report_dir)
    cwd = os.getcwd()
    print cwd
    client_csvfilename = '%s/top10_ap_for_%s_count.csv' % (report_dir,dtype) 

    try:
        staCsvPtr= open('%s' % client_csvfilename,"wb")
    except IOError:
        print "cannot open CSV file, exiting\n"
    if dtype == "g_channel_totalutilization" or dtype == "a_channel_totalutilization":
        fieldnames = ['ap', 'Total','Busy', 'RX', 'TX']
    else:
        fieldnames = ['ap', '%s_count' % type]
        
    dwriter= csv.writer(staCsvPtr,fieldnames, delimiter= ',')

    staCsvPtr.write(','.join(fieldnames)+'\r\n')
    for k,v in sorted(cntDict.iteritems(), key = lambda(k,v):int(v), reverse=True):

        dwriter.writerow((k,v))
    staCsvPtr.close()
    
def client_summary_writer(staDict):
    print staDict
    #os.chdir('/var/www/densitystatus/dailystatus')
    os.chdir('%s' % report_dir)
    cwd = os.getcwd()
    print cwd
    client_csvfilename = '%s/clientsummary.csv' % (report_dir)

    try:
        staCsvPtr= open('%s' % client_csvfilename,"wb")
    except IOError:
        print "cannot open CSV file, exiting\n"

    fieldnames = ['mac', 'ts','action']
    dwriter= csv.DictWriter(staCsvPtr,fieldnames, dialect = 'excel', delimiter= ',', extrasaction='ignore')

    staCsvPtr.write(','.join(fieldnames)+'\r\n')
    for mac in staDict.iterkeys():
        for ts in sorted(staDict[mac].iterkeys()):
            dwriter.writerow(staDict[mac][ts])

    staCsvPtr.close()

def daily_summary_writer(cntDict):
    
    #os.chdir('/var/www/densitystatus/dailystatus')
    os.chdir('%s' % report_dir)
    cwd = os.getcwd()
    print cwd
    csvname = "%s/summary.csv" % report_dir

    try:
        staCsvPtr= open('%s' % csvname,"wb")
    except IOError:
        print "cannot open CSV file, exiting\n"

    #fieldnames = ['item', 'value'] 
    dwriter= csv.writer(staCsvPtr, delimiter= ',')

    #staCsvPtr.write(','.join(fieldnames)+'\r\n')  
    for k,v in sorted(cntDict.iteritems()):
    #for k,v in (cntDict.iteritems(), key = lambda(k,v):int(v), reverse=True):
        dwriter.writerow((k,v))
    staCsvPtr.close()

def utility_writer(utilitylist,dtype):
    #os.chdir('/var/www/densitystatus/dailystatus')
    os.chdir('%s' % report_dir)
    cwd = os.getcwd()
    print cwd
    csvname = "%s/top10_aps_for_utilization_%s.csv" % (report_dir,dtype)

    try:
        staCsvPtr= open('%s' % csvname,"wb")
    except IOError:
        print "cannot open CSV file, exiting\n"

    fieldnames = ['ap', 'Total','Busy', 'RX', 'TX']
    dwriter= csv.writer(staCsvPtr,fieldnames, delimiter= ',')

    staCsvPtr.write(','.join(fieldnames)+'\r\n')  
    for item in utilitylist[:10]:
        #print item
        dwriter.writerow(item)
    staCsvPtr.close()
    
def get_client(ap_client_tuple):
    return ap_client_tuple[1]

def get_date():
    cmd = 'date -d "yesterday 13:00" \'+%b %d\''
    #cmd = 'date -d "today" \'+%b %d\''
    mydate = os.popen(cmd).read()
    if mydate[4] == '0':
        newdate = (mydate[:4]+' '+mydate[5]).rstrip()
    else:
        newdate = mydate.rstrip()
    return newdate    

def ap_detail():
    names = pd.read_csv('%s/ap_mac_ip_name.csv' % working_dir)
    aps = names[['apip','apname']]
    #print aps.values
    ap_ip_list = [] 
    newDict = {}
    for i in range (0,len(aps)):
        ap_ip_list.append(aps['apip'][i])
        newDict[aps['apip'][i]] = aps['apname'][i]
    return ap_ip_list,newDict    

def get_zd_details(working_dir):
    iniDict = {}
    with open('%s/initialize_file' % working_dir,'r') as ini_fp:
        for line in ini_fp:
            ini_list = line.split()
            iniDict["%s" % ini_list[0]] = ini_list[1].rstrip()
    return iniDict

def weekly_summary_writer(new_date):

    ### The following add the header line to the AP csv file
    headers =['item','value']
    f1 = "summary.csv"
    f2 = "summary_new.csv"
    cmd = "cp %s/%s %s/%s" % (report_dir,f1,report_dir,f2)
    os.system(cmd)
    nf = "%s/summary_new.csv" % (report_dir)
    if os.stat("%s"  % nf).st_size == 0 :
        return
    for line in fileinput.input(['%s' % nf], inplace=True):

        if fileinput.isfirstline():
            print','.join(headers)
            print line.rstrip()
        else:
            print line.rstrip()

    #reading the new summary.csv file
    #df = pd.read_csv("%s/summary.csv" % report_dir)
    df = pd.read_csv("%s" % nf)
    print df.values
    # the following gives the data, summary.csv is with two colums , type and value
    today_data = df['value']
    #print today_data.values
    ## the following reads the existing weeksummary.csv file
    df_org = pd.read_csv("%s/weekSummary.csv" % report_dir)
    print df_org.values
    ## inserting( or adding) the new column as column 1   df.insert(column_no, column_heading, values as a Series)
    df_org.insert(1,'%s' % new_date ,today_data)
    #print df_org.values
    #This gets the header ( column names in a list)
    clist = list(df_org.columns)
    print clist
    ## deleting the last column ,  df.drop(column_name,axis)
    tt = df_org.drop(clist[-1],1)
    ## removing the name of the dropped column name from the list
    nclist = clist[:-1]
    ## index =False to aviod the row index in the csv file
    tt.to_csv('%s/weekSummary.csv' % report_dir, header=True,cols=nclist,index=False)


def apStatsSort(newdate,summaryDict):
    ap_ip_list,newDict = ap_detail()
    headers = 'ap,ip,ap_name,uptime,g_client_count,a_client_count,cpuUse,per_memoryUsage,2g_ch_switch_count,5g_ch_switch_count,heartbeatlost_count,heartbeatlost_time,reboot_count,reboot_reason,target_assert_count,target_assert_times,wmi_stuck_count,wmi_lasttime_reported,target_inactive_count,target_inactive_times,beacon_stuck,2g_ch_util_Busy,2g_ch_util_RX,2g_ch_util_TX,2g_ch_util_Total,5g_ch_util_Busy,5g_ch_util_RX,5g_ch_util_TX,5g_ch_util_Total'.split()

    #get all the files  from apstats
    os.chdir('%s' % apstats_dir)
    cwd = os.getcwd()
    print cwd
    fname = "%s/ap_file.csv" % apstats_dir 
    filelist = []
    ###  the following get the list of files created previous day  to ap_file.csv
    
    os.system('ls -l |grep "%s" > %s' % (newdate, fname))
    
    dDict = {}
    fp = open('%s' % fname,'r')
    ### the following get the name of the files in to a list from ap_file.csv
    if (os.stat("%s" % fname).st_size == 0):
        print "No stats files are saved for %s, exiting" % newdate
        sys.exit(1)
    for line in fp:
        fname = line.split()[-1]
        if not fname.startswith('ap_stats_'):
            continue
        filelist.append(fname)
    print len(filelist)
    peak_g_client_list = []  
    peak_a_client_list = [] 
    ### This gets the peak client count
    for f in filelist:
        df = pd.read_csv('%s/%s' % (apstats_dir,f))
        g_sum = df['g_client_count'].sum() 
        a_sum = df['a_client_count'].sum() 
        peak_g_client_list.append(g_sum)
        peak_a_client_list.append(a_sum)
    peak_g_users = max(peak_g_client_list)
    peak_a_users = max(peak_a_client_list)
    ### the following creats a seperate file for each AP collecting the corresponding line from each csv file
    #os.system('rm -f %s/ap_file*' % apstats_dir)
    for ip in ap_ip_list:
        client_count = 0
        finame = "%s/ap_file_%s.csv" % (apstats_dir,ip) 
        for f in filelist:
            #cmd = 'cat /var/www/densitystatus/apstats/%s |grep %s >> %s' % (f,ip,finame) 
            cmd = 'cat %s/%s |grep %s >> %s' % (apstats_dir,f,ip,finame)
            os.system(cmd)

        ### The following add the header line to the AP csv file
        nf = "%s/ap_file_%s.csv" % (apstats_dir,ip)
        if os.stat("%s"  % nf).st_size == 0 :
            continue
        for line in fileinput.input(['%s' % nf], inplace=True):
            
            if fileinput.isfirstline():
                print','.join(headers)
                
            else:
                print line.rstrip()  
        ap = ip
        dDict[ap] = {}
        dDict[ap]['ap'] = ap
    
        ### the following  copies the csv file toa pandas DataFrame
    
        x = pd.read_csv('%s' % nf)
    
        ### The following gets the required columns to y
        #y = x[['2g_client_count']] 
        gclient_count_item = []
        aclient_count_item = []
        
        y =  x[['g_client_count','a_client_count','2g_ch_switch_count','5g_ch_switch_count','reboot_count','heartbeatlost_count','cpuUse','per_memoryUsage']]
        yy = y.fillna(0)       
        for d in ['g_client_count','a_client_count','2g_ch_switch_count','5g_ch_switch_count','reboot_count','heartbeatlost_count','cpuUse','per_memoryUsage']:
            d_count = 0
            df3 = yy['%s' % d] 
            dDict[ap]['%s' % d] = df3.max()
            d_count = 0
            '''df = y.sort('%s' % d,ascending=False)
            #d_count = max(df['%s' % d][i] for i in range(len(df)))
            #print df.values
            if df.all:
            
                if d_count < (df['%s' % d][1]):
                    d_count = int(df['%s' % d][1])
            
            dDict[ap]['%s' % d] = d_count  ''' 

        #print dDict[ap]
    
        df_gg = x[['2g_ch_util_Busy','2g_ch_util_RX','2g_ch_util_TX','2g_ch_util_Total']]
        df_aa = x[['5g_ch_util_Busy','5g_ch_util_RX','5g_ch_util_TX','5g_ch_util_Total']]
        #print df_g.values
        '''df_gg.convert_objects(convert_numeric=True)
        df_gg.replace('%','',regex=True).astype('float')
        df_g = df_gg.astype(float).fillna(0.0)
        df_a = df_aa.astype(float).fillna(0.0)'''
        df_g =df_gg.fillna(0)
        #print asd.values
        df_a =df_aa.fillna(0)
  
        print df_g.values
        print df_a.values
        util_max_list_g = df_g.ix[df_g['2g_ch_util_Total'].idxmax()]
        util_max_list_a = df_a.ix[df_a['5g_ch_util_Total'].idxmax()]
        
        dDict[ap]['2g_ch_util_Total'] = util_max_list_g['2g_ch_util_Total']
        dDict[ap]['2g_ch_util_Busy'] = util_max_list_g['2g_ch_util_Busy']
        dDict[ap]['2g_ch_util_RX'] = util_max_list_g['2g_ch_util_RX']
        dDict[ap]['2g_ch_util_TX'] = util_max_list_g['2g_ch_util_TX']   
        
        dDict[ap]['5g_ch_util_Total'] = util_max_list_a['5g_ch_util_Total']
        dDict[ap]['5g_ch_util_Busy'] = util_max_list_a['5g_ch_util_Busy']
        dDict[ap]['5g_ch_util_RX'] = util_max_list_a['5g_ch_util_RX']
        dDict[ap]['5g_ch_util_TX'] = util_max_list_a['5g_ch_util_TX']              
    
    os.system('rm -f %s/ap_file*' % apstats_dir)
    gclientDict = {}
    gclientDict["data"] = [] 
    rebootDict = {}
    rebootDict["data"] = []
    aclientDict = {}
    aclientDict["data"] = [] 
    gchannelswitchDict = {}
    gchannelswitchDict["data"] = [] 
    achannelswitchDict = {}
    achannelswitchDict["data"] = [] 
    beatDict = {}
    beatDict["data"] = [] 
    gchannelutilDict = {}
    gchannelutilDict["data"] =[] 
    achannelutilDict = {}
    achannelutilDict["data"] =[] 
    cpuDict = {}
    cpuDict["data"] = []
    memDict = {}
    memDict["data"] = []
    
    for ap in dDict.keys():
        if ap in newDict.keys():
            name = newDict[ap]
        else:
            name = ap
        print dDict[ap]['g_client_count']
        gclientDict["data"].append((name,dDict[ap]['g_client_count']))
        aclientDict["data"].append((name,dDict[ap]['a_client_count']))
        gchannelswitchDict["data"].append((name,dDict[ap]['2g_ch_switch_count']))
        achannelswitchDict["data"].append((name,dDict[ap]['5g_ch_switch_count']))
        beatDict["data"].append((name,dDict[ap]['heartbeatlost_count']))
        rebootDict["data"].append((name,dDict[ap]['reboot_count']))
        cpuDict["data"].append((name,dDict[ap]['cpuUse']))
        memDict["data"].append((name,dDict[ap]['per_memoryUsage']))
        
        gchannelutilDict["data"].append((name,dDict[ap]['2g_ch_util_Total'],dDict[ap]['2g_ch_util_Busy'],dDict[ap]['2g_ch_util_TX'],dDict[ap]['2g_ch_util_RX']))
        achannelutilDict["data"].append((name,dDict[ap]['5g_ch_util_Total'],dDict[ap]['5g_ch_util_Busy'],dDict[ap]['5g_ch_util_TX'],dDict[ap]['5g_ch_util_RX'])) 
    gclient_items = sorted(gclientDict["data"], key=get_client, reverse=True)
    aclient_items = sorted(aclientDict["data"], key=get_client, reverse=True)
    gch_switch_items = sorted(gchannelswitchDict["data"], key=get_client, reverse=True)
    ach_switch_items = sorted(achannelswitchDict["data"], key=get_client, reverse=True)
    beat_items = sorted(beatDict["data"], key=get_client, reverse=True)
    reboot_items = sorted(rebootDict["data"], key=get_client, reverse=True)
    cpu_items = sorted(cpuDict["data"], key=get_client, reverse=True)
    mem_items = sorted(memDict["data"], key=get_client, reverse=True)
    gch_util_items = sorted(gchannelutilDict["data"], key=get_client, reverse=True)
    ach_util_items = sorted(achannelutilDict["data"], key=get_client, reverse=True) 
    memCount = 0
    cpuCount = 0    
    for item in cpu_items:
        if int(item[1]) > 75:
            cpuCount +=1
    for item in mem_items:
        if int(item[1]) > 75:
            memCount += 1
    gclient_final = {}
    aclient_final = {}
    gch_switch_final = {}
    ach_switch_final = {}
    beat_final = {}
    gch_util_final = {}
    ach_util_final = {}
    for item in gclient_items[:10]:
        gclient_final[item[0]] = item[1]
    for item in aclient_items[:10]:
        aclient_final[item[0]] = item[1]
    for item in gch_switch_items[:10]:
        gch_switch_final[item[0]] = item[1]
    for item in ach_switch_items[:10]:
        ach_switch_final[item[0]] = item[1]
    for item in beat_items[:10]:
        beat_final[item[0]] = item[1]
    for item in gch_util_items[:10]:
        gch_util_final[item[0]] = item[1]
    for item in ach_util_items[:10]:
        ach_util_final[item[0]] = item[1] 
    summary_writer(gclient_final, "gclient")
    summary_writer(aclient_final, "aclient")
    summary_writer(gch_switch_final,"g_channel_switch")
    summary_writer(ach_switch_final,"a_channel_switch")
    summary_writer(beat_final,"heartbeatloss")
    #summary_writer(gch_util_final,"g_channel_totalutilization")
    #summary_writer(ach_util_final,"a_channel_totalutilization")  
    utility_writer(ach_util_items,"5g")
    utility_writer(gch_util_items,"2g")
    heartbeatsum = sum(beat_items[i][1] for i in range(len(beat_items)))
    rebootsum = sum(reboot_items[i][1] for i in range(len(reboot_items)))
    print heartbeatsum
    print rebootsum
    gchannelswitchsum = sum(gch_switch_items[i][1] for i in range(len(gch_switch_items)))
    achannelswitchsum = sum(ach_switch_items[i][1] for i in range(len(ach_switch_items)))
    summaryDict['Peak Users (2.4Ghz)'] = int(peak_g_users)
    summaryDict['Peak Users (5GHz)'] = int(peak_a_users)
    summaryDict['Total Number of ap Reboots'] = int(rebootsum)
    summaryDict['Total Number of heartbeat Loss'] = int(heartbeatsum)
    #summaryDict['Total Number of Unique clients'] = len(client_list)
    summaryDict['Total Number of 2 Ghz Channel Changes'] = int(gchannelswitchsum)
    summaryDict['Total Number of 5 Ghz Channel Changes'] = int(achannelswitchsum)    
    summaryDict['Number of APs with CPU utilization > 75%'] = int(cpuCount)
    summaryDict['Number of APs with memory usage > 80%'] = int(memCount)
    return summaryDict
def clientSort(newdate,summaryDict):
    #new_date = get_date()  
    os.chdir('%s' % clientstats_dir)
    cwd = os.getcwd()
    print cwd        
    headers = 'ap,ip,ts,action,station,roam_from_ap,roam_to_ap,auth_difficult_wlan,hint,rx_rssi,ack_rssi,reason,freq,chan,stats'.split()
    fname = "%s/client_file.csv" % clientstats_dir
    filelist = []
    ###  the following get the list of files created previous day  to client_file.csv
    
    os.system('ls -l |grep "%s" > %s' % (newdate, fname))
    
    fp = open('%s' % fname,'r')
    ### the following get the name of the files in to a list from client_file.csv
    
    for line in fp:
        fname = line.split()[-1]
        if not fname.startswith('client_stats_'):
            continue
        filelist.append(fname)
    #print len(filelist)
    #print filelist 
    dDict = {}
    
    ### the following creats a seperate file for each AP collecting the corresponding line from each csv file
    for f in filelist:
        x = pd.read_csv('%s' % f)
    
        ### The following gets the required columns to y
        y =  x[['ts','action','station']]
        df = y.sort(['station','ts','action'])
        #print df.values
        for i in range(0,len(df)):
            ts = df['ts'][i].split('/')[-1]
            mac = df['station'][i]
            action = df['action'][i]
    
            if mac not in dDict.keys():
                dDict[mac] = {}
            if ts not in dDict[mac].keys():
                dDict[mac][ts] = {}
               
            dDict[mac][ts]['action'] = action 
            dDict[mac][ts]['ts'] = ts
            dDict[mac][ts]['mac'] = mac
    client_summary_writer(dDict)                
    client_list = dDict.keys()
    print len(client_list)
    
    count = 0
    ts_list = []
    '''for ts in dDict['3c:a9:f4:09:0b:58'].keys():
        count +=1
        ts_list.append(ts)
        #print dDict['78:31:c1:58:1f:61'][client_filets]['action']
    print "count =  ", count
    print len(ts_list)
    new_list = list(set(ts_list))
    print len(new_list)  '''
    
    countDict = {}
    for mac in dDict.keys():
        countDict[mac] = {}
        countDict[mac]['disassoc_count'] = 0
        countDict[mac]['roaming_count'] = 0
        countDict[mac]['authdifficulty_count'] = 0
    
        for ts in dDict[mac].keys():
            if dDict[mac][ts]['action'] == 'disassoc':
                countDict[mac]['disassoc_count'] += 1
            elif dDict[mac][ts]['action'] == 'roaming':
                countDict[mac]['roaming_count'] += 1
            elif dDict[mac][ts]['action'] == 'Authentication Difficulty':
                countDict[mac]['authdifficulty_count'] += 1
     
    
    disassocDict = {}
    disassocDict["data"] = []
    roamingDict = {}
    roamingDict["data"] = []
    authdifficultyDict = {}
    authdifficultyDict["data"] = []
     
    for mac in countDict.keys():
        disassocDict["data"].append((mac,countDict[mac]['disassoc_count']))
        roamingDict["data"].append((mac,countDict[mac]['roaming_count']))
        authdifficultyDict["data"].append((mac,countDict[mac]['authdifficulty_count']))
    
    disassoclist = sorted(disassocDict["data"], key=get_client, reverse=True) 
    roaminglist = sorted(roamingDict["data"], key=get_client, reverse=True) 
    authdifficultylist = sorted(authdifficultyDict["data"], key=get_client, reverse=True)  
    nlist = []
    mlist = []
    rlist,alist, dlist = [],[],[]
    for r in roaminglist[:3]:
        rlist.append(r[0])
        nlist.append(r[1])
    for i in range(len(rlist)):
        mlist.append(rlist[i]+'('+str(nlist[i])+')')
        
    rslist= "   ".join(mlist)
    #nrlist = str(rlist)
    nlist = []
    mlist = []    
    for a in authdifficultylist[:3]:
        alist.append(a[0])
        nlist.append(a[1])
        
    for i in range(len(alist)):
        mlist.append(alist[i]+'('+str(nlist[i])+')')    
    aslist= "   ".join(mlist) 
    
    nlist = []
    mlist = []       
    
    for d in disassoclist[:3]:
        dlist.append(d[0])
        nlist.append(d[1])
    for i in range(len(dlist)):
        mlist.append(dlist[i]+'('+str(nlist[i])+')')     
    dslist= "   ".join(mlist)
    #print "dlist", dslist
    
    #print authdifficultylist
    disassocfinalDict = {}
    roamingfinalDict = {}
    authdifficultyfinalDict = {}
    
    for item in disassoclist[:10]:
        disassocfinalDict[item[0]] = item[1]
    
    for item in roaminglist[:10]:
        roamingfinalDict[item[0]] = item[1]
    
    for item in authdifficultylist[:10]:
        authdifficultyfinalDict[item[0]] = item[1]
    
    summary_writer(disassocfinalDict, "clientdisassoc")
    summary_writer(roamingfinalDict, "clientroaming")
    summary_writer(authdifficultyfinalDict, "client_auth_difficulty")
    authdifficultysum = sum(authdifficultylist[i][1] for i in range(len(authdifficultylist)))
    roamingsum = sum(roaminglist[i][1] for i in range(len(roaminglist)))
    disassocsum = sum(disassoclist[i][1] for i in range(len(disassoclist)))
    print authdifficultysum, roamingsum, disassocsum
    summaryDict['Total Number of Authetication Difficulty'] = int(authdifficultysum)
    summaryDict['Total Number of Client Roaming'] = int(roamingsum)
    summaryDict['Total Number of Client Disassoc'] = int(disassocsum)

    summaryDict['Top3 clients with maximum number of Disassoc '] = dslist
    summaryDict['Top3 clients with maximum number of Authentication Difficulty '] = aslist
    summaryDict['Top3 clients with maximum number of roaming '] = rslist  
    os.system('rm -f %s/ap_file*' % apstats_dir)
    os.system('rm -f %s/client_file*' % clientstats_dir)    
    return summaryDict
def clientCapabilitySort(newdate):
    
    headers = ['client','org','client_rssi','client_capability','ap_ip']
    #new_date = get_date()   
    os.chdir('%s' % capabilitystats_dir)
    cwd = os.getcwd()
    print cwd    
    fname = "%s/client_file.csv" % working_dir
    filelist = []
    ###  the following get the list of files created previous day  to client_file.csv
    
    os.system('ls -l |grep "%s" > %s' % (newdate, fname))
    
    fp = open('%s' % fname,'r')
    ### the following get the name of th        
    for line in fp:
        fname = line.split()[-1]
        if not fname.startswith('client_capability_'):
            continue
        filelist.append(fname)
    print len(filelist)
    dDict = {}
    
    ### the following creats a seperate file for each AP collecting the corresponding line from each csv file
    for f in filelist:
        x = pd.read_csv('%s' % f)
    
        ### The following gets the required columns to y
        df =  x[['client','org']]
        for i in range(0,len(df)):
            mac = df['client'][i]
            org = df['org'][i]
    
            if mac not in dDict.keys():
                dDict[mac] = {}
               
            dDict[mac]['org'] = org 
    client_list = dDict.keys()
    print len(client_list)
    macDict = {}
    
    for mac in dDict.keys():
        org = dDict[mac]['org']
        x =  org.split(' ')
        y = x[0].split(',')
    
        org =y[0].upper()
        if org in macDict.keys():
            macDict[org]['count'] += 1
            macDict[org][mac] = mac
        else:
            macDict[org] = {}
            macDict[org]['count'] = 1
            macDict[org][mac] = mac
    
    sortDict = {}
    sortDict["data"] =  []
    for org in macDict.keys():
        sortDict["data"].append((org,macDict[org]['count']))
    client_distr_list = sorted(sortDict["data"], key=get_client, reverse=True) 
    print client_distr_list
        
    distrDict = {}
    for item in client_distr_list[:10]:
        distrDict[item[0]] = item[1]
    summary_writer(distrDict, "clientdistribution")

if __name__ =='__main__':      

    summaryDict = {}
    new_date = get_date()
    #current_dir = os.getcwd()
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
        http_server = zdDict['http_addr']
    else:
        print "Not able to get ZD details, make sure to update details in  initilize_file, exiting"
        sys.exit(1)    

    '''zd = zdcli.ZDCLI(zd_ip)
    zd.connect(zduser, zdpass, timeout=3600,sesame_key="!v54!")
    #zd.to_shell()
    version = zd.get_zd_version()
    zd.close() 
    print version '''
    summaryDict['D image'] = '9.12.0.0.212'  
    #summaryDict['ZD image'] = version.rstrip()   
    summaryDict = apStatsSort(new_date,summaryDict)
    summaryDict = clientSort(new_date,summaryDict)

    #daily_summary_writer(summaryDict)
    #weekly_summary_writer(new_date)   
    #cmd = 'date -d "yesterday 13:00" \'+%b %d\''
    cmd = 'date -d "yesterday" \'+%m/%d/%Y\''
    mydate = os.popen(cmd).read() 
    message_fp = open('%s/dailymessage' % working_dir,'w')
    message_fp.write('DENSITY network daily report for %s is available in the following URL:\n\n' % mydate)
    #message_fp.write('http://10.150.13.7/densitystatus/dailystatus/test.html')                     
    message_fp.write('http://%s/%s/test.html' % (http_server,html_dir))
    message_fp.close()
    #subprocess.call(['%s/daily_density_email.sh' % working_dir]) 
