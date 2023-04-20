#!/usr/bin/python
#
# haproxy_build_config python script
# TODO :SQS ports (SQS is disabled by default => wait for next HS release)
#        multi-region => multi VIP ?
#        for ubuntu OS for example : use an account different than root + sudo cmd
# tuning : nbproc (avoid), nbthread (auto-tuned), cpu-map (avoid)
#
# Peter Long / v=1.4 / April 2023
# Config. for PROXY Protocol updated if it is enabled on Cloudian
# Compatibility with 7.4 (IAM HTTP/HTTPS layer 7) + 7.5.x
# IAM EndPoint warning if it is still based on AdminAPI Endpoint
# Add --folder command line option to specify a folder instead of all config files needed
# minor changes for stats page (security/default password)
# force TLS 1.2 minimum
# use maxconn per server line instead of global parameter => adjust it if needed
# Add LB.org/HyperBalance automatic configuration (8.6, 8.7 and 8.8.1)
# Tuning for LB.org/HyperBalance : timeout_client & timeout_server for CMC VIP + OPTIONS
# High Availability configuration for LB.org (primary / secondary)
# Support of the Cloudian multi-region deployment
# Look for customized service ports on the cluster
# TO DO : need to configure the iam secure for haproxy ! (hyperbalance= done)
# TO DO :   # The following node was removed on Wed Mar  8 19:57:51 IST 2023
#           # gseblr,dc1-node4,10.3.27.24,dc2,Rack1,ens224
#           ==> comment in the survey.csv file

# I can't use python methods or modules which are not installed on a HyperStore node
import argparse
import getpass
import os
import base64   # compatibility with Python 3.x
import re
from string import Template
import time


# I am using python2 compatible commands (hyperstore uses python2) instead python3 commands.
# force input = raw_input
if hasattr(__builtins__, 'raw_input'):
    input = raw_input


def print_green(text):
    print("\033[92m{}\033[00m" .format(text))


def print_red(text):
    print("\033[91m{}\033[00m" .format(text))


# Send Command by using os.system library and manage the return code - keep compatibility/less intrusive
def send_command(command, text):
    print("processing, please wait...")
    exitcode = os.system(command)
    if exitcode != 0:
        print_red("Error, the status is not ok. We stop the process at this point and let you check manually. Error = " + str(exitcode))
        exit(exitcode)
    elif text:
        print_green(text)


# Push the haproxy config file to the haproxy server by using scp & ssh
# can't use "paramiko" python module as it is not present on the OS deployed on the cloudian appliance
# source : file "haproxy.cfg" standard
def push_config(lb_file):
    print("\n Your HAProxy config file is : " + lb_file + " and it is in the local/current directory\n")
    print("You need to have the root access to push this config.")
    answer = input("Do you want to push & run this config file to your haproxy server ? (yes / no) : ")
    answer = answer.strip().lower()
    if answer.startswith('yes'):
        # Force standard configuration for the SSH (root = avoid permission conflict)
        username = "root"
        hostname = input("Please, enter the IP address of your haproxy server : ")
        control_ip(hostname)
        print_green("Enter the " + username + " password for the connection ... ")
        password = getpass.getpass()
        # Remote actions on the haproxy server
        print_green("Trying to connect to the host : " + hostname + " with the " + username + " password ..." +
              " and then checking some parameters for you ...")
        send_command("sshpass -p" + password + " ssh -o 'StrictHostKeyChecking no' "
                     + username + "@" + hostname + " haproxy -v | grep -i 'version'","")
        print_green("Enabling the haproxy service on the haproxy server...")
        send_command("sshpass -p" + password + " ssh -o 'StrictHostKeyChecking no' "
                     + username + "@" + hostname + " systemctl enable haproxy","")
        print_green("Backing up the old config on the haproxy server...")
        send_command("sshpass -p" + password + " ssh -o 'StrictHostKeyChecking no' "
                  + username + "@" + hostname + " cp /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.orig","")
        print_green("Copying config file to haproxy server...")
        send_command("sshpass -p" + password + " scp -o 'StrictHostKeyChecking no' " + lb_file + " "
                  + username + "@" + hostname + ":/etc/haproxy/haproxy.cfg","")
        print_green("Restarting haproxy service on the haproxy server...")
        send_command("sshpass -p" + password + " ssh -o 'StrictHostKeyChecking no' "
                  + username + "@" + hostname + " systemctl restart haproxy","")
        print_green("Checking status of haproxy service...")
        send_command("sshpass -p" + password + " ssh -o 'StrictHostKeyChecking no' "
                  + username + "@" + hostname + " systemctl status haproxy","")
    elif answer.startswith('no'):
        print_green("\nYou have to :")
        print("Enable the haproxy service on the haproxy server via systemctl command")
        print("next, copy the file " + lb_file + " to the haproxy server (into /etc/haproxy/)")
        print("Then restart the haproxy service on the haproxy server.")
        print_green("Have a good day !")
    else:
        print("Wrong answer. Exiting...")


