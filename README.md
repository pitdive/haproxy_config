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
Compatible with HyperStore 7.1, 7.2 (IAM TCP healthcheck only), 7.3 and **7.4**
Automatic discovery of the **staging directory**
Automatic discovery of the AdminAPI randomly generated password (HS 7.2.2.x and higher)
Automatic discovery and config. adjustement for **Proxy Protocol**
Option : push the HAProxy config. directly to the HAProxy host
Automatic refresh of the stats page + legends/pop-ups (HTTP code responses from 1xx to 5xx, ipv4 info, balance method, etc)
Email notification
Backup DC
Force **TLS > 1.2**
**MaxConn** parameter per node

# Tested On
### Avoid HAProxy < 2.0 due to deprecated parameters and this tool uses now the new parameters ###
### Consider to use HAProxy >= 2.2, prefer the LTS support on 2.2 or 2.4 ###
Tested on :
       Cloudian nodes : CentOS 7.5-7.9
       HyperStore : 7.1.x (4, 5 and 7) & 7.2.x (up to 7.2.4) & 7.3.2 & 7.4
       Python : 2.7.x - 3.9 
       Tested on HAProxy : 2.2 to 2.4 (LTS)
              last test on Debian --> HAProxy version 2.4.15-1 2022/03/14 - https://haproxy.org/
              Status: long-term supported branch - will stop receiving fixes around Q2 2026.
              Known bugs: http://www.haproxy.org/bugs/bugs-2.4.15.html
              Running on: Linux 5.16.0-5-amd64 #1 SMP PREEMPT Debian 5.16.14-1 (2022-03-15) x86_64
              **Options : USE_PCRE2=1 USE_PCRE2_JIT=1 USE_OPENSSL=1 USE_LUA=1 USE_SLZ=1 USE_SYSTEMD=1 USE_OT=1 USE_PROMEX=1**
              **multi-threading support**
              **Running on OpenSSL version : OpenSSL 1.1.1n  15 Mar 2022**
              **OpenSSL library supports : TLSv1.0 TLSv1.1 TLSv1.2 TLSv1.3**
       Cloudian clusters : from 1 to several nodes for PoC or Production environment (tested on 12 nodes cluster/multi-DC)
       Remote workstation : Should work on all OS which can support Python. Tested on my Debian with Python 2.7.x and 3.9 (regular testing)

# HAProxy upgrade recommendations
Before upgrading, on the HAProxy server, you should have a copy of the config file : /etc/haproxy/haproxy.cfg
It's recommended to take a snapshot of the VM if HAProxy is based on a virtual machine     


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
      -f FOLDER, --folder FOLDER
                            indicate the folder including all config files,
                            default = local folder
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
       haproxy_template.cfg FOUND - OK
       We are considering the following path as the current path for the cloudian installation : /opt/cloudian-staging/7.4/
       
       /opt/cloudian-staging/7.4/survey.csv FOUND - OK
       /opt/cloudian-staging/7.4/CloudianInstallConfiguration.txt FOUND - OK
       /etc/cloudian-7.4-puppet/manifests/extdata/common.csv FOUND - OK
       
       HyperStore release detected : 7.4
       
       Proxy Protocol ENABLED - the HAProxy config will reflect that
       
       
       Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
       
       You need to have the root access to push this config.
       Do you want to push & run this config file to your haproxy server ? (yes / no) : yes
       Please, enter the IP address or the hostname of your haproxy server : 192.168.110.200
       Enter the root password for the connexion ...
       Password:
       Trying to connect to the host : 192.168.110.200 with the root password ... and then checking some parameters for you ...
       HAProxy version 2.4.4-1 2021/09/08 - https://haproxy.org/
       Enabling the haproxy service on the haproxy server...
       Synchronizing state of haproxy.service with SysV service script with /lib/systemd/systemd-sysv-install.
       Executing: /lib/systemd/systemd-sysv-install enable haproxy
       Backing up the old config on the haproxy server...
       Copying config file to haproxy server...
       Restarting haproxy service on the haproxy server...
       Checking status of haproxy service...
       ● haproxy.service - HAProxy Load Balancer
       Loaded: loaded (/lib/systemd/system/haproxy.service; enabled; vendor preset: enabled)
       Active: active (running) since Fri 2022-04-08 11:04:46 CEST; 517ms ago
       Docs: man:haproxy(1)
       file:/usr/share/doc/haproxy/configuration.txt.gz
       Process: 621 ExecStartPre=/usr/sbin/haproxy -f $CONFIG -c -q $EXTRAOPTS (code=exited, status=0/SUCCESS)
       Main PID: 623 (haproxy)
       Tasks: 5 (limit: 2342)
       Memory: 71.8M
       CGroup: /system.slice/haproxy.service
       ├─623 /usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -S /run/haproxy-master.sock
       └─625 /usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -S /run/haproxy-master.sock
       
       Apr 08 11:04:46 cloudlab-haproxy-debian systemd[1]: Starting HAProxy Load Balancer...
       Apr 08 11:04:46 cloudlab-haproxy-debian haproxy[623]: [NOTICE]   (623) : New worker #1 (625) forked
       Apr 08 11:04:46 cloudlab-haproxy-debian systemd[1]: Started HAProxy Load Balancer.


