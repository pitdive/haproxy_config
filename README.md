# HAproxy Config
Script to build a HAProxy config file based on a Cloudian cluster config.

# Description
The goal is to build a HAPROXY configuration file (haproxy.cfg) based on the information already in place for the Cloudian cluster.
The result is a config file for a dedicated load-balancer (1 host or 1 VM) to Cloudian cluster.

This is a simple way to avoid misconfiguration for HAProxy config file (typo error, etc.) during installation for PoC and test (SE tool or tool provided to a customer) or multi-automated-installation via Vagrant

# Disclaimer / Warning
Use this tool with precautions (review the config file created manually for a double-check) for your environment : it is not an official tool supported by Cloudian.
Cloudian can NOT be involved for any bugs or misconfiguration due to this tool. So you are using it at your own risks and be aware of the restrictions.

# Features
Compatible with HyperStore 7.1 & 7.2 (IAM add-on) 
Automatic discovery of the staging directory 
Option : push the HAProxy config. directly to the HAProxy host
Automatic refresh of the stat page
Email notification
Backup DC

# Tested On
Tested on CentOS 7.5, Python 2.7.x & 3.7, HyperStore 7.1.x (4, 5 and 7) & 7.2
Tested on HAProxy (avoid versions < 1.8 for my testing - unmaintained), minimum is 1.8.x (LTS), 2.0 (LTS) and 2.1.2 
Cloudian clusters : from 1 to 12 nodes for PoC or Production environment.
Remote workstation : Should work on all OS which can support Python. Tested on my Debian Buster with Python 2.7.x and 3.7 (regular testing)

# Deployment
Download only the files below and put them into a directory of your choice (ex : /root/haproxy_config/) :

	haproxy_config.py
  	haproxy_template.cfg

or use the rpm package :

    haproxy_config-<version>.rpm
    
    By default, the rpm installation destination is :
    /root/haproxy_config/

You need to have also the files (from the Cloudian cluster / Puppet Master Host) :
(notice : For 7.0 and 7.1 releases --> the "Staging Directory" is by default : /root/CloudianPackages for the standard deployment excluding any software upgrade).
(notice : For 7.2 release --> the "Staging Directory" is by default : /opt/cloudian-staging/7.2 for the standard deployment excluding any software upgrade).

	<Staging Directory>/survey.csv
  	<Staging Directory>/CloudianInstallConfiguration.txt

Then, with the new version of the tool, we can discover automatically the Cloudian staging directory. You do not need to locate those files anymore.
  
Of course, it is still possible to run the script in a directory of your choice (containing those 4 files) or explicitly specify the files mentioned above in the command line with the optional parameters (look at the "Run" Chapter).

# Run & Usage

**if you want to have the command usage, just run the script with --help option**

    [root@cloudlab01 7.2]# python haproxy_config.py --help
    usage: haproxy_config.py [-h] [-s SURVEY] [-i INSTALL] [-bs3 BACKUPS3]
                             [-ms MAILSERVER] [-mf MAILFROM] [-mt MAILTO]
    
    parameters for the script
    
    optional arguments:
      -h, --help            show this help message and exit
      -s SURVEY, --survey SURVEY
                            indicate the survey file, default = survey.csv
      -i INSTALL, --install INSTALL
                            indicate the installation file, default =
                            CloudianInstallConfiguration.txt
      -bs3 BACKUPS3, --backups3 BACKUPS3
                            indicate the DC in backup/stand-by mode for s3,
                            default=none
      -ms MAILSERVER, --mailserver MAILSERVER
                            mail server name or @IP for alerts
      -mf MAILFROM, --mailfrom MAILFROM
                            indicate the sender, default = haproxy@localhost
      -mt MAILTO, --mailto MAILTO
                            indicate the recipient, default = root@localhost

**Those lines are suggested only for the demonstration**

For example, the tool is uploaded to /root directory on the puppet master and we run it from here without any parameters.

Quick example on 7.1.x HS release :
 
    [root@cloudlab01 ~]# python haproxy_config.py 
    We are considering the following path as the current path for the cloudian installation : /root/CloudianPackages/
     *** IAM Endpoint not found. Looks like it is an older version : HS 7.0.x or 7.1.x *** 
    Your HAProxy config file will use a temporary iam domain instead like : iam.not-yet-configured
    
     Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
    
    You need to have the root access to push this config.
    Do you want to push & run this config file to your haproxy server ? (yes / no) : no
    Enable the haproxy service on the haproxy server via systemctl command
    next, copy the file haproxy.cfg to the haproxy server (into /etc/haproxy/)
    Then restart the haproxy service on the haproxy server.

