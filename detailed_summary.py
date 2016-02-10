#!/usr/bin/python
import csv
import fileinput
import os,sys
import pandas as pd
import subprocess
import zdcli
current_dir = '/home/rms/density_rms'


cmd = 'date -d "today" \'+%b %d\''
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

    fieldnames = ['ap', 'Total','Busy', 'TX', 'RX']
    dwriter= csv.writer(staCsvPtr,fieldnames, delimiter= ',')

    staCsvPtr.write(','.join(fieldnames)+'\r\n')  
    for item in utilitylist[:10]:
        #print item
        dwriter.writerow(item)
    staCsvPtr.close()

def airutility_writer(utilitylist,dtype,wing):
    #os.chdir('/var/www/densitystatus/dailystatus')
    os.chdir('%s' % report_dir)
    cwd = os.getcwd()
    print cwd
    csvname = "%s/daily_air_utilization_%s_%s.csv" % (report_dir,dtype,wing)
    file_exists = os.path.isfile(csvname)
    try:
        staCsvPtr= open('%s' % csvname,"ab")
    except IOError:
        print "cannot open CSV file, exiting\n"
        sys.exit(1)
    fieldnames = ['newDate', '(%) Daily average (Total) air Utilization']
    dwriter= csv.writer(staCsvPtr,fieldnames, delimiter= ',')
    
    if file_exists:
        dwriter.writerow(utilitylist)
    else:

        staCsvPtr.write(','.join(fieldnames)+'\r\n')  
        dwriter.writerow(utilitylist)
    
    staCsvPtr.close()
    
def channel_utility_writer(chDict,newdate):
    #os.chdir('/var/www/densitystatus/dailystatus')
    os.chdir('%s' % report_dir)
    cwd = os.getcwd()
    print cwd
    csvname = "%s/channel_utilization.csv" % (report_dir)

    try:
        csvPtr= open('%s' % csvname,"wb")
    except IOError:
        print "cannot open CSV file, exiting\n"

    fieldnames = ['channel', 'avg_channel_util']
    dwriter= csv.DictWriter(csvPtr,fieldnames, dialect = 'excel', delimiter= ',', extrasaction='ignore')

    csvPtr.write(','.join(fieldnames)+'\r\n')  
    for key in sorted(chDict.keys()):
        #print item
        list
        dwriter.writerow(chDict[key])
    csvPtr.close()
def newairutility_writer(utilitylist):
    #os.chdir('/var/www/densitystatus/dailystatus')
    os.chdir('%s' % report_dir)
    cwd = os.getcwd()
    print cwd
    csvname = "%s/daily_air_utilization.csv" % (report_dir)
    file_exists = os.path.isfile(csvname)
    try:
        staCsvPtr= open('%s' % csvname,"ab")
    except IOError:
        print "cannot open CSV file, exiting\n"
        sys.exit(1)
    fieldnames = ['newDate', '2.4 GHz East Wing','5 GHz East Wing','2.4 GHz West Wing','5 GHz West Wing']
    dwriter= csv.writer(staCsvPtr,fieldnames, delimiter= ',')
    
    if file_exists:
        dwriter.writerow(utilitylist)
    else:

        staCsvPtr.write(','.join(fieldnames)+'\r\n')  
        dwriter.writerow(utilitylist)
    
    staCsvPtr.close()
    
def get_client(ap_client_tuple):
    return ap_client_tuple[1]
def get_year():
    cmd = 'date -d "yesterday 13:00" \'+%Y %b %d\''
    mydate = os.popen(cmd).read()
    current_year = mydate.split()[0]

    return current_year   

def get_date():
    #cmd = 'date -d "Today" \'+%b %d\''
    cmd = 'date -d "yesterday 13:00" \'+%b %d\''
    #cmd = 'date -d "2 days ago" \'+%b %d\''
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
    #print df.values
    # the following gives the data, summary.csv is with two colums , type and value
    today_data = df['value']
    #print today_data.values
    ## the following reads the existing weeksummary.csv file
    df_org = pd.read_csv("%s/weekSummary.csv" % report_dir)
    #print df_org.values
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
    