**Those lines are suggested as quick examples without config push**

For example, the tool is uploaded to /root directory on the puppet master and we run it from here without any parameters.

Quick example on 7.1.x HS release (IAM service not available) :

       [root@cloudlab01 ~]# python haproxy_config.py
       haproxy_template.cfg found - OK
       We are considering the following path as the current path for the cloudian installation : /root/CloudianPackages/
       /root/CloudianPackages/survey.csv found - OK
       /root/CloudianPackages/CloudianInstallConfiguration.txt found - OK
       /etc/cloudian-7.1.7-puppet/manifests/extdata/common.csv found - OK
       *** IAM Endpoint not found. Looks like it is an older version : HS 7.0.x or 7.1.x ***
       We prepare your HAProxy config file to use IAM with a temporary iam domain instead like : iam.not-yet-configured
       In the future, replace the iam.not-yet-configured with your IAM EndPoint value.
       Please, comment the IAM lines (with a #) in the config file if you don't want to see the warning lines in the STATs page
       
       Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
       
       You need to have the root access to push this config.
       Do you want to push & run this config file to your haproxy server ? (yes / no) : no
       
       You have to :
       Enable the haproxy service on the haproxy server via systemctl command
       next, copy the file haproxy.cfg to the haproxy server (into /etc/haproxy/)
       Then restart the haproxy service on the haproxy server.
       Have a good day !

Quick example on 7.2.x HS release (from 7.1.x upgrade - IAM service up but based on AdminAPI service) :

       [root@cloudlab01 ~]# python haproxy_config.py
       haproxy_template.cfg found - OK
       We are considering the following path as the current path for the cloudian installation : /opt/cloudian-staging/7.2.3/
       
       /opt/cloudian-staging/7.2.3/survey.csv found - OK
       /opt/cloudian-staging/7.2.3/CloudianInstallConfiguration.txt found - OK
       /etc/cloudian-7.2.3-puppet/manifests/extdata/common.csv found - OK
       
       *** Warning, your IAM Endpoint has the same value compared to the AdminAPI Endpoint ***
       IAM Endpoint = s3-admin-one.demo.lab
       API EndPoint = s3-admin-one.demo.lab
       This might not work well.
       Please, adjust accordingly or comment (with a #) the IAM lines in the HAProxy config file.
       
       Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
       
       You need to have the root access to push this config.
       Do you want to push & run this config file to your haproxy server ? (yes / no) : no
       
       You have to :
       Enable the haproxy service on the haproxy server via systemctl command
       next, copy the file haproxy.cfg to the haproxy server (into /etc/haproxy/)
       Then restart the haproxy service on the haproxy server.
       Have a good day !

Quick example on 7.2.x HS release :

       [root@cloudlab01 ~]# python haproxy_config.py
       haproxy_template.cfg found - OK
       We are considering the following path as the current path for the cloudian installation : /opt/cloudian-staging/7.2.4/
       
       /opt/cloudian-staging/7.2.4/survey.csv found - OK
       /opt/cloudian-staging/7.2.4/CloudianInstallConfiguration.txt found - OK
       /etc/cloudian-7.2.4-puppet/manifests/extdata/common.csv found - OK
       
       Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
       
       You need to have the root access to push this config.
       Do you want to push & run this config file to your haproxy server ? (yes / no) : no
       
       You have to :
       Enable the haproxy service on the haproxy server via systemctl command
       next, copy the file haproxy.cfg to the haproxy server (into /etc/haproxy/)
       Then restart the haproxy service on the haproxy server.
       Have a good day !

**or use the options to specify the files required (remote workstation in this example) :**

Specifying all files in the command line :

       plong@snoopy:~$ python haproxy_config.py -s ./config_7.2.2_three_nodes/survey.csv -i ./config_7.2.2_three_nodes/CloudianInstallConfiguration.txt -c ./config_7.2.2_three_nodes/common.csv
       haproxy_template.cfg found - OK
       We are considering this host is NOT the Cloudian puppet master
       
       ./config_7.2.2_three_nodes/survey.csv found - OK
       ./config_7.2.2_three_nodes/CloudianInstallConfiguration.txt found - OK
       ./config_7.2.2_three_nodes/common.csv found - OK
       
       Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
       
       You need to have the root access to push this config.
       Do you want to push & run this config file to your haproxy server ? (yes / no) : no
       
       You have to :
       Enable the haproxy service on the haproxy server via systemctl command
       next, copy the file haproxy.cfg to the haproxy server (into /etc/haproxy/)
       Then restart the haproxy service on the haproxy server.
       Have a good day !

or using the new option "--folder" : 

       ** 7.2.4 example **
       $ python haproxy_config.py --folder ./config_7.2.4_six_nodes/
       haproxy_template.cfg FOUND - OK
       We are considering this host is NOT the Cloudian puppet master
       
       Trying to find all the config files needed in : ./config_7.2.4_six_nodes//
       ./config_7.2.4_six_nodes//survey.csv FOUND - OK
       ./config_7.2.4_six_nodes//CloudianInstallConfiguration.txt FOUND - OK
       ./config_7.2.4_six_nodes//common.csv FOUND - OK
       
       HyperStore release detected : 7.2.4
       Notice : using legacy layer 4 HealthCheck for IAM Service based on the HS version detected.
       
       Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
       
       You need to have the root access to push this config.
       Do you want to push & run this config file to your haproxy server ? (yes / no) : no
       
       You have to :
       Enable the haproxy service on the haproxy server via systemctl command
       next, copy the file haproxy.cfg to the haproxy server (into /etc/haproxy/)
       Then restart the haproxy service on the haproxy server.
       Have a good day !


       ** 7.3.2 example **
       $ python haproxy_config.py --folder ./config_7.3.2_two_nodes
       haproxy_template.cfg FOUND - OK
       We are considering this host is NOT the Cloudian puppet master
       
       Trying to find all the config files needed in : ./config_7.3.2_two_nodes/
       ./config_7.3.2_two_nodes/survey.csv FOUND - OK
       ./config_7.3.2_two_nodes/CloudianInstallConfiguration.txt FOUND - OK
       ./config_7.3.2_two_nodes/common.csv FOUND - OK
       
       HyperStore release detected : 7.3.2
       
       Proxy Protocol ENABLED - the HAProxy config will reflect that
       
       Notice : using legacy layer 4 HealthCheck for IAM Service based on the HS version detected.
       
       Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
       
       You need to have the root access to push this config.
       Do you want to push & run this config file to your haproxy server ? (yes / no) : no
       
       You have to :
       Enable the haproxy service on the haproxy server via systemctl command
       next, copy the file haproxy.cfg to the haproxy server (into /etc/haproxy/)
       Then restart the haproxy service on the haproxy server.
       Have a good day !


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
       haproxy_template.cfg found - OK
       We are considering the following path as the current path for the cloudian installation : /opt/cloudian-staging/7.2.4/
       
       /opt/cloudian-staging/7.2.4/survey.csv found - OK
       /opt/cloudian-staging/7.2.4/CloudianInstallConfiguration.txt found - OK
       /etc/cloudian-7.2.4-puppet/manifests/extdata/common.csv found - OK
       
       Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
       
       You need to have the root access to push this config.
       Do you want to push & run this config file to your haproxy server ? (yes / no) : no
       
       You have to :
       Enable the haproxy service on the haproxy server via systemctl command
       next, copy the file haproxy.cfg to the haproxy server (into /etc/haproxy/)
       Then restart the haproxy service on the haproxy server.
       Have a good day !

This option is useful if the datacenter dc01 is the main datacenter where all the infrastructure is present.
The datacenter dc02 has Cloudian nodes with a limited infrastructure.
You would like to limit the bandwidth usage between the datacenters.
(avoid : sending a s3 request to dc02 although all your s3 clients are based on dc01 except if dc01's nodes are down)


**If you want to enable the mail parameters and send some alerts in case of a node or a service down, follow this :**
The email is sent only when the service/server becomes unreachable (no email sent when the service/server comes up)
(notice : again, I answered 'no' to the question "push & run" but you can answer 'yes')

       [root@cloudlab01 ~]# python haproxy_config.py -ms smtp.demo.lab -mf haproxy@demo.lab -mt adminsys@demo.lab
       haproxy_template.cfg found - OK
       We are considering the following path as the current path for the cloudian installation : /opt/cloudian-staging/7.2.4/
       
       /opt/cloudian-staging/7.2.4/survey.csv found - OK
       /opt/cloudian-staging/7.2.4/CloudianInstallConfiguration.txt found - OK
       /etc/cloudian-7.2.4-puppet/manifests/extdata/common.csv found - OK
       
       Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
       
       You need to have the root access to push this config.
       Do you want to push & run this config file to your haproxy server ? (yes / no) : no
       
       You have to :
       Enable the haproxy service on the haproxy server via systemctl command
       next, copy the file haproxy.cfg to the haproxy server (into /etc/haproxy/)
       Then restart the haproxy service on the haproxy server.
       Have a good day !

Notice : During maintenance operations like reboots of nodes, your email server might deal with several emails (one per service down).


**If you have answered 'no' and you don't want to push automatically the haproxy config file into the HAProxy host**

Just grab the haproxy.cfg file created in the local directory and send it to the haproxy server (aka the load-balancer host)

you might want to backup the previous configuration of HAProxy on your HAProxy server. So, do it before please.

	[root@cloudlab01 ~]# ls
    haproxy.cfg  haproxy_config.py  haproxy_template.cfg
	
	[root@cloudlab01 ~]# scp haproxy.cfg root@haproxy_server:/etc/haproxy/haproxy.cfg

Go to the HAProxy server by using SSH (or a console), then restart the haproxy service as mentioned.

       # ssh root@haproxy_server
       Linux haproxy 5.10.0-3-amd64 #1 SMP Debian 5.10.13-1 (2021-02-06) x86_64
       root@haproxy:~# systemctl restart haproxy
       root@haproxy:~#
       root@haproxy:~# systemctl status haproxy
       ● haproxy.service - HAProxy Load Balancer
       Loaded: loaded (/lib/systemd/system/haproxy.service; enabled; vendor preset: enabled)
       Active: active (running) since Fri 2021-03-05 13:12:57 CET; 9s ago
       Docs: man:haproxy(1)
       file:/usr/share/doc/haproxy/configuration.txt.gz
       Process: 413 ExecStartPre=/usr/sbin/haproxy -f $CONFIG -c -q $EXTRAOPTS (code=exited, status=0/SUCCESS)
       Main PID: 415 (haproxy)
       Tasks: 2 (limit: 1135)
       Memory: 35.0M
       CGroup: /system.slice/haproxy.service
       ├─415 /usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -S /run/haproxy-master.sock
       └─417 /usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -S /run/haproxy-master.sock
       
       Mar 05 13:12:57 haproxy haproxy[415]: Proxy https.s3-cloudlab.demo.lab started.
       Mar 05 13:12:57 haproxy haproxy[415]: Proxy https.s3-cloudlab.demo.lab started.
       Mar 05 13:12:57 haproxy haproxy[415]: Proxy s3-cloudlab-admin.demo.lab started.
       Mar 05 13:12:57 haproxy haproxy[415]: Proxy s3-cloudlab-admin.demo.lab started.
       Mar 05 13:12:57 haproxy haproxy[415]: Proxy s3-cloudlab-iam.demo.lab started.
       Mar 05 13:12:57 haproxy haproxy[415]: Proxy s3-cloudlab-iam.demo.lab started.
       Mar 05 13:12:57 haproxy haproxy[415]: Proxy https.s3-cloudlab-iam.demo.lab started.
       Mar 05 13:12:57 haproxy haproxy[415]: Proxy https.s3-cloudlab-iam.demo.lab started.
       Mar 05 13:12:57 haproxy haproxy[415]: [NOTICE] 063/131257 (415) : New worker #1 (417) forked
       Mar 05 13:12:57 haproxy systemd[1]: Started HAProxy Load Balancer.

# Version
1.2

# Bugs & Suggestions
Any bugs or suggestions, please contact the author directly.

# Author
Peter Long