# Check if a specific file is available
def file_available(filename):
    if not (os.path.isfile(filename)):
        print_red("Error, the file : " + filename + " is missing.")
        print("Check the path and the filename and try again")
        exit(1)
    else:
        print(filename + '\033[92m' + " --> FOUND - OK"  + '\033[00m')


# Check Connectivity for HyperBalance
def check_hb(lb_file, username, password, primary, secondary):
    print("You need to have the root access.")
    username = "root"
    primary = input("Please, enter the IP address of your Primary HyperBalance appliance : ")
    control_ip(primary)
    print_green("Enter the " + username + " password for the connection ... ")
    password = getpass.getpass()
    # Connection test to the LB
    print_green("Trying to connect to the host : " + primary + " with the " + username + " password ..." +
            " and then checking some parameters for you ...")
    send_command("sshpass -p" + password + " ssh -o 'StrictHostKeyChecking no' "
             + username + "@" + primary + " lbcli --action nodestatus >" + lb_file + ".log", "OK. HyperBalance * Primary * is reachable...")
    secondary = input('Please enter the IP address for the Secondary (or leave empty) :')
    if not (secondary == ""):
        control_ip(secondary)
        send_command("sshpass -p" + password + " ssh -o 'StrictHostKeyChecking no' "
                 + username + "@" + secondary + " lbcli --action nodestatus >>" + lb_file + ".log", "OK. HyperBalance * Secondary * is reachable...")
    return username, password, primary, secondary


# Revert the HyperBalance configuration applied to the appliance
def revert_hb_config(lb_file, username, password, primary, secondary):
    answer = input("Could you confirm the REVERT action please (restart is mandatory) ? (yes / no) : ")
    answer = answer.strip().lower()
    if answer.startswith('yes'):
        # Do revert for primary
        file_available("lb_config_primary.xml")
        send_command("sshpass -p" + password + " scp -o 'StrictHostKeyChecking no' lb_config_primary.xml "
                     + username + "@" + primary + ":/etc/loadbalancer.org/lb_config.xml", "Primary config restored")
        # Do same for secondary if exists
        if not (secondary == ""):
            file_available("lb_config_secondary.xml")
            send_command("sshpass -p" + password + " scp -o 'StrictHostKeyChecking no' lb_config_secondary.xml "
                + username + "@" + secondary + ":/etc/loadbalancer.org/lb_config.xml", "Secondary config restored")
            print_green("--> Pair broken, restart needed ...")
            send_command("sshpass -p" + password + " ssh -T -q -o 'StrictHostKeyChecking no' "
                + username + "@" + primary + " lbcli --action power --function restart"
                + " >>" + lb_file + ".log", "Running restart for the appliance : secondary.")
        # Finish job for primary
        send_command("sshpass -p" + password + " ssh -T -q -o 'StrictHostKeyChecking no' "
            + username + "@" + primary + " lbcli --action power --function restart"
            + " >>" + lb_file + ".log", "Running restart for the appliance : primary.")
        # Checking logs for warnings or errors
        check_hb_log(lb_file)
        exit (0)
    else:
        print_red("** revert action canceled **")
        exit(0)


# Check the HyperBalance logs for fatal or failed messages
def check_hb_log(lb_file):
    # Checking logs for warnings or errors
    with open(lb_file + ".log", "r") as filein:
        # status:failed or status:fatal
        if '"status":"fa' in filein.read():
            print_red("you must check the logfile : " + lb_file + ".log" + " there are some errors.")
    filein.close()


