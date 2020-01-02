#!/usr/bin/python
#
# haproxy_build_config python script
# TODO : more complex stuff like global affinities (2 config for 2 HAProxy, 2 DCs)
#         work on parameters like : maxconn, nbproc, nbthread, cpu-map
#         work on parameter like : monitor fail & monitor-uri
#         work on a wizard instead parameters in command line (needed ??)
#
# Peter Long / v=0.6.1 / Jan 2020
# minor changes + improve backward compatibility with HS 7.1.x (due to IAM_DOMAIN not present)

# I can't use python methods or modules which are not installed on a HyperStore node
import argparse
import getpass
import os
from string import Template

# I am using python2 compatible commands (hyperstore uses python2) instead python3 commands.
# force input = raw_input
if hasattr(__builtins__, 'raw_input'):
    input = raw_input


# Push the haproxy config file to the haproxy server by using scp & ssh
# source : file "haproxy.cfg" standard
def push_config(haproxy_file):
    print("\n Your HAProxy config file is : " + haproxy_file + " and it is in the local/current directory\n")
    answer = input("Do you want to push & run this config file to your haproxy server ? (yes / no) : ")
    answer = answer.strip().lower()
    if answer.startswith('y'):
        # Force standard configuration for the SSH (root = avoid permission conflict)
        username = "root"
        hostname = input("Please, enter the IP address or the hostname of your haproxy server : ")
        print("Enter the " + username + " password for the connexion : ")
        password = getpass.getpass()
        # Remote actions on the haproxy server
        print("Trying to connect to the host : " + hostname + " with the " + username + " password ..." +
              " and then checking some parameters for you ...")
        print("Enabling the haproxy service on the haproxy server...")
        os.system("sshpass -p" + password + " ssh -o 'StrictHostKeyChecking no' "
                  + username + "@" + hostname + " systemctl enable haproxy")
        print("Backing up the old config on the haproxy server...")
        os.system("sshpass -p" + password + " ssh -o 'StrictHostKeyChecking no' "
                  + username + "@" + hostname + " cp /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.orig")
        print("Copying config file to haproxy server...")
        os.system("sshpass -p" + password + " scp -o 'StrictHostKeyChecking no' " + haproxy_file + " "
                  + username + "@" + hostname + ":/etc/haproxy/haproxy.cfg")
        print("Restarting haproxy service on the haproxy server...")
        os.system("sshpass -p" + password + " ssh -o 'StrictHostKeyChecking no' "
                  + username + "@" + hostname + " systemctl restart haproxy")
        print("Checking status of haproxy service...")
        os.system("sshpass -p" + password + " ssh -o 'StrictHostKeyChecking no' "
                  + username + "@" + hostname + " systemctl status haproxy")
    elif answer.startswith('n'):
        print("Please copy the file " + haproxy_file + " on the haproxy server (into /etc/haproxy/)")
        print("Then restart the haproxy service on the haproxy server via systemctl command")
        print("example : systemctl restart haproxy")
    else:
        print("Wrong answer. Exiting...")


