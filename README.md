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
Automatic discovery of the AdminAPI randomly generated password (HS 7.2.2.x)
Option : push the HAProxy config. directly to the HAProxy host
Automatic refresh of the stat page
Email notification
Backup DC

# Tested On
Tested on CentOS 7.5-7.7, Python 2.7.x - 3.8 HyperStore 7.1.x (4, 5 and 7) & 7.2.x (up to 7.2.2)
Tested on HAProxy (avoid versions < 2.0 for my testing - deprecated parameters), 2.1 & 2.2 (LTS)
Cloudian clusters : from 1 to 12 nodes for PoC or Production environment.
Remote workstation : Should work on all OS which can support Python. Tested on my Debian Buster with Python 2.7.x and 3.8 (regular testing)

# Deployment
Download only the files below and put them into a directory of your choice (ex : /root/haproxy_config/) :

	haproxy_config.py
  	haproxy_template.cfg

You need to have also some files (from the Cloudian cluster / Puppet Master Host) if you execute this tool outside of the cloudian cluster :
(notice : For 7.0 and 7.1 releases --> the "Staging Directory" is by default : /root/CloudianPackages for the standard deployment excluding any software upgrade).
(notice : For 7.2 release --> the "Staging Directory" is by default : /opt/cloudian-staging/7.2 for the standard deployment excluding any software upgrade).

	<Staging Directory>/survey.csv
  	<Staging Directory>/CloudianInstallConfiguration.txt
  	/etc/cloudian-<HS-version>-puppet/manifests/extdata/common.csv

Then, with the new version of the tool, we can discover automatically the Cloudian staging directory if it is on the Puppet Master host.

# Run & Usage

**if you want to have the command usage, just run the script with --help option**

    [root@cloudlab01 ~]# python haproxy_config.py  --help
    usage: haproxy_config.py [-h] [-s SURVEY] [-i INSTALL] [-c COMMON]
                             [-bs3 BACKUPS3] [-ms MAILSERVER] [-mf MAILFROM]
                             [-mt MAILTO]
    
    parameters for the script
    
    optional arguments:
      -h, --help            show this help message and exit
      -s SURVEY, --survey SURVEY
                            indicate the survey file, default = survey.csv
      -i INSTALL, --install INSTALL
                            indicate the installation file, default =
                            CloudianInstallConfiguration.txt
      -c COMMON, --common COMMON
                            indicate the common.csv file, default = common.csv
      -bs3 BACKUPS3, --backups3 BACKUPS3
                            indicate the DC in backup/stand-by mode for s3,
                            default=none
      -ms MAILSERVER, --mailserver MAILSERVER
                            mail server name or @IP for alerts
      -mf MAILFROM, --mailfrom MAILFROM
                            indicate the sender, default = haproxy@localhost
      -mt MAILTO, --mailto MAILTO
                            indicate the recipient, default = root@localhost


**Common and standard uses from the Puppet Master Host**
**You can run a single line without any option and push the config on the HAProxy host directly (most standard use for 1 or more DCs) :**
    
    [root@cloudlab01 ~]# python haproxy_config.py 
    We are considering the following path as the current path for the cloudian installation : /opt/cloudian-staging/7.2.2/
    Common config path found too.
    
     Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
    
    You need to have the root access to push this config.
    Do you want to push & run this config file to your haproxy server ? (yes / no) : yes
    Please, enter the IP address or the hostname of your haproxy server : cloudlab-haproxy
    Enter the root password for the connexion ... 
    Password: **********
    Trying to connect to the host : cloudlab-haproxy with the root password ... and then checking some parameters for you ...
    HA-Proxy version 2.2.3-0e58a34 2020/09/08 - https://haproxy.org/
    Enabling the haproxy service on the haproxy server...
    haproxy.service is not a native service, redirecting to systemd-sysv-install.
    Executing: /usr/lib/systemd/systemd-sysv-install enable haproxy
    Backing up the old config on the haproxy server...
    Copying config file to haproxy server...
    Restarting haproxy service on the haproxy server...
    Checking status of haproxy service...
    ● haproxy.service - SYSV: HA-Proxy is a TCP/HTTP reverse proxy which is particularly suited for high availability environments.
       Loaded: loaded (/etc/rc.d/init.d/haproxy; generated)
       Active: active (running) since Fri 2020-10-02 12:12:29 EDT; 416ms ago
         Docs: man:systemd-sysv-generator(8)
      Process: 11646 ExecStop=/etc/rc.d/init.d/haproxy stop (code=exited, status=0/SUCCESS)
      Process: 11657 ExecStart=/etc/rc.d/init.d/haproxy start (code=exited, status=0/SUCCESS)
     Main PID: 11668 (haproxy)
        Tasks: 2 (limit: 23988)
       Memory: 18.9M
       CGroup: /system.slice/haproxy.service
               └─11668 /usr/sbin/haproxy -D -f /etc/haproxy/haproxy.cfg -p /var/run/haproxy.pid
    
    Oct 02 12:12:29 haproxy systemd[1]: Stopped SYSV: HA-Proxy is a TCP/HTTP reverse proxy which is particularly suited for high availability environments..
    Oct 02 12:12:29 haproxy systemd[1]: Starting SYSV: HA-Proxy is a TCP/HTTP reverse proxy which is particularly suited for high availability environments....
    Oct 02 12:12:29 haproxy haproxy[11657]: Starting haproxy: [  OK  ]
    Oct 02 12:12:29 haproxy systemd[1]: Started SYSV: HA-Proxy is a TCP/HTTP reverse proxy which is particularly suited for high availability environments..