# Check the IP format
def control_ip(ip_addr):
    is_ok = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", ip_addr)
    if bool(is_ok) is False:
        print_red("Error, the IP address provided : " + ip_addr + " is not in a valid format like : 192.168.1.2")
        exit(1)
    for ip_digit in ip_addr.split("."):
        digit = int(ip_digit)
        if digit < 0 or digit > 255:
            print_red("Error, the IP address provided : " + ip_addr + " is not in a valid byte range.")
            exit(1)


# Backup the HyperBalance configuration
def backup_hyperbalance(username, password, primary, secondary):
    send_command("sshpass -p" + password + " scp -o 'StrictHostKeyChecking no' " + username + "@" + primary + ":/etc/loadbalancer.org/lb_config.xml lb_config_primary.xml", "Backup Primary config")
    if not (secondary == ""):
        send_command("sshpass -p" + password + " scp -o 'StrictHostKeyChecking no' " + username + "@" + secondary + ":/etc/loadbalancer.org/lb_config.xml lb_config_secondary.xml", "Backup Secondary config")


# For Debug perf.
def whattimeisit():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print("## for DEBUG, current time is : " + current_time)


def main():
    # CONSTANT
    # to build the list of nodes for each TCP service - don't want to have a parameter file
    HEADER = "    server "
    CMC_HTTPS_PARAMETERS = "check check-ssl verify none inter 5s rise 1 fall 2 slowstart 5000 maxconn 200"
    S3_HTTP_PARAMETERS = "check inter 5s rise 1 fall 2 slowstart 5000 maxconn 200"
    S3_HTTPS_PARAMETERS = "check check-ssl verify none inter 5s rise 1 fall 2 slowstart 5000 maxconn 200"
    ADMIN_HTTPS_PARAMETERS = "check check-ssl verify none inter 5s rise 1 fall 2 slowstart 5000 maxconn 200"
    IAM_HTTP_PARAMETERS = "check inter 5s rise 1 fall 2 slowstart 5000 maxconn 200"
    IAM_HTTPS_PARAMETERS = "check check-ssl verify none inter 5s rise 1 fall 2 slowstart 5000 maxconn 200"
    # HyperBalance
    HEADER_HB_VIP = "--action add-vip --layer 7 --vip "
    HEADER_HB_RIP = " --action add-rip --vip "
    CMC_HTTPS_HB_PARAMETERS = "--mode tcp --persistence ip --check_type negotiate_https_options --check_request '/Cloudian/login.htm' --timeout on --timeout_client 180000 --timeout_server 181000"
    S3_HTTP_HB_PARAMETERS = "--mode tcp --persistence none --check_type negotiate_http_head --check_request '/.healthCheck'"
    S3_HTTPS_HB_PARAMETERS = "--mode tcp --persistence none --check_type negotiate_https_head --check_request '/.healthCheck'"
    ADMIN_HTTPS_HB_PARAMETERS = "--mode tcp --persistence none --check_type negotiate_https_head --check_request '/.healthCheck'"
    IAM_HTTP_HB_PARAMETERS = "--mode tcp --persistence none --check_type negotiate_http_head --check_request '/.healthCheck'"
    IAM_HTTPS_HB_PARAMETERS = "--mode tcp --persistence none --check_type negotiate_https_head --check_request '/.healthCheck'"
    HB_TUNING_PARAMETERS = " --weight 100 --maxconns 200"
    # for options in the command line
    DEFAULT_BACKUP = "nobackupatall"
    DEFAULT_MAILSERVER = "nomailserver"

    # VARIABLES
    survey_file = "survey.csv"
    install_config_file = "CloudianInstallConfiguration.txt"
    servicemap_file = "/opt/cloudian/conf/cloudianservicemap.json"
    common_file = "common.csv"
    common_extra_path = "/manifests/extdata/"
    install_path = "/root/CloudianPackages"     # old fashion
    template_file = "haproxy_config_template.cfg"
    lb_file = "haproxy.cfg"
    hyperstore_version = "0"    # 0 means no version
    # Force empty value or default
    cmc_endpoint = ""
    cmc_https_list = []
    cmc_port = 8443
    s3_endpoint = ""
    s3_http_list = []
    s3_https_list = []
    s3_http_port = 80
    s3_https_port = 443
    admin_endpoint = ""
    admin_https_list = []
    admin_port = 19443
    iam_endpoint = ""
    iam_http_list = []
    iam_https_list = []
    iam_http_port = 16080
    iam_https_port = 16443
    iam_only_https = False
    config_path = ""
    #    backup_parameter = ""
    use_backup_option = False
    mailserver = []
    mail_list = []
    dc_exist = False
    hyperbalance = False

    # Test arguments from command line
    # Define VARIABLE : install_config_file and survey_file in any case
    parser = argparse.ArgumentParser(description='parameters for the script')
    parser.add_argument('-s', '--survey',
                        help="indicate the survey file, default = survey.csv",
                        default=survey_file)
    parser.add_argument('-i', '--install',
                        help="indicate the installation file, default = CloudianInstallConfiguration.txt",
                        default=install_config_file)
    parser.add_argument('-c', '--common',
                        help="indicate the common.csv file, default = common.csv",
                        default=common_file)
    parser.add_argument('-f', '--folder',
                        help="indicate the folder including all config files, default = local folder",
                        default=config_path)
    parser.add_argument('-hb', '--hyperbalance',
                        help="specify you want to create a HyperBalance configuration",
                        action="store_true",
                        default=hyperbalance)
    parser.add_argument('-hbr', '--hbrevert',
                        help="revert the hyperbalance config applied",
                        action="store_true")
    parser.add_argument('-bs3', '--backups3',
                        help="indicate the DC in backup/stand-by mode for s3, default=none",
                        default=DEFAULT_BACKUP)
    parser.add_argument('-ms', '--mailserver',
                        help="mail server name or @IP for alerts",
                        default=DEFAULT_MAILSERVER)
    parser.add_argument('-mf', '--mailfrom',
                        help="indicate the sender, default = haproxy@localhost",
                        default='haproxy@localhost')
    parser.add_argument('-mt', '--mailto',
                        help="indicate the recipient, default = root@localhost",
                        default='root@localhost')
    args = parser.parse_args()

    hyperbalance = args.hyperbalance
    # In case of a HyperBalance config or haproxy, we need to do more steps
    if hyperbalance:
        print("You requested a configuration for : " + '\033[92m' + "HyperBalance appliance\n" + '\033[00m')
        lb_file = "hb-config"
    elif args.hbrevert:
        lb_file = "hb-config"
        print_red("YOU ARE REQUESTING TO REVERT THE CONFIGURATION")
        username, password, primary, secondary = check_hb(lb_file, "root", password="", primary="", secondary="")
        revert_hb_config(lb_file, username, password, primary, secondary)
    else:
        print("You requested a configuration for : " + '\033[92m' + "HAProxy\n" + '\033[00m')
        # Define if we are using the "backup" parameter
        if args.backups3 != DEFAULT_BACKUP:
            use_backup_option = True
        # Define if we are using the "mail" parameters and create the config
        if args.mailserver != DEFAULT_MAILSERVER:
            mailserver.append("mailers mailservers")
            mailserver.append("    mailer smtp1 " + args.mailserver + ":25")
            mail_list.append("    email-alert mailers mailservers")
            mail_list.append("    email-alert from " + args.mailfrom)
            mail_list.append("    email-alert to " + args.mailto)
            mail_list.append("    email-alert level alert")
        else:
            mailserver.append("#no mail configuration")
            mail_list.append("    #no mail configuration")
        # 1st - Check if the haproxy_config_template.cfg exists
        file_available(template_file)

    # Automatic discovery of the information needed (survey + CloudianInstallConfiguration + common.csv)
    # By-pass parameters indicated in the command-line if we are on the cloudian puppet host
    if os.path.isfile(servicemap_file):
        with open(servicemap_file, "r") as filein:
            for line in filein:
                if "cloudianInstall.sh" in line:
                    install_path = line.strip().split(':')[4].split(',')[0].split('\"')[1].split('cloudianInstall.sh')[0]
                    print("We are considering the following path as the current path for the cloudian installation : " + '\033[92m' + install_path + '\033[00m')
                    survey_file = install_path + survey_file
                    install_config_file = install_path + install_config_file
                if "configdir" in line:
                    common_path = line.strip().split(':')[3].split(',')[0].split('\"')[1]
                    common_file = common_path + common_extra_path + common_file
                    # common file will be checked later ... file_available(common_file)
    else:
        print_red("We are considering this host is NOT the Cloudian puppet primary \n")
        # if there is no servicemap file, then the script will keep the defaults or options
        # looking for the config files in the folder specified if there is...
        if args.folder != "":
            print("Trying to find all the config files needed in : " + args.folder +"/")
            # force '/' at the end of the path
            survey_file = args.folder + "/" + args.survey
            install_config_file = args.folder + "/" + args.install
            common_file = args.folder + "/" + args.common
        else:
            survey_file = args.survey
            install_config_file = args.install
            common_file = args.common

    # 2nd - Check if the three required files exist on the host
    file_available(survey_file)
    file_available(install_config_file)
    file_available(common_file)

    # Check if we have to use the Proxy_Protocol for S3
    # Retrieve the HyperStore version too
    # source : file "common.csv"
    with open(common_file, "r") as filein:
        for line in filein:
            if "release_version," in line:
                hyperstore_version = line.strip().split(',')[1]
                print_green("\nHyperStore release detected : " + hyperstore_version)
            if "cmc_https_port," in line:
                cmc_port = line.strip().split(',')[1]
            if "cmc_admin_secure_port," in line:
                admin_port = line.strip().split(',')[1]
            if "cloudian_s3_port," in line:
                s3_http_port = line.strip().split(',')[1]
            if "cloudian_s3_ssl_port," in line:
                s3_https_port = line.strip().split(',')[1]
            if "iam_port," in line:
                iam_http_port = line.strip().split(',')[1]
            if "iam_secure_port," in line:
                iam_https_port = line.strip().split(',')[1]
            if "iam_secure,true" in line:
                print_green("\nIAM secure DETECTED - the config will use only IAM HTTPS EndPoint\n")
                iam_only_https = True
            if "s3_proxy_protocol_enabled,true" in line:
                print_green("\nProxy Protocol ENABLED - the HAProxy config will reflect that with ports 81 and 4431\n")
                S3_HTTP_PARAMETERS = S3_HTTP_PARAMETERS.replace(":80 check", ":81 check send-proxy")
                S3_HTTPS_PARAMETERS = S3_HTTPS_PARAMETERS.replace(":443 check", ":4431 check send-proxy")

    # Check the HyperStore version for compatibility reason and layer 7 healthcheck
    # HS < 7.4 is no more supported by this tool
    if int(hyperstore_version.split('.')[0]) == 7:
        if int(hyperstore_version.split('.')[1]) < 4:
            print_red("Error, we recommend to use HyperStore : 7.4.x at the minimum level."
                      "\nThis tool supports only HyperStore 7.4.x or upper")
            exit(1)
    else:
        print_red("Error, we support only HyperStore version 7.x at the moment")
        print("Contact the author of the tool")
        exit(1)

    # Retrieve Endpoint information (default region, s3 domain, admin domain, cmc domain, iam domain)
    # source : file "CloudianInstallConfiguration.txt"
    with open(install_config_file, "r") as filein:
        for line in filein:
            if "cloudian_cluster_regionname_region1=" in line:
                default_region = line.strip().split('=')[1]
            if "cloudian_s3_domain_region1=" in line:
                s3_endpoint = line.strip().split('=')[1]
            elif "cloudian_admin_host=" in line:
                admin_endpoint = line.strip().split('=')[1]
            elif "cloudian_cmc_domain=" in line:
                cmc_endpoint = line.strip().split('=')[1]
            elif "cloudian_iam_host=" in line:
                iam_endpoint = line.strip().split('=')[1]
    filein.close()

    # Test if IAM domain is present or if there is an issue with admin EndPoint (not the case for 7.0 or 7.1 config files/back compatibility)
    # will be removed later
    if not iam_endpoint:
        print_red("\n Error, IAM Endpoint not found. Looks like it is an old version. ")
        exit(1)
    elif iam_endpoint == admin_endpoint:
        print_red("\n *** Warning, your IAM Endpoint has the same value compared to the AdminAPI Endpoint ***")
        print("IAM Endpoint = ") + iam_endpoint
        print("API EndPoint = ") + admin_endpoint
        print("This might not work well.")
        print("Please, adjust accordingly or comment (with a #) the IAM lines in the HAProxy config file.")

    # Retrieve list of nodes + IPs and build lists for each TCP service
    # source : file "survey.csv"
    with open(survey_file, "r") as filein:
        line = filein.readline()
        while line != "":
            listing = line.split(",")
            if listing[3] == args.backups3:
                backup_parameter = "backup"
                dc_exist = True
            else:
                backup_parameter = ""
            if not hyperbalance:
                cmc_https_list.append(HEADER + listing[1] + " " + listing[2] + ":" + cmc_port + " " + CMC_HTTPS_PARAMETERS)
                s3_http_list.append(HEADER + listing[1] + " " + listing[2] + ":" + s3_http_port + " " + S3_HTTP_PARAMETERS + " " + backup_parameter)
                s3_https_list.append(HEADER + listing[1] + " " + listing[2] + ":" + s3_https_port + " " + S3_HTTPS_PARAMETERS + " " + backup_parameter)
                if (listing[0] == default_region ):
                    admin_https_list.append(HEADER + listing[1] + " " + listing[2] + ":" + admin_port + " " +ADMIN_HTTPS_PARAMETERS)
                    iam_http_list.append(HEADER + listing[1] + " " + listing[2] + ":" + iam_http_port + " " + IAM_HTTP_PARAMETERS + " " + backup_parameter)
                    iam_https_list.append(HEADER + listing[1] + " " + listing[2] + ":" + iam_https_port + " " + IAM_HTTPS_PARAMETERS + " " + backup_parameter)
            else:
                cmc_https_list.append(HEADER_HB_RIP + cmc_endpoint + " --rip " + listing[1] + " --ip " + listing[2] + " --port " + cmc_port + " " + HB_TUNING_PARAMETERS)
                s3_http_list.append(HEADER_HB_RIP + s3_endpoint + "_HTTP" + " --rip " + listing[1] + " --ip " + listing[2] + " --port " + s3_http_port + " " + HB_TUNING_PARAMETERS)
                s3_https_list.append(HEADER_HB_RIP + s3_endpoint + "_HTTPS" + " --rip " + listing[1] + " --ip " + listing[2] + " --port " + s3_https_port + " " + HB_TUNING_PARAMETERS)
                if (listing[0] == default_region ):
                    admin_https_list.append(HEADER_HB_RIP + admin_endpoint + " --rip " + listing[1] + " --ip " + listing[2] + " --port " + admin_port + " " + HB_TUNING_PARAMETERS)
                    if not iam_only_https:
                        iam_http_list.append(HEADER_HB_RIP + iam_endpoint + "_HTTP" + " --rip " + listing[1] + " --ip " + listing[2] + " --port " + iam_http_port + " " + HB_TUNING_PARAMETERS)
                    iam_https_list.append(HEADER_HB_RIP + iam_endpoint + "_HTTPS" + " --rip " + listing[1] + " --ip " + listing[2] + " --port " + iam_https_port + " " + HB_TUNING_PARAMETERS)
            line = filein.readline()
    if (not dc_exist) and use_backup_option:
        print("Error, the expected DC : " + args.backups3 + " is not valid")
        print("This DC name : " + args.backups3 + " is not in the survey file : " + survey_file)
        print("Check the DC name or the survey file and try again")
        exit(1)

    if not hyperbalance:
        # Create the HA proxy config file
        # destination : lb_file based on the template "haproxy_template.cfg"
        with open(template_file, "r") as filein:
            # Read template file
            src = Template(filein.read())
            d = {'mailserver_line': '\n'.join(mailserver), 'cmc_endpoint': cmc_endpoint, 's3_endpoint': s3_endpoint,
                 'admin_endpoint': admin_endpoint, 'iam_endpoint': iam_endpoint,
                 'cmc_https_list': '\n'.join(cmc_https_list),
                 's3_http_list': '\n'.join(s3_http_list), 's3_https_list': '\n'.join(s3_https_list),
                 'admin_https_list': '\n'.join(admin_https_list), 'mail_list': ''.join(mail_list),
                 'iam_http_list': '\n'.join(iam_http_list), 'iam_https_list': '\n'.join(iam_https_list)}
            # Substitution in the template --> result
            result = src.substitute(d)
            # Write result into haproxy file
            fileout = open(lb_file, "w")
            fileout.write(result)
            fileout.close()
            # Push the configuration file to the haproxy server
            # Prompt : yes or no + password
            push_config(lb_file)
    else:
        # Create HyperBalance config file
        # destination : lb_file
        username, password, primary, secondary = check_hb(lb_file, "root", password="", primary="", secondary="")
        vip = input("\nPlease, enter the IP address for the VIP (floating IP) : ")
        control_ip(vip)
        print_green("Building the configuration")
        result = [HEADER_HB_VIP + cmc_endpoint + " --ip " + vip + " --ports " + cmc_port + " " + CMC_HTTPS_HB_PARAMETERS]
        result.extend(cmc_https_list)
        result.append([HEADER_HB_VIP + s3_endpoint + "_HTTP" + " --ip " + vip + " --ports " + s3_http_port + " " + S3_HTTP_HB_PARAMETERS])
        result.extend(s3_http_list)
        result.append([HEADER_HB_VIP + s3_endpoint + "_HTTPS" + " --ip " + vip + " --ports " + s3_https_port + " " + S3_HTTPS_HB_PARAMETERS])
        result.extend(s3_https_list)
        result.append([HEADER_HB_VIP + admin_endpoint + " --ip " + vip + " --ports " + admin_port + " " + ADMIN_HTTPS_HB_PARAMETERS])
        result.extend(admin_https_list)
        if not(iam_only_https):
            result.append([HEADER_HB_VIP + iam_endpoint + "_HTTP" + " --ip " + vip + " --ports " + iam_http_port + " " + IAM_HTTP_HB_PARAMETERS])
            result.extend(iam_http_list)
        result.append([HEADER_HB_VIP +  iam_endpoint + "_HTTPS" + " --ip " + vip + " --ports " + iam_https_port + " " + IAM_HTTPS_HB_PARAMETERS])
        result.extend(iam_https_list)
        result.append("--action restart-haproxy")
        with open(lb_file + "-add.cmd", "w") as fileout:
            for line in result:
                fileout.write("\nlbcli " + "".join(line))
            fileout.close()
        # Backup
        backup_hyperbalance(username,password,primary,secondary)
        # Remote actions on the hyperbalance appliance - Apply config on the primary
        send_command("sshpass -p" + password + " ssh -T -q -o 'StrictHostKeyChecking no' "
                + username + "@" + primary + " <./" + lb_file + "-add.cmd >>" + lb_file + ".log", "HyperBalance configuration is applied.")
        # Checking logs for warnings or errors
        check_hb_log(lb_file)

        if not (secondary == ""):
            print_green("HA configuration in progress")
            send_command("sshpass -p" + password + " ssh -T -q -o 'StrictHostKeyChecking no' "
                         + username + "@" + primary + " lbcli --action ha_create --local_ip " + primary
                         + " --peer_ip " + secondary + " --peer_password " + password
                         + " >>" + lb_file + ".log", "HA pair created.")
            send_command("sshpass -p" + password + " ssh -T -q -o 'StrictHostKeyChecking no' "
                         + username + "@" + primary + " lbcli --action restart-heartbeat"
                         + " >>" + lb_file + ".log", "Heartbeat restarted on primary.")
            send_command("sshpass -p" + password + " ssh -T -q -o 'StrictHostKeyChecking no' "
                         + username + "@" + secondary + " lbcli --action restart-heartbeat"
                         + " >>" + lb_file + ".log", "Heartbeat restarted on secondary.")
            send_command("sshpass -p" + password + " ssh -T -q -o 'StrictHostKeyChecking no' "
                         + username + "@" + primary + " lbcli --action restart-haproxy"
                         + " >>" + lb_file + ".log", "HA is fully configured.")
            check_hb_log(lb_file)


if __name__ == "__main__":
    main()
