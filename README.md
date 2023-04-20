# HAproxy Config
This tool is designed to build a HAProxy config file or HyperBalance configuration based on a Cloudian cluster config.

# Description
The goal is to build a HAPROXY configuration file (haproxy.cfg) or a HyperBalance config based on the information already in place for the Cloudian cluster.
The result is a config file for a dedicated HAProxy load-balancer (1 host or 1 VM) to Cloudian cluster or a full High Availability configuration for HyperBalance loadbalancers. 
Next, you decide to push it (or not) to the load-balancer.

This is a simple way to avoid misconfiguration for HAProxy config file (typo error, etc.) during installation for PoC and test (SE tool or tool provided to a customer) or multi-automated-installation via Vagrant

# Disclaimer / Warning
Use this tool with precautions (review the config file created manually for a double-check) for your environment : it is not an official tool supported by Cloudian.
Cloudian can NOT be involved for any bugs or misconfiguration due to this tool. So you are using it at your own risks and be aware of the restrictions.

# Features
* Compatible with HyperStore **7.4.x and 7.5** (old versions are available for previous HS release)
* **Support of HyperBalance single configuration** (read the How-To for HyperBalance)
* **Support of HyperBalance HA configuration** 
* **Support of multi-regions in the same cluster**
* Optimize the nodes per service for multi-regions accordingly with HyperStore recommendations
* HealthChecks on layer7 (CMC, S3, Admin API, IAM)
* Tuning for HyperBalance LBs
* Automatic discovery of the **staging directory**
* Automatic discovery and config. adjustement for **Proxy Protocol**
* Option : push the HAProxy config. directly to the HAProxy host
* Automatic refresh of the stats page + legends/pop-ups (HTTP code responses from 1xx to 5xx, ipv4 info, balance method, etc)
* Email notification
* Backup DC
* Force **TLS > 1.2**
* **MaxConn** parameter per node

>> **Notice : HyperBalance and LB.org are supported both**

# Tested On

> **Avoid HAProxy < 2.0 due to deprecated parameters and this tool uses now the new parameters
Consider to use HAProxy >= 2.2, prefer the LTS support on 2.2, 2.4 or 2.6 and higher**

Tested on :
* Cloudian nodes : CentOS 7.5-7.9
* HyperStore : 7.4.x & 7.5.x
* Python : 2.7.x - 3.11
* HyperBalance 8.6, 8.7 and 8.8.1

Tested on HAProxy : 2.2 to 2.6 (LTS). Last test on Debian :
	
	HAProxy version 2.6.8-1 2023/01/24 - https://haproxy.org/
       Status: long-term supported branch - will stop receiving fixes around Q2 2027.
       Known bugs: http://www.haproxy.org/bugs/bugs-2.6.8.html
       Running on: Linux 5.10.0-3-amd64 #1 SMP Debian 5.10.13-1 (2021-02-06) x86_64
       Built with multi-threading support (MAX_THREADS=64, default=4).
       Built with OpenSSL version : OpenSSL 3.0.7 1 Nov 2022
       Running on OpenSSL version : OpenSSL 3.0.7 1 Nov 2022
       OpenSSL library supports : TLSv1.0 TLSv1.1 TLSv1.2 TLSv1.3

Cloudian clusters : 

* from 1 to several nodes for PoC or Production environment (tested on 12 nodes cluster/multi-DC)
* from 1 to several regions for PoC (multi-tested on 2 regions)
* Remote workstation : Should work on all OS which can support Python. Tested on my Debian with Python 2.7.x and 3.9 (regular testing)

# HAProxy upgrade recommendations
Before upgrading, on the HAProxy server, you should have a copy of the config file : /etc/haproxy/haproxy.cfg
It's recommended to take a snapshot of the VM if HAProxy is based on a virtual machine     


# Deployment
Download only the files below and put them into a directory of your choice (ex : /root/lb-tools/) :

	haproxy_config.py
	haproxy_config_template.cfg

