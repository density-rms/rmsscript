#TFTP SERVER IP Address need to be changed as REQUIRED

TFTP_SERVER=10.150.13.7

cd /tmp
TS=`date +%m%d_%H%M`
wlaninfo -A | grep ^AP | awk '{print $2}' > maclist
APLIST=/tmp/maclist
#wlaninfo -A | awk '/Addr/{printf "%s ", $2}/Model/{print $3}' | grep -v zf > $APLIST

for ap in `cut -d',' -f1 $APLIST`; do
    echo "$ap ..."
    aap=${ap//:/_}
    b=`rksap_cli -a $ap -s "top -n 1"> /writable/datafile.$aap` 
    b=`rksap_cli -a $ap -s "uptime">> /writable/datafile.$aap` 
    b=`rksap_cli -a $ap -s "hostname">> /writable/datafile.$aap` 
    b=`rksap_cli -a $ap -s "nodestats">> /writable/datafile.$aap` 
    b=`rksap_cli -a $ap -s "nodestats wifi1">> /writable/datafile.$aap` 
    b=`rksap_cli -a $ap -s "logread"> /writable/logread.$aap` 
        
    b=`rksap_cli -a $ap -s "athstats -i wifi1 | grep 'beacons transmitted' "` 
    b_no=`echo $b | awk '{print $1}'`
    sleep 10
    b_new=`rksap_cli -a $ap -s "athstats -i wifi1 |grep 'beacons transmitted'"` 
    b_no_new=`echo $b_new | awk '{print $1}'`
    if [ $b_no -eq $b_no_new ]
    then
      
        if [ "$b_no" != "" ]
            then
               echo "$b_no ..."
               echo 'beacon stuck found collecting all logs' >> /writable/datafile.$aap
        fi
    fi
    rksap_cli -a $ap -s "cat /dev/v54rb2" >> /writable/datafile.$aap
    #tar -czf /writable/output_$aap.tgz /writable/*.$aap
    #tftp -p -l /writable/output_$aap.tgz -r output_$aap-$TS.tgz $TFTP_SERVER
    #rm -rf /writable/*.$aap
    #rm -rf /writable/*.tgz
    
    #rksap_cli -a $ap  "support"
    #sleep 10
    #rksap_cli -a $ap -s "cat /tmp/support" > /writable/support$aap.txt
done
    #tar -czf /writable/supportall.tgz /writable/support*.txt
    #tftp -p -l /writable/supportall.tgz -r supportall-$TS.tgz $TFTP_SERVER
    #rm -rf /writable/support*.txt    
    #rm -rf /writable/supportall.tgz    

    tar -czf /writable/datafileall.tgz /writable/datafile.*
    tar -czf /writable/logreadall.tgz /writable/logread.*
    tftp -p -l /writable/datafileall.tgz -r datafileall.tgz $TFTP_SERVER
    tftp -p -l /writable/logreadall.tgz -r logreadall.tgz $TFTP_SERVER
    tftp -p -l /var/log/ap.log -r ap.log $TFTP_SERVER
    rm -rf /writable/datafile*
    rm -rf /writable/logread*