Quick example on 7.2 HS release :

	[root@cloudlab01 ~]# python haproxy_config.py 
    We are considering the following path as the current path for the cloudian installation : /opt/cloudian-staging/7.2/
    
     Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
    
    You need to have the root access to push this config.
    Do you want to push & run this config file to your haproxy server ? (yes / no) : no
    Enable the haproxy service on the haproxy server via systemctl command
    next, copy the file haproxy.cfg to the haproxy server (into /etc/haproxy/)
    Then restart the haproxy service on the haproxy server.


**For only 1 DC, you can run a single line without any option and push the config on the haproxy host directly :**

	[root@cloudlab01]# python haproxy_config.py 
    We are considering the following path as the current path for the cloudian installation : /root/CloudianPackages/
     *** IAM Endpoint not found. Looks like it is an older version : HS 7.0.x or 7.1.x *** 
    Your HAProxy config file will use a temporary iam domain instead like : iam.not-yet-configured
    
     Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
    
    You need to have the root access to push this config.
    Do you want to push & run this config file to your haproxy server ? (yes / no) : yes
    Please, enter the IP address or the hostname of your haproxy server : 172.16.11.230
    Enter the root password for the connexion ... 
    Password: ********
    Trying to connect to the host : 192.168.110.200 with the root password ... and then checking some parameters for you ...
    Enabling the haproxy service on the haproxy server...
    Backing up the old config on the haproxy server...
    Copying config file to haproxy server...
    Restarting haproxy service on the haproxy server...
    Checking status of haproxy service...
    ● haproxy.service - HAProxy Load Balancer
       Loaded: loaded (/usr/lib/systemd/system/haproxy.service; enabled; vendor preset: disabled)
       Active: active (running) since Wed 2020-02-26 14:20:12 CET; 236ms ago
      Process: 1314 ExecStartPre=/usr/sbin/haproxy -f $CONFIG -c -q (code=exited, status=0/SUCCESS)
     Main PID: 1315 (haproxy)
       CGroup: /system.slice/haproxy.service
               ├─1315 /usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid
               └─1317 /usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid
    
    Feb 26 14:20:12 cloudlab-haproxy haproxy[1315]: Proxy s3-cloudlab.demo.lab started.
    Feb 26 14:20:12 cloudlab-haproxy haproxy[1315]: Proxy s3-cloudlab.demo.lab started.
    Feb 26 14:20:12 cloudlab-haproxy haproxy[1315]: Proxy https.s3-cloudlab.demo.lab started.
    Feb 26 14:20:12 cloudlab-haproxy haproxy[1315]: Proxy https.s3-cloudlab.demo.lab started.
    Feb 26 14:20:12 cloudlab-haproxy haproxy[1315]: Proxy s3-cloudlab-admin.demo.lab started.
    Feb 26 14:20:12 cloudlab-haproxy haproxy[1315]: Proxy s3-cloudlab-admin.demo.lab started.
    Feb 26 14:20:12 cloudlab-haproxy haproxy[1315]: Proxy iam.not-yet-configured started.
    Feb 26 14:20:12 cloudlab-haproxy haproxy[1315]: Proxy iam.not-yet-configured started.
    Feb 26 14:20:12 cloudlab-haproxy haproxy[1315]: Proxy https.iam.not-yet-configured started.
    Feb 26 14:20:12 cloudlab-haproxy haproxy[1315]: Proxy https.iam.not-yet-configured started.