def weekly_airUtilization_writer(new_date):
    
        ### The following add the header line to the AP csv file
        headers =['channel','avg_channel_util']
        f1 = "channel_utilization.csv"
        f2 = "channel_utilization_new.csv"
        cmd = "cp %s/%s %s/%s" % (report_dir,f1,report_dir,f2)
        os.system(cmd)
        nf = "%s/channel_utilization_new.csv" % (report_dir)
        '''if os.stat("%s"  % nf).st_size == 0 :
            return
        for line in fileinput.input(['%s' % nf], inplace=True):
    
            if fileinput.isfirstline():
                print','.join(headers)
                print line.rstrip()
            else:
                print line.rstrip() '''
    
        #reading the new summary.csv file
        #df = pd.read_csv("%s/summary.csv" % report_dir)
        df = pd.read_csv("%s" % nf)
        #print df.values
        # the following gives the data, summary.csv is with two colums , type and value
        today_data = df['avg_channel_util']
        #print today_data.values
        ## the following reads the existing weeksummary.csv file
        df_org = pd.read_csv("%s/weekly_air_utilization.csv" % report_dir)
        #print df_org.values
        
        clist = list(df_org.columns)
        print clist
        ## deleting the last column ,  df.drop(column_name,axis)
        tt = df_org.drop(clist[-1],1)
        ## inserting( or adding) the new column as column 1   df.insert(column_no, column_heading, values as a Series)
        tt.insert(1,'%s' % new_date ,today_data)
        
        ## removing the name of the dropped column name from the list
        clist = list(tt.columns)
        ## index =False to aviod the row index in the csv file
        #df_org.to_csv('%s/weekly_air_utilization.csv' % report_dir, header=True,cols=clist,index=False)
        tt.to_csv('%s/weekly_air_utilization.csv' % report_dir, header=True,cols=clist,index=False)
    