You need to have also some files (from the Cloudian cluster / Puppet Master Host) if you execute this tool outside of the cloudian cluster :

	<Staging Directory>/survey.csv
	<Staging Directory>/CloudianInstallConfiguration.txt
  	/etc/cloudian-<HS-version>-puppet/manifests/extdata/common.csv

Then, with the new version of the tool, we can discover automatically the Cloudian staging directory if it is on the Puppet Master host.

# Run & Usage

**if you want to have the command usage, just run the script with --help option**

    [root@cloudlab01 lb-tools]# python haproxy_config.py --help
       usage: haproxy_config.py [-h] [-s SURVEY] [-i INSTALL] [-c COMMON] [-f FOLDER]
                                [-hb] [-hbr] [-bs3 BACKUPS3] [-ms MAILSERVER]
                                [-mf MAILFROM] [-mt MAILTO]
       
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
         -hb, --hyperbalance   specify you want to create a HyperBalance
                               configuration
         -hbr, --hbrevert      revert the hyperbalance config applied
         -bs3 BACKUPS3, --backups3 BACKUPS3
                               indicate the DC in backup/stand-by mode for s3,
                               default=none
         -ms MAILSERVER, --mailserver MAILSERVER
                               mail server name or @IP for alerts
         -mf MAILFROM, --mailfrom MAILFROM
                               indicate the sender, default = haproxy@localhost
         -mt MAILTO, --mailto MAILTO
                               indicate the recipient, default = root@localhost

### HAProxy

**Common and standard uses from the Puppet Master Host**
**You can run a single line without any option and push the config on the HAProxy host directly (most standard use for 1 or more DCs) :**

       [root@cloudlab01 lb-tools]# python ./haproxy_config.py
       haproxy_config_template.cfg FOUND - OK
       We are considering the following path as the current path for the cloudian installation : /opt/cloudian-staging/7.4.2/
       
       /opt/cloudian-staging/7.4.2/survey.csv FOUND - OK
       /opt/cloudian-staging/7.4.2/CloudianInstallConfiguration.txt FOUND - OK
       /etc/cloudian-7.4.2-puppet/manifests/extdata/common.csv FOUND - OK
       
       HyperStore release detected : 7.4.2
       
       Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
       
       You need to have the root access to push this config.
       Do you want to push & run this config file to your haproxy server ? (yes / no) : yes
       Please, enter the IP address of your haproxy server : 192.168.110.200
       Enter the root password for the connection ...
       Password:
       Trying to connect to the host : 192.168.110.200 with the root password ... and then checking some parameters for you ...
       processing, please wait...
       Warning: Permanently added '192.168.110.200' (ECDSA) to the list of known hosts.
       HAProxy version 2.4.4-1 2021/09/08 - https://haproxy.org/
       Enabling the haproxy service on the haproxy server...
       processing, please wait...
       Synchronizing state of haproxy.service with SysV service script with /lib/systemd/systemd-sysv-install.
       Executing: /lib/systemd/systemd-sysv-install enable haproxy
       Backing up the old config on the haproxy server...
       processing, please wait...
       Copying config file to haproxy server...
       processing, please wait...
       Restarting haproxy service on the haproxy server...
       processing, please wait...
       Checking status of haproxy service...
       processing, please wait...
       ● haproxy.service - HAProxy Load Balancer
       Loaded: loaded (/lib/systemd/system/haproxy.service; enabled; vendor preset: enabled)
       Active: active (running) since Mon 2022-09-26 10:24:22 CEST; 215ms ago
       Docs: man:haproxy(1)
       file:/usr/share/doc/haproxy/configuration.txt.gz
       Process: 503 ExecStartPre=/usr/sbin/haproxy -f $CONFIG -c -q $EXTRAOPTS (code=exited, status=0/SUCCESS)
       Main PID: 505 (haproxy)
       Tasks: 5 (limit: 2342)
       Memory: 71.7M
       CGroup: /system.slice/haproxy.service
       ├─505 /usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -S /run/haproxy-master.sock
       └─507 /usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -S /run/haproxy-master.sock
       
       Sep 26 10:24:22 cloudlab-haproxy-debian systemd[1]: Starting HAProxy Load Balancer...
       Sep 26 10:24:22 cloudlab-haproxy-debian haproxy[505]: [NOTICE]   (505) : New worker #1 (507) forked
       Sep 26 10:24:22 cloudlab-haproxy-debian systemd[1]: Started HAProxy Load Balancer.
       [root@cloudlab01 lb-tools]#