**or use the options to specify the files required :**

    [root@cloudlab01 ~]# ls
    haproxy_config.py  haproxy_template.cfg
    [root@cloudlab01 ~]# python haproxy_config.py -s /opt/cloudian-staging/7.2/survey.csv -i /opt/cloudian-staging/7.2/CloudianInstallConfiguration.txt 
    
     Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
    
    Do you want to push & run this config file to your haproxy server ? (yes / no) :yes
    Please, enter the IP address or the hostname of your haproxy server :172.16.11.230
    Enter the root password for the connexion
    Password: **********
    Trying to connect to the host : 172.16.11.230 and then enabling the haproxy service on the haproxy server...
    Backing up the old config on the haproxy server...
    Copying config file to haproxy server...
    Restarting haproxy service on the haproxy server...
    Checking status of haproxy service...
    ● haproxy.service - HAProxy Load Balancer
       Loaded: loaded (/usr/lib/systemd/system/haproxy.service; enabled; vendor preset: disabled)
       Active: active (running) since Fri 2019-12-13 18:18:50 UTC; 432ms ago
     Main PID: 2089 (haproxy-systemd)
       CGroup: /system.slice/haproxy.service
               ├─2089 /usr/sbin/haproxy-systemd-wrapper -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid
               ├─2090 /usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -Ds
               └─2091 /usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -Ds
    
    Dec 13 18:18:50 cloudlab-haproxy haproxy[2090]: Proxy s3-cloudlab.demo.lab started.
    Dec 13 18:18:50 cloudlab-haproxy haproxy[2090]: Proxy s3-cloudlab.demo.lab started.
    Dec 13 18:18:50 cloudlab-haproxy haproxy[2090]: Proxy https.s3-cloudlab.demo.lab started.
    Dec 13 18:18:50 cloudlab-haproxy haproxy[2090]: Proxy https.s3-cloudlab.demo.lab started.
    Dec 13 18:18:50 cloudlab-haproxy haproxy[2090]: Proxy s3-admin.demo.lab started.
    Dec 13 18:18:50 cloudlab-haproxy haproxy[2090]: Proxy s3-admin.demo.lab started.
    Dec 13 18:18:50 cloudlab-haproxy haproxy[2090]: Proxy iam.demo.lab started.
    Dec 13 18:18:50 cloudlab-haproxy haproxy[2090]: Proxy iam.demo.lab started.
    Dec 13 18:18:50 cloudlab-haproxy haproxy[2090]: Proxy https.iam.demo.lab started.
    Dec 13 18:18:50 cloudlab-haproxy haproxy[2090]: Proxy https.iam.demo.lab started.
         
    [root@cloudlab01 ~]# ls
    haproxy.cfg  haproxy_config.py  haproxy_template.cfg 


**or use a remote workstation where you have uploaded the files required :**

    plong@snoopy:~/MyProject$ python haproxy_config.py 
    We are considering this host is not the Cloudian puppet master
     *** IAM Endpoint not found. Looks like it is an older version : HS 7.0.x or 7.1.x *** 
    Your HAProxy config file will use a temporary iam domain instead like : iam.not-yet-configured

     Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
    
    Do you want to push & run this config file to your haproxy server ? (yes / no) : yes
    Please, enter the IP address or the hostname of your haproxy server : 172.16.11.230
    Enter the root password for the connexion
    Password: **********
    Trying to connect to the host : 172.16.11.230 and then enabling the haproxy service on the haproxy server...
    Warning: Permanently added '172.16.11.230' (ECDSA) to the list of known hosts.
    Backing up the old config on the haproxy server...
    Copying config file to haproxy server...
    Restarting haproxy service on the haproxy server...
    Checking status of haproxy service...
    ● haproxy.service - HAProxy Load Balancer
       Loaded: loaded (/usr/lib/systemd/system/haproxy.service; enabled; vendor preset: disabled)
       Active: active (running) since Fri 2019-12-13 18:24:14 UTC; 452ms ago
     Main PID: 2155 (haproxy-systemd)
       CGroup: /system.slice/haproxy.service
               ├─2155 /usr/sbin/haproxy-systemd-wrapper -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid
               ├─2156 /usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -Ds
               └─2159 /usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -Ds
    
    Dec 13 18:24:14 cloudlab-haproxy haproxy[2156]: Proxy s3-cloudlab.demo.lab started.
    Dec 13 18:24:14 cloudlab-haproxy haproxy[2156]: Proxy s3-cloudlab.demo.lab started.
    Dec 13 18:24:14 cloudlab-haproxy haproxy[2156]: Proxy https.s3-cloudlab.demo.lab started.
    Dec 13 18:24:14 cloudlab-haproxy haproxy[2156]: Proxy https.s3-cloudlab.demo.lab started.
    Dec 13 18:24:14 cloudlab-haproxy haproxy[2156]: Proxy s3-admin.demo.lab started.
    Dec 13 18:24:14 cloudlab-haproxy haproxy[2156]: Proxy s3-admin.demo.lab started.
    Dec 13 18:24:14 cloudlab-haproxy haproxy[2156]: Proxy iam.demo.lab started.
    Dec 13 18:24:14 cloudlab-haproxy haproxy[2156]: Proxy iam.demo.lab started.
    Dec 13 18:24:14 cloudlab-haproxy haproxy[2156]: Proxy https.iam.demo.lab started.
    Dec 13 18:24:14 cloudlab-haproxy haproxy[2156]: Proxy https.iam.demo.lab started.


**For two DCs or more without any preferences. you can use it with the same way.**
       **=> load-balancing will occur on all nodes in the same manner.**

In this case, you can run the command line like you would run it for 1 DC.
All the nodes will be treated as others and the requests will be propagated to all nodes available no matter the location (aka DC).