def dailyChannelUtility(filelist,newdate):
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']  
    import  time 
    import datetime    
    print  newdate
    dateList = newdate.split()
    (m,d) = dateList[0], dateList[1]
    if m in months:
        m_index = months.index(m)
        slist = [00,00,00]
        tlist = [int(year), m_index+1, int(d)]
        tlist.extend(slist)
        tlist.extend([1,1,1])
        time_insec = int(time.mktime(tuple(tlist)))+3600    
    channel2_Total_mean = 0
    channel5_Total_mean = 0
    headers = '2g_ch_util_Total,5g_ch_util_Total,2g_channel,5g_channel'.split(',')
    #headers = 'ap,ip,ap_name,uptime,g_client_count,a_client_count,cpuUse,per_memoryUsage,2g_ch_switch_count,5g_ch_switch_count,heartbeatlost_count,heartbeatlost_time,reboot_count,upgrade_reboot_count,reboot_reason,target_assert_count,target_assert_times,tx_desc_stuck_count,tx_desc_stuck_times,wmi_stuck_count,wmi_lasttime_reported,target_inactive_count,target_inactive_times,beacon_stuck,2g_ch_util_Busy,2g_ch_util_RX,2g_ch_util_TX,2g_ch_util_Total,5g_ch_util_Busy,5g_ch_util_RX,5g_ch_util_TX,5g_ch_util_Total,2g_channel,5g_channel'.split()
    g_channel_list = [2412,2417,2422,2427,2432,2437,2442,2447,2452,2457,2462]
    a_channel_list = [5180,5200,5220,5240,5260,5280,5300,5320,5500,5520,5540,5560,5580,5600,5620,5640,5660,5680,5700,5745,5765,5785,5805,5825]
    channel_tuple = [(2412,1),(2417,2),(2422,3),(2427,4),(2432,5),(2437,6),(2442,7),(2447,8),(2452,9),(2457,10),(2462,11),(5180,36),(5200,40),(5220,44),(5240,48),(5260,52),(5280,56),(5300,60),(5320,64),(5500,100),(5520,104),(5540,108),(5560,112),(5580,116),(5600,120),(5620,124),(5640,128),(5660,132),(5680,136),(5700,140),(5745,149),(5765,153),(5785,157),(5805,161),(5825,165)]
    chanDict = {}    
    for item in channel_tuple:
        key,v = item[0], item[1]
        chanDict[key] = v
    uDict = {}    
    for f in filelist: 
        ftime = int(f.split('_')[2].split('.')[0])
        if ftime < (time_insec + 8*60*60):
            continue
        if ftime > (time_insec + 19*60*60):
            break
        f1 = 'daily_east_out.csv'
        f2 = 'daily_west_out.csv'
        for ch in g_channel_list:
            # separating the list for east and west wing                            
            df = pd.read_csv('%s/%s' % (apstats_dir,f))
            #df.loc[df['column_name'] == some_value]
            df_new = df.loc[(df['2g_channel'] == ch)]
            #df_new = df[df['ip'].isin(east_ap_list)]
            #print df_new.values
            if df_new.empty:
                continue
            else:
                df_new.to_csv('%s' % f1, cols=headers,index=None)     

                df = pd.read_csv('%s' % (f1))
                
                Total_mean = df['2g_ch_util_Total'].mean().round()
                
                os.system('rm %s' % f1)
                if ch not in uDict.keys():
                    uDict[ch] = []
                    
                uDict[ch].append(Total_mean)
        for ch in a_channel_list:
                                           
            df = pd.read_csv('%s/%s' % (apstats_dir,f))
            #df.loc[df['column_name'] == some_value]
            df_new = df.loc[(df['5g_channel'] == ch)]
            #df_new = df[df['ip'].isin(east_ap_list)]
            #print df_new.values
            if df_new.empty:
                continue    
            else:
                df_new.to_csv('%s' % f1, cols=headers,index=None)     
            
                df = pd.read_csv('%s' % (f1))
            
                Total_mean = df['5g_ch_util_Total'].mean().round()
            
                os.system('rm %s' % f1)
                if ch not in uDict.keys():
                    uDict[ch] = []
                uDict[ch].append(Total_mean)
    chDict = {}
    for key in uDict.keys():
        utility_avg = sum(uDict[key])/len(uDict[key])
        chDict[key] = {}
        chDict[key]['channel'] = chanDict[key]
        chDict[key]['avg_channel_util'] = int(utility_avg)

    channel_utility_writer(chDict,newdate)