**Those lines are suggested as quick examples without config push**

For example, the tool is uploaded to /root directory on the puppet master and we run it from here without any parameters.

Quick example on 7.1.x HS release :
 
    [root@cloudian7.1.4 ~]# python haproxy_config.py 
    We are considering the following path as the current path for the cloudian installation : /root/CloudianPackages/
    Common config path found too.
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
    We are considering the following path as the current path for the cloudian installation : /opt/cloudian-staging/7.2.2/
    Common config path found too.
    
     Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
    
    You need to have the root access to push this config.
    Do you want to push & run this config file to your haproxy server ? (yes / no) : no
    Enable the haproxy service on the haproxy server via systemctl command
    next, copy the file haproxy.cfg to the haproxy server (into /etc/haproxy/)
    Then restart the haproxy service on the haproxy server.


**or use the options to specify the files required (remote workstation in this example) :**

     plong@snoopy:~$ python haproxy_config.py -s ./config_7.2.2_three_nodes/survey.csv -i ./config_7.2.2_three_nodes/CloudianInstallConfiguration.txt -c ./config_7.2.2_three_nodes/common.csv
     We are considering this host is NOT the Cloudian puppet master
     
      Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
     
     You need to have the root access to push this config.
     Do you want to push & run this config file to your haproxy server ? (yes / no) : yes
     Please, enter the IP address or the hostname of your haproxy server : cloudlab-haproxy
     Enter the root password for the connexion ... 
     Password: 
     Trying to connect to the host : cloudlab-haproxy with the root password ... and then checking some parameters for you ...
     HA-Proxy version 2.2.3-0e58a34 2020/09/08 - https://haproxy.org/
     Enabling the haproxy service on the haproxy server...
     haproxy.service is not a native service, redirecting to systemd-sysv-install.
     Executing: /usr/lib/systemd/systemd-sysv-install enable haproxy
     Backing up the old config on the haproxy server...
     Copying config file to haproxy server...
     Restarting haproxy service on the haproxy server...
     Checking status of haproxy service...
     ● haproxy.service - SYSV: HA-Proxy is a TCP/HTTP reverse proxy which is particularly suited for high availability environments.
        Loaded: loaded (/etc/rc.d/init.d/haproxy; generated)
        Active: active (running) since Fri 2020-10-02 12:31:43 EDT; 346ms ago
          Docs: man:systemd-sysv-generator(8)
       Process: 12252 ExecStop=/etc/rc.d/init.d/haproxy stop (code=exited, status=0/SUCCESS)
       Process: 12263 ExecStart=/etc/rc.d/init.d/haproxy start (code=exited, status=0/SUCCESS)
      Main PID: 12275 (haproxy)
         Tasks: 2 (limit: 23988)
        Memory: 18.9M
        CGroup: /system.slice/haproxy.service
                └─12275 /usr/sbin/haproxy -D -f /etc/haproxy/haproxy.cfg -p /var/run/haproxy.pid
     
     Oct 02 12:31:43 haproxy haproxy[12274]: Proxy https.s3-cloudlab.demo.lab started.
     Oct 02 12:31:43 haproxy haproxy[12274]: Proxy https.s3-cloudlab.demo.lab started.
     Oct 02 12:31:43 haproxy haproxy[12274]: Proxy s3-cloudlab-admin.demo.lab started.
     Oct 02 12:31:43 haproxy haproxy[12274]: Proxy s3-cloudlab-admin.demo.lab started.
     Oct 02 12:31:43 haproxy haproxy[12274]: Proxy s3-cloudlab-iam.demo.lab started.
     Oct 02 12:31:43 haproxy haproxy[12274]: Proxy s3-cloudlab-iam.demo.lab started.
     Oct 02 12:31:43 haproxy haproxy[12274]: Proxy https.s3-cloudlab-iam.demo.lab started.
     Oct 02 12:31:43 haproxy haproxy[12274]: Proxy https.s3-cloudlab-iam.demo.lab started.
     Oct 02 12:31:43 haproxy haproxy[12263]: Starting haproxy: [  OK  ]
     Oct 02 12:31:43 haproxy systemd[1]: Started SYSV: HA-Proxy is a TCP/HTTP reverse proxy which is particularly suited for high availability environments..
      

