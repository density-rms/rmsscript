import time, os, re
import pysftp
import subprocess
for da in range(1,41,41,41,4):

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
    os.mkdir('/home/wspbackup/newdir/latestscript/yesterdaystats')
    os.chdir('/var/www/densitystatus/apstats')
    print os.getcwd()
    cmd = 'ls -ltr|grep \"%s\" > %s' % (nd,fname)
    print cmd
    os.system(cmd)
    if os.path.isfile(fname):
        cmd = 'cat %s | awk "{ print \$9}" >> %s' %(fname, newname) 
        os.system(cmd)
        cmd = 'tar -czvf apcsvfiles.tar.gz `cat %s`' % newname 
        print cmd
        print os.getcwd()
        os.system(cmd)
        cmd = 'mv /var/www/densitystatus/apstats/apcsvfiles.tar.gz /home/wspbackup/newdir/latestscript/yesterdaystats/apcsvfiles.tar.gz'
        os.system(cmd)
        os.system('rm -f %s' % fname)
        os.system('rm -f %s' % newname)
    
    os.chdir('/var/www/densitystatus/clientstats')
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
    
    #x = nd.split(' ')
    #newdate = x[0]+'_'+x[1]
    print newdate
    ## sftp connection
    srv = pysftp.Connection(host="10.150.7.222",username="rms")
    srv.chdir("/home")
    srv.mkdir("densitystats_%s" % newdate)
    srv.pwd
    srv.put_r("/home/wspbackup/newdir/latestscript/yesterdaystats/","/home/densitystats_%s/" % newdate , preserve_mtime=True)
    srv.close()
    os.system('rm -r /home/wspbackup/newdir/latestscript/yesterdaystats')
    
    os.chdir('/home/wspbackup/newdir/latestscript')  