def dailyAirUtility(filelist,newdate):
    
    
    east_g_Total_mean = 0
    east_a_Total_mean = 0
    
    west_g_Total_mean = 0
    west_a_Total_mean = 0    
    #headers = 'ap,ip,ap_name,uptime,g_client_count,a_client_count,cpuUse,per_memoryUsage,2g_ch_switch_count,5g_ch_switch_count,heartbeatlost_count,heartbeatlost_time,reboot_count,upgrade_reboot_count,reboot_reason,target_assert_count,target_assert_times,tx_desc_stuck_count,tx_desc_stuck_times,wmi_stuck_count,wmi_lasttime_reported,target_inactive_count,target_inactive_times,beacon_stuck,2g_ch_util_Busy,2g_ch_util_RX,2g_ch_util_TX,2g_ch_util_Total,5g_ch_util_Busy,5g_ch_util_RX,5g_ch_util_TX,5g_ch_util_Total'.split()
    
    headers = 'ap,ip,ap_name,uptime,g_client_count,a_client_count,cpuUse,per_memoryUsage,2g_ch_switch_count,5g_ch_switch_count,heartbeatlost_count,heartbeatlost_time,reboot_count,upgrade_reboot_count,reboot_reason,target_assert_count,target_assert_times,tx_desc_stuck_count,tx_desc_stuck_times,wmi_stuck_count,wmi_lasttime_reported,target_inactive_count,target_inactive_times,beacon_stuck,2g_ch_util_Busy,2g_ch_util_RX,2g_ch_util_TX,2g_ch_util_Total,5g_ch_util_Busy,5g_ch_util_RX,5g_ch_util_TX,5g_ch_util_Total'.split(',')
    east_ap_list = ['172.16.22.55','172.16.22.158','172.16.21.120','172.16.21.93','172.16.22.52','172.16.21.168','172.16.22.156','172.16.22.122','172.16.22.157','172.16.21.128','172.16.21.122','172.16.22.8','172.16.22.60','172.16.22.153','172.16.21.235','172.16.21.131','172.16.20.86']
    west_ap_list = ['172.16.22.54','172.16.22.95','172.16.21.254','172.16.20.97','172.16.22.132','172.16.21.189','172.16.21.35','172.16.21.124','172.16.22.34','172.16.22.22','172.16.21.221','172.16.21.126','172.16.21.247']
    for f in filelist:    
        f1 = 'daily_east_out.csv'
        f2 = 'daily_west_out.csv'
        # separating the list for east and west wing                            
        df = pd.read_csv('%s/%s' % (apstats_dir,f))
        df_new = df[df['ip'].isin(east_ap_list)]
        #print df_new.values
        df_new.to_csv('%s' % f1, cols=headers,index=None)
        
        df = pd.read_csv('%s/%s' % (apstats_dir,f))
        df_new = df[df['ip'].isin(west_ap_list)]
        df_new.to_csv('%s' % f2, cols=headers,index=None)        
       
        if f1:
            df = pd.read_csv('%s' % (f1))  
            east_g_Total_mean += df['2g_ch_util_Total'].mean().round()
            east_a_Total_mean += df['5g_ch_util_Total'].mean().round()
            os.system('rm %s' % f1)
    
        if f2:
            df = pd.read_csv('%s' % (f2))
            west_g_Total_mean += df['2g_ch_util_Total'].mean().round()
            west_a_Total_mean += df['5g_ch_util_Total'].mean().round()
            os.system('rm %s' % f2)
    all_west_g_Total_mean = west_g_Total_mean // len(filelist)
    all_west_a_Total_mean = west_a_Total_mean // len(filelist)
    all_east_g_Total_mean = east_g_Total_mean // len(filelist)
    all_east_a_Total_mean = east_a_Total_mean // len(filelist)
    #cmd = 'date -d "today" \'+%b %d %H:%M\''
    #mydate = os.popen(cmd).read().rstrip()
    mydate = newdate
    dailyairList = [mydate,all_east_g_Total_mean,all_east_a_Total_mean,all_west_g_Total_mean,all_west_a_Total_mean]
    #eastg5airList = [mydate,all_east_a_Total_mean]
    #westg2airList = [mydate,all_west_g_Total_mean]
    #westg5airList = [mydate,all_west_a_Total_mean]    
    
    newairutility_writer(dailyairList)
    #airutility_writer(eastg5airList,"5g","east")    
    #airutility_writer(westg2airList,"2g","west")
    #airutility_writer(westg5airList,"5g","west") 
    
    

