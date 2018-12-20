# HAproxy Build Config
Scripting for build HAProxy config file based on a Cloudian cluster config

# Description
The goal is to build a HAPROXY configuration file (haproxy.cfg) based on the info already in place for the Cloudian cluster.
This is a simple way to avoid misconfiguration for HAProxy config file (typo error, etc.) during installation for PoC and test (SE tool or tool provided to a customer).
This is not a tool which could be used in a production environment as it is a beta version.

# Deployment
Download only the files :

	haproxy_build_config.py
  	haproxy_template.cfg

You need to have also the files (from the Cloudian cluster / Puppet Master) :

	CloudianPackages/survey.csv
  	CloudianPackages/CloudianInstallConfiguration.txt
  

Then, run the script in a directory of your choice (containing those 4 files).

# Tested
Tested on CentOS 7.4, HyperStore 7.0 and 7.1
small clusters : several nodes on 1 DC

# Run
Example :

**those lines can be ignored, this is only for the demonstration**
**I am using directly the CloudianPackages directory on the puppet master in this example**

	root@cloudianone CloudianPackages# ls haproxy*
	haproxy_build_config.py  haproxy_template.cfg

	root@cloudianone CloudianPackages# ls survey.csv 
	survey.csv

	root@cloudianone CloudianPackages# ls CloudianInstallConfiguration.txt 
	CloudianInstallConfiguration.txt


**this is the single line to run**

	root@cloudianone CloudianPackages# python haproxy_build_config.py 
	Done.
	HAProxy config file is : haproxy.cfg
	Please copy the file haproxy.cfg on the haproxy server
	Then reload the config + restart the haproxy service on the haproxy server

**or with config files as parameters - remote workstation**

	plong@snoopy:$ python haproxy_build_config.py survey.csv CloudianInstallConfiguration.txt 
    	Done.
    	HAProxy config file is : haproxy.cfg
    	Please copy the file haproxy.cfg on the haproxy server
    	Then reload the config + restart the haproxy service on the haproxy server

**grab the haproxy.cfg file created and push it to the haproxy server**

	root@cloudianone CloudianPackages# ls haproxy.cfg 
	haproxy.cfg

# Versioning
0.1beta

# Authors
Pit