### HyperBalance 
**Full Example of HyperBalance configuration - single LB**
>>This tool support HyperBalance config from HyperStore 7.4 at the minimum release level.

       [root@cloudlab01]# python ./haproxy_config.py --hyperbalance
       You requested a configuration for a HyperBalance appliance
       
       We are considering the following path as the current path for the cloudian installation : /opt/cloudian-staging/7.4.2/
       
       /opt/cloudian-staging/7.4.2/survey.csv FOUND - OK
       /opt/cloudian-staging/7.4.2/CloudianInstallConfiguration.txt FOUND - OK
       /etc/cloudian-7.4.2-puppet/manifests/extdata/common.csv FOUND - OK
       
       HyperStore release detected : 7.4.2
       You need to have the root access.
       Please, enter the IP address of your HyperBalance appliance : 192.168.110.199
       Enter the root password for the connection ...
       Password:
       Trying to connect to the host : 192.168.110.199 with the root password ... and then checking some parameters for you ...
       processing, please wait...
       OK. HyperBalance is reachable...
       Please enter the IP address for the Secondary (or leave empty) :

       Please, enter the IP address for the VIP (floating IP) : 192.168.110.200
       processing, please wait...
       HyperBalance configuration is applied.

**Full Example of HyperBalance configuration - High Availability Configuration**

       [root@cloudlab01 ~]# python ./haproxy_config.py --hyperbalance
       You requested a configuration for : HyperBalance appliance 
       
       We are considering the following path as the current path for the cloudian installation : /opt/cloudian-staging/7.5.1/
       /opt/cloudian-staging/7.5.1/survey.csv --> FOUND - OK
       /opt/cloudian-staging/7.5.1/CloudianInstallConfiguration.txt --> FOUND - OK
       /etc/cloudian-7.5.1-puppet/manifests/extdata/common.csv --> FOUND - OK

       HyperStore release detected : 7.5.1
       You need to have the root access.
       Please, enter the IP address of your Primary HyperBalance appliance : 192.168.110.199
       Enter the root password for the connection ... 
       Password: *******
       Trying to connect to the host : 192.168.110.199 with the root password ... and then checking some parameters for you ...
       processing, please wait...
       OK. HyperBalance * Primary * is reachable...
       Please enter the IP address for the Secondary (or leave empty) :192.168.110.198
       processing, please wait...
       OK. HyperBalance * Secondary * is reachable...

       Please, enter the IP address for the VIP (floating IP) : 192.168.110.200
       Building the configuration
       processing, please wait...
       Backup Primary config
       processing, please wait...
       Backup Secondary config
       processing, please wait...
       HyperBalance configuration is applied.
       HA configuration in progress
       processing, please wait...
       HA pair created.
       processing, please wait...
       Heartbeat restarted on primary.
       processing, please wait...
       Heartbeat restarted on secondary.
       processing, please wait...
       HA is fully configured.

**Those lines are suggested as quick examples for HAProxy without config push**

For example, the tool is uploaded to /root directory on the puppet master and we run it from here without any parameters.