def apStatsSort(newdate,summaryDict):
    ap_ip_list,newDict = ap_detail()

    headers = 'ap,ip,ap_name,uptime,g_client_count,a_client_count,cpuUse,per_memoryUsage,2g_ch_switch_count,5g_ch_switch_count,heartbeatlost_count,heartbeatlost_time,reboot_count,upgrade_reboot_count,reboot_reason,target_assert_count,target_assert_times,tx_desc_stuck_count,tx_desc_stuck_times,wmi_stuck_count,wmi_lasttime_reported,target_inactive_count,target_inactive_times,beacon_stuck,2g_ch_util_Busy,2g_ch_util_RX,2g_ch_util_TX,2g_ch_util_Total,5g_ch_util_Busy,5g_ch_util_RX,5g_ch_util_TX,5g_ch_util_Total,2g_channel,5g_channel'.split()

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
    #**************************************************** need to remove
    #filelist = ['ap_stats_1449241796.csv','ap_stats_1449244033.csv','ap_stats_1449246270.csv','ap_stats_1449248509.csv','ap_stats_1449250753.csv','ap_stats_1449252998.csv','ap_stats_1449255242.csv','ap_stats_1449257505.csv','ap_stats_1449259761.csv','ap_stats_1449259761.csv','ap_stats_1449262009.csv']
    
    #print len(filelist)
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
    dailyAirUtility(filelist,newdate)
    dailyChannelUtility(filelist, newdate)

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
        #print x.values
    
        ### The following gets the required columns to y
        #y = x[['2g_client_count']] 
        gclient_count_item = []
        aclient_count_item = []
        
        y =  x[['g_client_count','a_client_count','2g_ch_switch_count','5g_ch_switch_count','reboot_count','upgrade_reboot_count','heartbeatlost_count','cpuUse','per_memoryUsage']]
        yy = y.fillna(0) 
        #print yy.values
        for d in ['g_client_count','a_client_count','2g_ch_switch_count','5g_ch_switch_count','reboot_count','upgrade_reboot_count','heartbeatlost_count','cpuUse','per_memoryUsage']:
            d_count = 0
            df3 = yy['%s' % d] 
            dDict[ap]['%s' % d] = df3.max()
            d_count = 0

        df_gg = x[['2g_ch_util_Busy','2g_ch_util_RX','2g_ch_util_TX','2g_ch_util_Total']]
        df_aa = x[['5g_ch_util_Busy','5g_ch_util_RX','5g_ch_util_TX','5g_ch_util_Total']]
        #print df_gg.values
        
        #df_gg.convert_objects(convert_numeric=True)
        #df_gg.replace('%','',regex=True).astype('float')
        df_g = df_gg.astype(float).fillna(0.0)
        df_a = df_aa.astype(float).fillna(0.0)
        df_g =df_gg.fillna(0)
        #print asd.values
        df_a =df_aa.fillna(0)

        util_max_list_g = df_g.ix[df_g['2g_ch_util_Total'].idxmax()]
        util_max_list_a = df_a.ix[df_a['5g_ch_util_Total'].idxmax()]
        #print util_max_list_g.values
        dDict[ap]['2g_ch_util_Total'] = util_max_list_g['2g_ch_util_Total']
        #print util_max_list_g['2g_ch_util_Total']
        dDict[ap]['2g_ch_util_Busy'] = util_max_list_g['2g_ch_util_Busy']
        dDict[ap]['2g_ch_util_RX'] = util_max_list_g['2g_ch_util_RX']
        dDict[ap]['2g_ch_util_TX'] = util_max_list_g['2g_ch_util_TX']   
        
        dDict[ap]['5g_ch_util_Total'] = util_max_list_a['5g_ch_util_Total']
        dDict[ap]['5g_ch_util_Busy'] = util_max_list_a['5g_ch_util_Busy']
        dDict[ap]['5g_ch_util_RX'] = util_max_list_a['5g_ch_util_RX']
        dDict[ap]['5g_ch_util_TX'] = util_max_list_a['5g_ch_util_TX']
        
    #The following is for the daily airtime report    
    
    #g2airList = [newdate,g_TX_sum,g_RX_sum,g_Busy_sum,g_Total_sum]
    #g5airList = [newdate,a_TX_sum,a_RX_sum,a_Busy_sum,a_Total_sum]
        
    #airutility_writer(g2airList,"2g")
    #airutility_writer(g5airList,"5g")   
    
    gclientDict = {} 

    gclientDict["data"] = [] 
    rebootDict = {}
    rebootDict["data"] = []
    upgradeDict = {}
    upgradeDict["data"] = []
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
        #print dDict[ap]['g_client_count']
        gclientDict["data"].append((name,dDict[ap]['g_client_count']))
        aclientDict["data"].append((name,dDict[ap]['a_client_count']))
        gchannelswitchDict["data"].append((name,dDict[ap]['2g_ch_switch_count']))
        achannelswitchDict["data"].append((name,dDict[ap]['5g_ch_switch_count']))
        beatDict["data"].append((name,dDict[ap]['heartbeatlost_count']))
        rebootDict["data"].append((name,dDict[ap]['reboot_count']))
        upgradeDict["data"].append((name,dDict[ap]['upgrade_reboot_count']))
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
    upgrade_items = sorted(upgradeDict["data"], key=get_client, reverse=True)
    cpu_items = sorted(cpuDict["data"], key=get_client, reverse=True)
    mem_items = sorted(memDict["data"], key=get_client, reverse=True)
    #print gchannelutilDict["data"]
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
        gch_util_final[item[0]] = item[1:]
    for item in ach_util_items[:10]:
        ach_util_final[item[0]] = item[1:] 
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
    upgradesum = sum(upgrade_items[i][1] for i in range(len(upgrade_items)))
    other_rebootsum = abs(upgradesum - rebootsum)

    gchannelswitchsum = sum(gch_switch_items[i][1] for i in range(len(gch_switch_items)))
    achannelswitchsum = sum(ach_switch_items[i][1] for i in range(len(ach_switch_items)))
    summaryDict['Peak Users (2.4Ghz)'] = int(peak_g_users)
    summaryDict['Peak Users (5GHz)'] = int(peak_a_users)
    summaryDict['Total Number of ap Reboots ( excluding Upgrade)'] = int(other_rebootsum)
    summaryDict['Total Number of ap Reboots ( Upgrade)'] = int(upgradesum)
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
        df =  x[['ts','action','station','hint','reason','freq','rx_rssi','total_bytes']]
        #print y.values
        #df = y.sort(['station','ts','action','hint','reason','freq','rx_rssi','total_bytes'])
        #print df.values
        for i in range(0,len(df)):
            ts = df['ts'][i]
            mac = df['station'][i]
            action = df['action'][i]
            reason = df['reason'][i]
            freq = df['freq'][i]
            rssi = df['rx_rssi'][i]
            total_bytes = df['total_bytes'][i]
            if action == 'disassoc':
                hint = df['hint'][i].split()[0]
            else:
                hint = ''
            if mac not in dDict.keys():
                dDict[mac] = {}
            if ts not in dDict[mac].keys():
                dDict[mac][ts] = {}
    
            dDict[mac][ts]['action'] = action 
            dDict[mac][ts]['reason'] = reason
            dDict[mac][ts]['freq'] = freq
            dDict[mac][ts]['hint'] = hint    
            dDict[mac][ts]['rssi'] = rssi  
            dDict[mac][ts]['total_bytes'] = total_bytes
                    
    client_list = dDict.keys()
    #print len(client_list)
    countDict = {}
    reasonDict = {}
    for mac in dDict.keys():
        countDict[mac] = {}
             
        countDict[mac]['disassoc_count'] = 0
        countDict[mac]['roaming_count'] = 0
        countDict[mac]['authdifficulty_count'] = 0
        countDict[mac]['gband_count'] = 0
        countDict[mac]['acband_count'] = 0
        countDict[mac]['total_bytes'] = 0
        
        #### here the reasonDict starts
        for ts in dDict[mac].keys():
            if dDict[mac][ts]['action'] == 'disassoc':
                hint = dDict[mac][ts]['hint']
                if hint =='AP':
                    continue                
                countDict[mac]['disassoc_count'] += 1 
                if mac not in reasonDict.keys():
                    reasonDict[mac] = {}
                if hint not in reasonDict[mac].keys():
                    reasonDict[mac][hint] = {}
                    reasonDict[mac][hint]['disassoc_count'] = 0 
                reasonDict[mac][hint]['disassoc_count'] += 1
                    
            elif dDict[mac][ts]['action'] == 'roaming':
                countDict[mac]['roaming_count'] += 1
            elif dDict[mac][ts]['action'] == 'Authentication Difficulty':
                countDict[mac]['authdifficulty_count'] += 1
            elif dDict[mac][ts]['action'] == 'leaving':
                countDict[mac]['total_bytes'] += dDict[mac][ts]['total_bytes']           
     
    disassocDict = {}
    disassocDict["data"] = []
    senddisassocDict = {}
    senddisassocDict["data"] = []
    recdisassocDict = {}
    recdisassocDict["data"] = [] 
    stadisassocDict = {}
    stadisassocDict["data"] = []     
    
    roamingDict = {}
    roamingDict["data"] = []
    authdifficultyDict = {}
    authdifficultyDict["data"] = []
    usageDict = {}
    usageDict["data"] = []     
    for mac in countDict.keys():
        roamingDict["data"].append((mac,countDict[mac]['roaming_count']))
        authdifficultyDict["data"].append((mac,countDict[mac]['authdifficulty_count']))
        disassocDict["data"].append((mac,countDict[mac]['disassoc_count']))
        usageDict["data"].append((mac,countDict[mac]['total_bytes']))
        
    for mac in reasonDict.keys():
        for hint in reasonDict[mac].keys():
            if hint =='send':
                senddisassocDict["data"].append((mac,reasonDict[mac][hint]['disassoc_count'])) 
            elif hint == 'received':
                recdisassocDict["data"].append((mac,reasonDict[mac][hint]['disassoc_count']))                 
            elif hint == 'STA':
                stadisassocDict["data"].append((mac,reasonDict[mac][hint]['disassoc_count']))                        
                
    senddisassoclist = sorted(senddisassocDict["data"], key=get_client, reverse=True)
    recdisassoclist = sorted(recdisassocDict["data"], key=get_client, reverse=True)
    stadisassoclist = sorted(stadisassocDict["data"], key=get_client, reverse=True)
    roaminglist = sorted(roamingDict["data"], key=get_client, reverse=True) 
    authdifficultylist = sorted(authdifficultyDict["data"], key=get_client, reverse=True) 
    disassoclist = sorted(disassocDict["data"], key=get_client, reverse=True)  
    usagelist = sorted(usageDict["data"], key=get_client, reverse=True)  

    nlist = []
    mlist = []
    rlist,alist, dlist,tlist = [],[],[],[]
    for r in roaminglist[:3]:
        rlist.append(r[0])
        nlist.append(r[1])
    for i in range(len(rlist)):
        mlist.append(rlist[i]+'('+str(nlist[i])+')')
        
    rslist= "   ".join(mlist)
    #nrlist = str(rlist)
    nlist = []
    mlist = []  
    alist = []
    for a in authdifficultylist[:3]:
        alist.append(a[0])
        nlist.append(a[1])
        
    for i in range(len(alist)):
        mlist.append(alist[i]+'('+str(nlist[i])+')')    
    aslist= "   ".join(mlist) 
    
    nlist = []
    mlist = []       
    dlist = []
    for d in disassoclist[:3]:
        dlist.append(d[0])
        nlist.append(d[1])
    for i in range(len(dlist)):
        mlist.append(dlist[i]+'('+str(nlist[i])+')')     
    dslist= "   ".join(mlist)
    #print "dlist", dslist
    nlist = []
    mlist = []       
    dlist = []
    for d in usagelist[:3]:
        dlist.append(d[0])
        nlist.append(d[1])

    for i in range(len(dlist)):
        mlist.append(dlist[i]+'('+str(nlist[i])+')')     
        tslist= "   ".join(mlist)    
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
    senddisassocsum = sum(senddisassoclist[i][1] for i in range(len(senddisassoclist)))
    recdisassocsum = sum(recdisassoclist[i][1] for i in range(len(recdisassoclist)))
    stadisassocsum = sum(stadisassoclist[i][1] for i in range(len(stadisassoclist)))
    #print authdifficultysum, roamingsum, disassocsum,senddisassocsum,recdisassocsum    
    summaryDict['Total Number of Client Disassoc sent'] = int(senddisassocsum)
    summaryDict['Total Number of Client Disassoc received'] = int(recdisassocsum)  
    summaryDict['Total Number of Client Disassoc kicked out'] = int(stadisassocsum)  
    summaryDict['Total Number of Authetication Difficulty'] = int(authdifficultysum)
    summaryDict['Total Number of Client Roaming'] = int(roamingsum)
    summaryDict['Total Number of Client Disassoc'] = int(disassocsum)

    summaryDict['Top3 clients with maximum number of Disassoc '] = dslist
    summaryDict['Top3 clients with maximum number of Authentication Difficulty '] = aslist
    summaryDict['Top3 clients with maximum number of roaming '] = rslist  
    os.system('rm -f %s/ap_file*' % apstats_dir)
    os.system('rm -f %s/client_file*' % clientstats_dir)  
    #rssiDictWriter(reasonDict,new_date)
    rstr = new_date+ '   '+rslist
    ustr = new_date+ '   '+tslist
    fp = open('%s/freq_roamers.txt' % working_dir, 'a')
    fp.write(rstr)
    fp.write('\n')
    fp.close()
    
    fp = open('%s/most_usage.txt' % working_dir, 'a')
    fp.write(ustr)
    fp.write('\n')
    fp.close()    
    
    return summaryDict



