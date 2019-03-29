# HAproxy Config
Script to build a HAProxy config file based on a Cloudian cluster config.

# Description
The goal is to build a HAPROXY configuration file (haproxy.cfg) based on the information already in place for the Cloudian cluster.
The result is a config file for a dedicated load-balancer (1 host or 1 VM) to Cloudian cluster.

This is a simple way to avoid misconfiguration for HAProxy config file (typo error, etc.) during installation for PoC and test (SE tool or tool provided to a customer).

# Disclaimer / Warning
Use this tool with precautions (review the config file created manually for a double-check) for your environment : it is not an official tool supported by Cloudian.
Cloudian can NOT be involved for any bugs or misconfiguration due to this tool. So you are using it at your own risks and be aware of the restrictions.

# Deployment
Download only the files :

	haproxy_config.py
  	haproxy_template.cfg

You need to have also the files (from the Cloudian cluster / Puppet Master Host) :
(notice : the "Stagging Directory" is by default : /root/CloudianPackages for the standard deployment excluding any software upgrade).

	<Stagging Directory>/survey.csv
  	<Stagging Directory>/CloudianInstallConfiguration.txt
  
Then, run the script in a directory of your choice (containing those 4 files) or explicitly specify the files mentioned above in the command line with the optional parameters (look at the "Run" Chapter").

# Tested On
Tested on CentOS 7.4, Python 2.7.x, HyperStore 7.0.x and 7.1.x

Tested on HAProxy 1.5.x, 1.6.x and 1.8.x

Cloudian clusters : 3 and more nodes on 1 DC (PoC + clusters running in PROD) and 12 nodes on 2 DCs without any preferences and 6 nodes on 2 DCs with affinity for the first DC (clusters running in PROD).

Remote workstation : Should work on all OS which can support Python. Tested on Debian Stretch/Buster with Python 2.7.x and 3.7.x

# Run & Usage

**Those lines are suggested only for the demonstration**

I am using directly the Stagging Directory : /root/CloudianPackages on the puppet master in this example just after an installation of HyperStore cluster.

First, you should have the files mentioned above (or you can locate them) :

	root@cloudianone CloudianPackages# ls haproxy*
	haproxy_config.py  haproxy_template.cfg

	root@cloudianone CloudianPackages# ls survey.csv 
	survey.csv

	root@cloudianone CloudianPackages# ls CloudianInstallConfiguration.txt 
	CloudianInstallConfiguration.txt

**if you want to have the command usage, just run the script with --help option**

    root@cloudianone CloudianPackages# python haproxy_config.py --help
    usage: haproxy_config.py [-h] [-s SURVEY] [-i INSTALL] [-b BACKUP]

    parameters for the script
    
    optional arguments:
      -h, --help            show this help message and exit
      -s SURVEY, --survey SURVEY
                            indicate the survey file, default = survey.csv
      -i INSTALL, --install INSTALL
                            indicate the installation file, default =
                            CloudianInstallConfiguration.txt
      -bs3 BACKUPS3, --backups3 BACKUP
                            indicate the DC in backup/stand-by mode for s3 protocol (HTTP and HTTPS)

**For only 1 DC, you can run a single line without any option (notice : I am using the stagging directory) :**

	root@cloudianone CloudianPackages# python haproxy_config.py 
	Successful.
    HAProxy config file is : haproxy.cfg
    Please copy the file haproxy.cfg on the haproxy server (into /etc/haproxy/)
    Then restart the haproxy service on the haproxy server via systemctl command

**or use the options, from another directory :**

    [root@cloudianone ~]# python haproxy_config.py -s /root/CloudianPackages/survey.csv -i /root/CloudianPackages/CloudianInstallConfiguration.txt 
    Successful.
    HAProxy config file is : haproxy.cfg
    Please copy the file haproxy.cfg on the haproxy server (into /etc/haproxy/)
    Then restart the haproxy service on the haproxy server via systemctl command

**or use a remote workstation where you put the files required :**

    plong@snoopy:~$ python3.7 haproxy_config.py -s survey.csv -i CloudianInstallConfiguration.txt 
    Successful.
    HAProxy config file is : haproxy.cfg
    Please copy the file haproxy.cfg on the haproxy server (into /etc/haproxy/)
    Then restart the haproxy service on the haproxy server via systemctl command

**For 2 DCs or more without any preferences. So load-balancing will occur on all nodes in the same manner.**

In this case, you can run the command line like you would run it for 1 DC.
All the nodes will be treated as others and the requests will be propagated to all nodes available no matter the location (aka DC).

**For 2 DCs and affinity : choice to have one active and the second passive for s3 service, you must run the command line with the option "--backups3".**

In this example, we have 2 DataCenters : dc1 and dc2. 
The dataCenter "dc1" is the active datacenter for the s3 requests and dc2 is only the passive dataCenter in case of a DC failure.
Based on that choice, all s3 requests will be sent by HAProxy to only the "dc1" nodes in a nominal state else on the "dc2" nodes (in case of a failure of dc1).

    plong@snoopy:~$ python haproxy_config.py -s survey.csv -i CloudianInstallConfiguration.txt -bs3 dc2
    Successful.
    HAProxy config file is : haproxy.cfg
    This configuration include the backup option for the DC : dc2
    Please copy the file haproxy.cfg on the haproxy server (into /etc/haproxy/)
    Then restart the haproxy service on the haproxy server via systemctl command

**In all cases, grab the haproxy.cfg file created in the local directory and send it to the haproxy server (aka the load-balancer host)**

you might want to backup the previous configuration of HAProxy on your HAProxy server. So, do it before please.

	root@cloudianone CloudianPackages# ls haproxy.cfg 
	haproxy.cfg
	
	root@cloudianone CloudianPackages# scp haproxy.cfg root@haproxy_server:/etc/haproxy/haproxy.cfg

# Version
0.4

# Bugs & Suggestions
Any bugs or suggestions, please contact the author directly.

# Author
Peter Long