### HAProxy - Quick example on 7.5 HS release

       [root@cloudlab01 ~]# python haproxy_config.py
       You requested a configuration for : HAProxy

       haproxy_config_template.cfg --> FOUND - OK
       We are considering the following path as the current path for the cloudian installation : /opt/cloudian-staging/7.5/
       /opt/cloudian-staging/7.5/survey.csv --> FOUND - OK
       /opt/cloudian-staging/7.5/CloudianInstallConfiguration.txt --> FOUND - OK
       /etc/cloudian-7.5-puppet/manifests/extdata/common.csv --> FOUND - OK

       HyperStore release detected : 7.5
       
        Your HAProxy config file is : haproxy.cfg and it is in the local/current directory
       
       You need to have the root access to push this config.
       Do you want to push & run this config file to your haproxy server ? (yes / no) : no
       
       You have to :
       Enable the haproxy service on the haproxy server via systemctl command
       next, copy the file haproxy.cfg to the haproxy server (into /etc/haproxy/)
       Then restart the haproxy service on the haproxy server.
       Have a good day !

### HAProxy - Options
**use the options to specify the files required (remote workstation in this example) :**

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

or using the new option "--folder" (remote workstation) : 

       ** 7.4 example **
       $ python haproxy_config.py -f ./config_7.4_six_nodes
       You requested a configuration for : HAProxy
       
       haproxy_config_template.cfg --> FOUND - OK
       We are considering this host is NOT the Cloudian puppet primary 
       
       Trying to find all the config files needed in : ./config_7.4_six_nodes/
       ./config_7.4_six_nodes/survey.csv --> FOUND - OK
       ./config_7.4_six_nodes/CloudianInstallConfiguration.txt --> FOUND - OK
       ./config_7.4_six_nodes/common.csv --> FOUND - OK
       
       HyperStore release detected : 7.4
       
       Proxy Protocol ENABLED - the HAProxy config will reflect that with ports 81 and 4431

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

### HAProxy - 2 DCs with one as a backup DC

**For 2 DCs with a DC as backup : choice to have one active and the second passive for s3 service, you must run the command line with the option "--backups3".**

In this example, we have 2 DataCenters : dc01 and dc02. 
The dataCenter "dc01" is the active datacenter for the s3 requests and dc02 is only the passive dataCenter (backup for s3 => bs3) in case of a DC failure.
Based on that choice, all s3 requests will be sent by HAProxy to only the "dc01" nodes in a nominal state else on the "dc02" nodes (in case of a failure of dc01).
(notice : I answered 'no' to the question "push & run" but you can answer 'yes')

       [root@cloudlab01 ~]# python haproxy_config.py -bs3 dc02
       You requested a configuration for : HAProxy
       
       haproxy_config_template.cfg --> FOUND - OK
       We are considering the following path as the current path for the cloudian installation : /opt/cloudian-staging/7.5/
       /opt/cloudian-staging/7.5/survey.csv --> FOUND - OK
       /opt/cloudian-staging/7.5/CloudianInstallConfiguration.txt --> FOUND - OK
       /etc/cloudian-7.5-puppet/manifests/extdata/common.csv --> FOUND - OK
       
       HyperStore release detected : 7.5
       
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

### HAProxy - Mailing
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

### HAProxy - Manual push

**If you have answered 'no' and you don't want to push automatically the haproxy config file into the HAProxy host**

Just grab the **haproxy.cfg** file created in the local directory and send it to the haproxy server (aka the load-balancer host)

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

### HyperBalance - Revert option

       [root@cloudlab01 ~]# python haproxy_config.py --hbr
       YOU ARE REQUESTING TO REVERT THE CONFIGURATION
       You need to have the root access.
       Please, enter the IP address of your Primary HyperBalance appliance : 192.168.110.199
       Enter the root password for the connection ... 
       Password: 
       Trying to connect to the host : 192.168.110.199 with the root password ... and then checking some parameters for you ...
       processing, please wait...
       OK. HyperBalance * Primary * is reachable...
       Please enter the IP address for the Secondary (or leave empty) :
       Could you confirm the REVERT action please (restart is mandatory) ? (yes / no) : yes
       lb_config_primary.xml --> FOUND - OK
       processing, please wait...
       Primary config restored
       processing, please wait...
       Running restart for the appliance : primary.

# Version
1.4

# Bugs & Suggestions
Any bugs or suggestions, please contact the author directly.

# Author
Peter Long