**For 2 DCs with a DC as backup : choice to have one active and the second passive for s3 service, you must run the command line with the option "--backups3".**

In this example, we have 2 DataCenters : dc1 and dc2. 
The dataCenter "dc1" is the active datacenter for the s3 requests and dc2 is only the passive dataCenter in case of a DC failure.
Based on that choice, all s3 requests will be sent by HAProxy to only the "dc1" nodes in a nominal state else on the "dc2" nodes (in case of a failure of dc1).
(notice : I answered 'no' to the question "push & run" but you can answer 'yes')

    [root@cloudlab01 ~]# python haproxy_config.py -bs3 dc2
    
     Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
    
    Do you want to push & run this config file to your haproxy server ? (yes / no) :no
    Please copy the file haproxy.cfg on the haproxy server (into /etc/haproxy/)
    Then restart the haproxy service on the haproxy server via systemctl command
    example : systemctl restart haproxy


This option is useful if the datacenter dc1 is the main datacenter where all the infrastructure is present.
The datacenter dc2 has Cloudian ndoes with a limited infrastructure.
You would like to limit the bandwidth usage between the datacenters.
(avoid : sending a s3 request to dc2 although all your s3 clients are based on dc1 except if dc1 nodes are down)


**If you want to enable the mail parameters and send some alerts in case of a node or a service down, follow this :**
The email is sent only when the service/server becomes unreachable (no email sent when the service/server comes up)
(notice : I answered 'no' to the question "push & run" but you can answer 'yes')

    [root@cloudlab01 ~]# python haproxy_config.py -ms smtp.demo.lab -mf haproxy@demo.lab -mt adminsys@demo.lab
    
     Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
    
    Do you want to push & run this config file to your haproxy server ? (yes / no) :no
    Please copy the file haproxy.cfg on the haproxy server (into /etc/haproxy/)
    Then restart the haproxy service on the haproxy server via systemctl command
    example : systemctl restart haproxy

Notice : During maintenance operations like reboots of nodes, your email server might deal with several emails (one per service down).


**If you have answered 'no' and you don't want to push automatically the haproxy config file**

Just grab the haproxy.cfg file created in the local directory and send it to the haproxy server (aka the load-balancer host)

you might want to backup the previous configuration of HAProxy on your HAProxy server. So, do it before please.

	[root@cloudlab01 ~]# ls
    haproxy.cfg  haproxy_config.py  haproxy_template.cfg
	
	[root@cloudlab01 ~]# scp haproxy.cfg root@haproxy_server:/etc/haproxy/haproxy.cfg

Go to the HAProxy server by using SSH (or a console), then restart the haproxy service as mentioned.

    plong@snoopy:~$ ssh -l root haproxy_server
    root@haproxy's password: ********
    #
    [root@haproxy ~]# systemctl restart haproxy
    #
    [root@haproxy ~]# systemctl status haproxy
    ● haproxy.service - HAProxy Load Balancer
       Loaded: loaded (/usr/lib/systemd/system/haproxy.service; enabled; vendor preset: disabled)
       Active: active (running) since Fri 2019-06-14 16:53:46 CEST; 2s ago
     Main PID: 1010 (haproxy-systemd)
       CGroup: /system.slice/haproxy.service
               ├─1010 /usr/sbin/haproxy-systemd-wrapper -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid
               ├─1011 /usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -Ds
               └─1012 /usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -Ds
    
    Jun 14 16:53:46 haproxy haproxy[1011]: Proxy cmc.demo.lab started.
    Jun 14 16:53:46 haproxy haproxy[1011]: Proxy cmc.demo.lab started.
    Jun 14 16:53:46 haproxy haproxy[1011]: Proxy https.cmc.demo.lab started.
    Jun 14 16:53:46 haproxy haproxy[1011]: Proxy https.cmc.demo.lab started.
    Jun 14 16:53:46 haproxy haproxy[1011]: Proxy s3-fr.demo.lab started.
    Jun 14 16:53:46 haproxy haproxy[1011]: Proxy s3-fr.demo.lab started.
    Jun 14 16:53:46 haproxy haproxy[1011]: Proxy https.s3-fr.demo.lab started.
    Jun 14 16:53:46 haproxy haproxy[1011]: Proxy https.s3-fr.demo.lab started.
    Jun 14 16:53:46 haproxy haproxy[1011]: Proxy s3-admin.demo.lab started.
    Jun 14 16:53:46 haproxy haproxy[1011]: Proxy s3-admin.demo.lab started.


# Version
0.7

# Bugs & Suggestions
Any bugs or suggestions, please contact the author directly.

# Author
Peter Long
