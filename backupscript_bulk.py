import time, os, re
import pysftp
import subprocess
for da in range(14,25):

    #cmd = 'date -d "yesterday 13:00" \'+%b %d\''
    #cmd = 'date -d "3 days ago"  \'+%b %d\'' 
    cmd = r'date -d "%s days ago" ' % da
    #cmd = 'date -d "today" \'+%m/%d/%Y:%H\''

    mydate = os.popen(cmd).read()
    print mydate
    d = mydate.split(' ')[1:4]
    print d
    if d[1] == '':
        nd = d[0]+'  '+d[2]
        newdate = d[0]+'_0'+d[2]
    else:
        nd = d[0]+' '+d[1]
        newdate = d[0]+'_'+d[1]
    print nd
    fname= 'filelist'
    newname= 'newfile'
    os.system('rm -r /home/wspbackup/newdir/latestscript/yesterdaystats')
    os.mkdir('/home/wspbackup/newdir/latestscript/yesterdaystats')
    for item in ['apstats','clientstats']: 
        fname= 'filelist'
        newname= 'newfile'        
        tarfilename = '%sfiles.tar.gz' % item
        os.chdir('/var/www/densitystatus/%s' % item)
        print os.getcwd()
        cmd = 'ls -ltr|grep \"%s\" > %s' % (nd,fname)
        print cmd
        os.system(cmd)
        if os.stat(fname).st_size > 0:
            cmd = 'cat %s | awk "{ print \$9}" >> %s' %(fname, newname) 
            os.system(cmd)
            cmd = 'tar -czvf %s `cat %s`' % (tarfilename,newname) 
            print cmd
            print os.getcwd()
            os.system(cmd)
            cmd = 'mv /var/www/densitystatus/%s/%s /home/wspbackup/newdir/latestscript/yesterdaystats/%s' %(item,tarfilename,tarfilename)
            os.system(cmd)
            os.system('rm -f %s' % fname)
            os.system('rm -f %s' % newname)  
   
    for ap in [('ap102','2c_c5_d3_01_82_3c'),('ap141','2c_c5_d3_01_82_4c'),('ap142','2c_c5_d3_01_83_5c')]:
        fname= 'filelist'
        newname= 'newfile'        
        tarfilename = 'ap_%s_capture.tar.gz' % ap[1]
        os.chdir('/var/www/densitystatus/snifferfiles/%s' % ap[0])
        print os.getcwd()
        cmd = 'ls -ltr|grep \"%s\" > %s' % (nd,fname)
        print cmd
        os.system(cmd)
        if os.stat(fname).st_size > 0:
            cmd = 'cat %s | awk "{ print \$9}" >> %s' %(fname, newname) 
            os.system(cmd)
            cmd = 'tar -czvf %s `cat %s`' % (tarfilename,newname) 
            print cmd
            print os.getcwd()
            os.system(cmd)
            cmd = 'mv /var/www/densitystatus/snifferfiles/%s/%s /home/wspbackup/newdir/latestscript/yesterdaystats/%s' %(ap[0],tarfilename,tarfilename)
            os.system(cmd)
            os.system('rm -f %s' % fname)
            os.system('rm -f %s' % newname)
    

    '''os.chdir('/var/www/densitystatus/clientstats')
    ## getting all stats directory
    #cmd = 'find \. -not -path `\.`  -mtime -1  > %s' % (fname)
    cmd = 'ls -ltr|grep \"%s\" > %s' % (nd,fname)
    print cmd
    os.system(cmd)
    if os.path.isfile(fname):
        cmd = 'cat %s | awk "{ print \$9}" >> %s' %(fname, newname)
        os.system(cmd)
        cmd = 'tar -czvf allstats.tar.gz `cat %s`' % newname
        print cmd
        print os.getcwd()
        os.system(cmd)
        cmd = 'mv /var/www/densitystatus/clientstats/allstats.tar.gz /home/wspbackup/newdir/latestscript/yesterdaystats/allstats.tar.gz'
        os.system(cmd)
        os.system('rm -f %s' % fname)
        os.system('rm -f %s' % newname) 
   
    os.chdir('/var/www/densitystatus/snifferfiles/ap142')
    ## getting all stats directory
    #cmd = 'find \. -not -path `\.`  -mtime -1  > %s' % (fname)
    cmd = 'ls -ltr|grep \"%s\" > %s' % (nd,fname)
    print cmd
    os.system(cmd)
    if os.stat(fname).st_size > 0:
        cmd = 'cat %s | awk "{ print \$9}" >> %s' %(fname, newname)
        os.system(cmd)
        cmd = 'tar -czvf ap_2c_c5_d3_01_83_5c_capture.tar.gz `cat %s`' % newname
        os.system(cmd)
        cmd = 'mv /var/www/densitystatus/snifferfiles/ap142/ap_2c_c5_d3_01_83_5c_capture.tar.gz /home/wspbackup/newdir/latestscript/yesterdaystats/ap_2c_c5_d3_01_83_5c_capture.tar.gz'
        os.system(cmd)        
        os.system('rm -f %s' % fname)
        os.system('rm -f %s' % newname) '''
 
    print newdate
    ## sftp connection
    srv = pysftp.Connection(host="10.150.7.222",username="rms")
    srv.chdir("/home")
    srv.mkdir("densitystats_%s" % newdate)
    #srv.chdir("densitystats_%s" % newdate)
    srv.pwd
    srv.put_r("/home/wspbackup/newdir/latestscript/yesterdaystats/","/home/densitystats_%s/" % newdate , preserve_mtime=True)
    srv.close()
    os.system('rm -r /home/wspbackup/newdir/latestscript/yesterdaystats')
    
    os.chdir('/home/wspbackup/newdir/latestscript')  
