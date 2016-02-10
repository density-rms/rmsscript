import pexpect
import sys
import re
import time
import cStringIO

class ZDCLI:
    IS_8x = 1
    IS_9x = 2
    ZD_PROMPT = ["ruckus>", 'ruckus%', 'ruckus#','#', 'ruckus\$']
    def __init__(self,zd_ip, verbose=False):
        self.ip = zd_ip
        self.prompt = self.ZD_PROMPT
        self.VERBOSE = verbose

    def setvars(self, s, user, passwd, i, timeout=60):
        self.user = user
        self.passwd = passwd
        self.s = s
        self.set_zdtype(i)
        self.s.maxread = 5000
        self.s.timeout = timeout
        
    def connect(self, user, passwd, timeout=60, sesame_key=None):
        self.sesame_key = sesame_key
        ssh_newkey = 'Are you sure you want to continue connecting'    
        #print "Connecting to %s" % self.ip
        s = pexpect.spawn( 'ssh %s' % self.ip, searchwindowsize = 8 )
        i = s.expect([pexpect.TIMEOUT, ssh_newkey, '.*login:'])
        if i == 1:
            s.sendline( 'yes' )
            s.expect('.*login:')
        s.sendline(user)  # run a command
        s.expect('.*assword\S*:')       
        s.sendline(passwd)  # run a command
        i=s.expect(self.prompt)  # match the prompt
        self.setvars(s, user, passwd, i, timeout)
        
    def set_zdtype(self, prompt_res):
        i = prompt_res
        if i == 0:
            self.zdtype = self.IS_9x
        elif i == 1:
            self.zdtype = self.IS_8x
        else:
            raise Exception("Unrecognized prompt")
        
    def get_sys_info(self):
        if self.zdtype == self.IS_9x:
            self.s.sendline('enable')
            self.s.expect(self.prompt)
            data = self.cmd('show sysinfo')
            self.s.sendline('disable')
            self.s.expect(self.prompt)
        elif self.zdtype == self.IS_8x:
            data = self.cmd('show sys')
        return data


    def to_shell(self):
        self.s.sendline('') # send newline to see what the shell looks like
        i = self.s.expect(self.prompt)
        if self.zdtype == self.IS_9x:
            if i == 3: # already in shell, return
                return
            if i == 0:
                self.s.sendline('enable')
                self.s.expect(self.prompt[2])

            key = self.sesame_key
            #    key = self.tikona_keyfetch()
            self.s.sendline(key)
            self.s.expect(self.prompt[3])
        else: # ver 8x
            if i == 2: # already in shell, return
                return
            self.s.sendline("!v54!")
            self.s.expect(self.prompt[2])

    def cmd(self, cmd, prompt=None, timeout=None, comment=None):
        if self.VERBOSE:
            output = cmd
            if comment != None:
                output = comment
            if len(output):
                print "ZD %s# %s" % (self.ip, output)
        self.s.sendline(cmd)
        if not prompt:
            prompt = self.prompt
        self.s.expect(prompt, timeout = timeout)
        rx = self.s.before
        print rx
        if rx:
            rx = rx.replace(cmd, '')
            rx = rx.strip()
            
        return cStringIO.StringIO(rx).readlines()
            
    def get_shell_sys_info(self, shell_key = '!v54!'):
        return self.shell_cmd('show system', shell_key)
    def get_zd_version(self):
        self.s.sendline('enable')
        self.s.expect(self.prompt)
        self.s.sendline('show sysinfo')
        self.s.expect(self.prompt)   
        rx = self.s.before
        print rx
        if rx:
            pattern = 'Version.*?(\d.*?)\n'
            res = re.search(pattern,rx)
            if res:
                version = res.group(1)
                return version
            else:
                print "Could not get ZD version"
                return
    def get_zdapmac(self,addr):
        #res = self.cmd("wlaninfo -A | grep ^AP")
        #return [(aline.strip().split()[1].split(',')[0],aline.strip().split()[5]) for aline in res]
        #return res
        self.s.sendline('enable force')
        self.s.expect(self.prompt)
        self.s.sendline('debug')
        self.s.expect(self.prompt)
        self.s.sendline('script')
        self.s.expect(self.prompt)
        cmd = 'exec zdmaclist.sh %s' % addr
        #self.s.sendline('exec zdmaclist.sh addr')
        self.s.sendline(cmd)
        self.s.expect(self.prompt)
        #self.s.expect('quit')
        #self.s.expect(self.prompt)
        #self.s.expect('quit')
        #self.s.expect(self.prompt)  
        #self.s.expect('quit')      
        return ('ok')    

    def set_snifferchan(self):
        self.s.sendline('enable')
        self.s.expect(self.prompt)
        self.s.sendline('debug')
        self.s.expect(self.prompt)
        self.s.sendline('script')
        self.s.expect(self.prompt)
        cmd = 'exec channelset.sh'
        self.s.sendline(cmd)
        self.s.expect(self.prompt)
        return ('ok')

    def get_zdallmonitor(self,addr):
        self.s.sendline('enable')
        self.s.expect(self.prompt)
        self.s.sendline('debug')
        self.s.expect(self.prompt)
        self.s.sendline('script')
        self.s.expect(self.prompt)
        cmd = 'exec zdallmonitor.sh %s' % addr
        #self.s.sendline('exec zdmaclist.sh addr')
        self.s.sendline(cmd)
        self.s.expect(self.prompt)  
        return ('ok') 
    
    def get_supportfile(self,aplist,addr):
        self.s.sendline('enable')
        self.s.expect(self.prompt)
        self.s.sendline('debug')
        self.s.expect(self.prompt)
        self.s.sendline('script')
        self.s.expect(self.prompt)
        for ap in aplist:
            ap = ap.replace('_',':')       
            cmd = 'exec testsupport.sh %s %s' % (ap,addr)
            self.s.sendline(cmd)
            self.s.expect(self.prompt)  
        return ('ok') 
    def get_dramdump(self,aplist,addr):
        self.s.sendline('enable')
        self.s.expect(self.prompt)
        self.s.sendline('debug')
        self.s.expect(self.prompt)
        self.s.sendline('script')
        self.s.expect(self.prompt)
        for a in aplist:
            ap = a[0]
            ap = ap.replace('_',':')
            interface = a[1]
            cmd = 'exec dramdump.sh %s %s %s' % (ap,interface,addr)
            self.s.sendline(cmd)
            self.s.expect(self.prompt)  
        return ('ok')     
    def get_aplist(self):
        res = self.cmd("wlaninfo -A | grep ^AP")
        return [aline.strip().split()[5] for aline in res]

    def get_apnamelist(self,ap):
        res = self.cmd("rksap_cli -a %s -s \"hostname\"" % ap)
        #return [aline.strip().split()[5] for aline in res]
        if res: 
            if len(res) > 1:
                return res[1] 
            else: 
                return 
            
    def get_apname(self,ap):
        '''self.s.sendline('enable')
        self.s.expect(self.prompt)
        self.s.sendline('debug')
        self.s.expect(self.prompt)
        self.s.sendline('script')
        self.s.expect(self.prompt)  '''
        cmd = 'exec getapname.sh %s' % ap
        self.s.sendline(cmd)
        self.s.expect(self.prompt)
        rx = self.s.before
        print rx
        if rx:
            return rx

        else:
            return

    def get_aptime(self,ap):
        res = self.cmd("rksap_cli -a %s -s \"date\"" % ap)
        #return [aline.strip().split()[5] for aline in res]
        if res: 
            if len(res) > 1:
                return res[1] 
            else: 
                return 

    def get_apmaclist(self):
        #res = self.cmd("wlaninfo -A | grep ^AP")
        #return [(aline.strip().split()[1].split(',')[0],aline.strip().split()[5]) for aline in res]
        #return res
        ok = self.cmd("cd /writable")
        ok = self.cmd("./zd_script_for_maclist.sh")
        return (ok)
 
    def run_monitor_script(self):
        ok = self.cmd("cd /writable")
        ok = self.cmd("./zd_script_for_network_monitor.sh")
        return (ok)
 
    def run_monitor_for_all_script(self):
        ok = self.cmd("cd /writable")
        ok = self.cmd("./zd_script_for_all_monitor.sh")
        return (ok)
    
    def run_get_support_script(self,aplist):
        ok = self.cmd("cd /writable")
        for ap in aplist:
            
            mycmd = "./testsupport.sh %s" % ap.replace('_',':')
            ok = self.cmd(mycmd)
        return (ok)    
    def get_zdstats(self,cmd):
        if cmd == 'ifconfig':
            cmd1 = cmd
        else:
            cmd1 = "wlaninfo %s " % cmd
        res = self.cmd(cmd1)
        return res

    def get_radiobssid(self, mac):
        res = self.cmd("wlaninfo -s %s" % mac)
        x = res[1].split(' ')
        return (x[6], x[4])


    def get_stalist(self):
        stal = self.cmd("wlaninfo -S | grep ^Station")
        stal = [aline.strip().split() for aline in stal]
        #print stal 
        #stal = [(x[1],x[-1][1:]) for x in stal]  # This works for ZD image 9.2 or below
        stal = [(x[1],x[10][1:-1]) for x in stal]   # This works for ZD image 9.4 and above
        return [(mac, ip, self.get_radiobssid(mac)) for mac,ip in stal]

    def close(self):
        self.s.close()

if __name__ == "__main__":

    pass
    '''zd = ZDCLI('172.16.20.3')
    zd.connect('admin','video54java')
    res = zd.set_snifferchan()   
    print res
    if len(sys.argv) >= 6:
        zd.to_shell()
        res = zd.cmd(sys.argv[5])
        for aline in res:
            print aline  '''