if __name__ =='__main__':      

    summaryDict = {}
    new_date = get_date()
    print new_date
    year = get_year()
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

    zd = zdcli.ZDCLI(zd_ip)
    zd.connect(zduser, zdpass, timeout=3600,sesame_key="!v54!")
    #zd.to_shell()
    version = zd.get_zd_version()
    zd.close() 
    print version
    if version:
        summaryDict['ZD image'] = version.rstrip() 
    else:
        summaryDict['ZD image'] = '9.12.2.0 build 84'    
    summaryDict = apStatsSort(new_date,summaryDict)
    summaryDict = clientSort(new_date,summaryDict)
    #summaryDict = walSort(new_date,summaryDict)

    daily_summary_writer(summaryDict)
    weekly_summary_writer(new_date) 
    weekly_airUtilization_writer(new_date)
    cmd = 'date -d "yesterday 13:00" \'+%b %d\''
    #cmd = 'date -d "today" \'+%m/%d/%Y:%H\''
    mydate = os.popen(cmd).read() 
    #print mydate
    d = mydate.split(':')[0]
    #h = mydate.split(':')[1] 
    #print working_dir
    message_fp = open('%s/dailymessage' % working_dir,'w')
    
    message_fp.write('DENSITY network daily report for %s  is available in the following URL:\n\n' % (d))
    #message_fp.write('http://10.150.7.177/densitystatus/dailystatus/test.html')                     
    message_fp.write('http://%s/%s/test.html' % (http_server,html_dir))
    message_fp.write('\n\nDENSITY network Air utilization report s available in the following URL:\n\n' )
    message_fp.write('http://%s/%s/dailytest.html' % (http_server,html_dir))
    message_fp.write('\n\nSummary file is attached' )
    message_fp.close()
    fname = '/var/www/densitystatus/dailystatus/summary.csv'
    subprocess.call(['%s/daily_density_email.sh' % working_dir,  "%s" % fname]) 
    
    
