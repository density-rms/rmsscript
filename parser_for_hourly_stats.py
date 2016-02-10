
#!/usr/bin/python


import  time
import datetime
import calendar
import pandas as pd
import fileinput
import os,csv

currentdir = "/home/rms/density_rms"
reportdir = "/var/www/densitystatus/dailystatus"

def newairutility_writer(utilitylist):

    csvname = "%s/hourly_air_utilization.csv" % currentdir

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
    newname = "%s/hourly_air_utilization.csv" % reportdir
    os.system('cp %s %s' %(csvname, newname))
    return

def apStatsSum():
   
    headers = '2g_ch_util_Busy,2g_ch_util_RX,2g_ch_util_TX,2g_ch_util_Total,5g_ch_util_Busy,5g_ch_util_RX,5g_ch_util_TX,5g_ch_util_Total'.split(',')

    lastfile = '%s/hourly_stats.csv' % currentdir
    east_ap_list = ['172.16.22.55','172.16.22.158','172.16.21.120','172.16.21.93','172.16.22.52','172.16.21.168','172.16.22.156','172.16.22.122','172.16.22.157','172.16.21.128','172.16.21.122','172.16.22.8','172.16.22.60','172.16.22.153','172.16.21.235','172.16.21.131','172.16.20.86']
    west_ap_list = ['172.16.22.54','172.16.22.95','172.16.21.254','172.16.20.97','172.16.22.132','172.16.21.189','172.16.21.35','172.16.21.124','172.16.22.34','172.16.22.22','172.16.21.221','172.16.21.126','172.16.21.247']
    if lastfile:
        f1 = '%s/east_out.csv' % currentdir
        f2 = '%s/west_out.csv' % currentdir
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

    #cmd = 'date -d "today" \'+%b %d %H:%M\''
    cmd = '/bin/date -d "today" \'+%H:00\''
    mydate = os.popen(cmd).read().rstrip()
    utilization_list = [mydate,east_g_Total_mean,east_a_Total_mean,west_g_Total_mean,west_a_Total_mean]
    newairutility_writer(utilization_list)
if  __name__ =='__main__':
    apStatsSum()