**For two DCs or more without any preferences. you can use it with the same way.**
       **=> load-balancing will occur on all nodes in the same manner.**

In this case, you can run the command line like you would run it for 1 DC.
All the nodes will be treated as others and the requests will be propagated to all nodes available no matter the location (aka DC).


**For 2 DCs with a DC as backup : choice to have one active and the second passive for s3 service, you must run the command line with the option "--backups3".**

In this example, we have 2 DataCenters : dc01 and dc02. 
The dataCenter "dc01" is the active datacenter for the s3 requests and dc02 is only the passive dataCenter (backup for s3 => bs3) in case of a DC failure.
Based on that choice, all s3 requests will be sent by HAProxy to only the "dc01" nodes in a nominal state else on the "dc02" nodes (in case of a failure of dc01).
(notice : I answered 'no' to the question "push & run" but you can answer 'yes')

    [root@cloudlab01 ~]# python haproxy_config.py -bs3 dc02
    We are considering the following path as the current path for the cloudian installation : /opt/cloudian-staging/7.2.2/
    Common config path found too.
    
     Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
    
    You need to have the root access to push this config.
    Do you want to push & run this config file to your haproxy server ? (yes / no) : no
    Enable the haproxy service on the haproxy server via systemctl command
    next, copy the file haproxy.cfg to the haproxy server (into /etc/haproxy/)
    Then restart the haproxy service on the haproxy server.

This option is useful if the datacenter dc01 is the main datacenter where all the infrastructure is present.
The datacenter dc02 has Cloudian nodes with a limited infrastructure.
You would like to limit the bandwidth usage between the datacenters.
(avoid : sending a s3 request to dc02 although all your s3 clients are based on dc01 except if dc01's nodes are down)


**If you want to enable the mail parameters and send some alerts in case of a node or a service down, follow this :**
The email is sent only when the service/server becomes unreachable (no email sent when the service/server comes up)
(notice : I answered 'no' to the question "push & run" but you can answer 'yes')

    [root@cloudlab01 ~]# python haproxy_config.py -ms smtp.demo.lab -mf haproxy@demo.lab -mt adminsys@demo.lab
    We are considering the following path as the current path for the cloudian installation : /opt/cloudian-staging/7.2.2/
    Common config path found too.
    
     Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
    
    You need to have the root access to push this config.
    Do you want to push & run this config file to your haproxy server ? (yes / no) : no
    Enable the haproxy service on the haproxy server via systemctl command
    next, copy the file haproxy.cfg to the haproxy server (into /etc/haproxy/)
    Then restart the haproxy service on the haproxy server.

Notice : During maintenance operations like reboots of nodes, your email server might deal with several emails (one per service down).


**If you have answered 'no' and you don't want to push automatically the haproxy config file into the HAProxy host**

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
1.0

# Bugs & Suggestions
Any bugs or suggestions, please contact the author directly.

# Author
Peter Long