def main():
    # CONSTANT
    # for building the list of nodes for each TCP service
    HEADER = "    server "
    CMC_HTTPS_PARAMETERS = ":8443 check check-ssl verify none inter 5s rise 1 fall 2"
    S3_HTTP_PARAMETERS = ":80 check inter 5s rise 1 fall 2"
    S3_HTTPS_PARAMETERS = ":443 check check-ssl verify none inter 5s rise 1 fall 2"
    ADMIN_HTTPS_PARAMETERS = ":19443 check check-ssl verify none inter 5s rise 1 fall 2"
    IAM_HTTP_PARAMETERS = ":16080 check inter 5s rise 1 fall 2"
    IAM_HTTPS_PARAMETERS = ":16443 check check-ssl verify none inter 5s rise 1 fall 2"
    # for options in the command line
    DEFAULT_BACKUP = "nobackupatall"
    DEFAULT_MAILSERVER = "nomailserver"

    # VARIABLE
    survey_file = "survey.csv"
    install_config_file = "CloudianInstallConfiguration.txt"
    template_file = "haproxy_template.cfg"
    haproxy_file = "haproxy.cfg"
    # Force empty value
    cmc_endpoint = ""
    cmc_https_list = []
    s3_endpoint = ""
    s3_http_list = []
    s3_https_list = []
    admin_endpoint = ""
    admin_https_list = []
    iam_endpoint = ""
    iam_http_list = []
    iam_https_list = []
    #    backup_parameter = ""
    use_backup_option = False
    mailserver = []
    mail_list = []
    dc_exist = False

    # Test arguments from command line
    # Define VARIABLE : install_config_file and survey_file in any case
    parser = argparse.ArgumentParser(description='parameters for the script')
    parser.add_argument('-s', '--survey', help="indicate the survey file, default = survey.csv",
                        default=survey_file)
    parser.add_argument('-i', '--install',
                        help="indicate the installation file, default = CloudianInstallConfiguration.txt",
                        default=install_config_file)
    parser.add_argument('-bs3', '--backups3',
                        help="indicate the DC in backup/stand-by mode for s3, default=none", default=DEFAULT_BACKUP)
    parser.add_argument('-ms', '--mailserver', help="mail server name or @IP for alerts", default=DEFAULT_MAILSERVER)
    parser.add_argument('-mf', '--mailfrom', help="indicate the sender, default = haproxy@localhost",
                        default='haproxy@localhost')
    parser.add_argument('-mt', '--mailto', help="indicate the recipient, default = root@localhost",
                        default='root@localhost')
    args = parser.parse_args()
    survey_file = args.survey
    install_config_file = args.install
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

    # 1st - Check if the haproxy_template.cfg exists
    if not (os.path.isfile(template_file)):
        print("Error, the file : " + template_file + " does not exist.")
        print("Check the path and the filename and try again")
        exit(1)

    # 2nd - Check if the two required files exist
    if not ((os.path.isfile(survey_file)) and (os.path.isfile(install_config_file))):
        print("Error, the required files : " + survey_file + " & " + install_config_file + " are wrong.")
        print("Check the path and the filename and try again")
        exit(1)

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
            cmc_https_list.append(HEADER + listing[1] + " " + listing[2] + CMC_HTTPS_PARAMETERS)
            s3_http_list.append(HEADER + listing[1] + " " + listing[2] + S3_HTTP_PARAMETERS + " " + backup_parameter)
            s3_https_list.append(HEADER + listing[1] + " " + listing[2] + S3_HTTPS_PARAMETERS + " " + backup_parameter)
            admin_https_list.append(HEADER + listing[1] + " " + listing[2] + ADMIN_HTTPS_PARAMETERS)
            iam_http_list.append(HEADER + listing[1] + " " + listing[2] + IAM_HTTP_PARAMETERS + " "
                                 + backup_parameter)
            iam_https_list.append(HEADER + listing[1] + " " + listing[2] + IAM_HTTPS_PARAMETERS + " "
                                  + backup_parameter)
            line = filein.readline()
    if (not dc_exist) and use_backup_option:
        print("Error, the expected DC : " + args.backups3 + " is not valid")
        print("This DC name : " + args.backups3 + " is not in the survey file : " + survey_file)
        print("Check the DC name or the survey file and try again")
        exit(1)

    # Retrieve Endpoint information (s3 domain, admin domain, cmc domain, iam domain)
    # source : file "CloudianInstallConfiguration.txt"
    with open(install_config_file, "r") as filein:
        for line in filein:
            if "cloudian_s3_domain_region1=" in line:
                s3_endpoint = line.strip().split('=')[1]
            elif "cloudian_admin_host=" in line:
                admin_endpoint = line.strip().split('=')[1]
            elif "cloudian_cmc_domain=" in line:
                cmc_endpoint = line.strip().split('=')[1]
            elif "cloudian_iam_host=" in line:
                iam_endpoint = line.strip().split('=')[1]

    # Test if IAM domain is present (not the case for 7.0 or 7.1 config files)
    if not iam_endpoint:
        print(" *** IAM Endpoint not found. Expected an older version like HS 7.0.x or 7.1.x ***")
        iam_endpoint = "iam.not-yet-configured"
        print("Your HAProxy config file will use a temporary iam domain instead like : " + iam_endpoint)

    # Create the HA proxy config file
    # destination : file "haproxy.cfg" based on the template "haproxy_template.cfg"
    with open(template_file, "r") as filein:
        # Read template file
        src = Template(filein.read())
        # Concatenate infos
        d = {'mailserver_line': '\n'.join(mailserver), 'cmc_endpoint': cmc_endpoint, 's3_endpoint': s3_endpoint,
             'admin_endpoint': admin_endpoint, 'iam_endpoint': iam_endpoint,
             'cmc_https_list': '\n'.join(cmc_https_list),
             's3_http_list': '\n'.join(s3_http_list), 's3_https_list': '\n'.join(s3_https_list),
             'admin_https_list': '\n'.join(admin_https_list), 'mail_list': '\n'.join(mail_list),
             'iam_http_list': '\n'.join(iam_http_list), 'iam_https_list': '\n'.join(iam_https_list)}
        # Substitution in the template --> result
        result = src.substitute(d)
        # Write result into haproxy file
        fileout = open(haproxy_file, "w")
        fileout.write(result)
        fileout.close()

    # Push the configuration file to the haproxy server
    # Prompt : yes or no + password
    push_config(haproxy_file)


if __name__ == "__main__":
    main()
