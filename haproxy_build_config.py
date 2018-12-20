#
# haproxy_build_config python script
# TO DO : add more verification tests like file exist ? etc... (no redundancy with DNS check)
#
# Peter Long / v=0.1b / Dec 2018
#

from string import Template
import sys


def main():
    # CONSTANT
    # for building the list of nodes for each TCP service
    HEADER = "    server "
    CMC_HTTPS_PARAMETERS = ":8443 check check-ssl verify none inter 5s rise 1 fall 2"
    S3_HTTP_PARAMETERS = ":80 check inter 5s rise 1 fall 2"
    S3_HTTPS_PARAMETERS = ":443 check check-ssl verify none inter 5s rise 1 fall 2"
    ADMIN_HTTPS_PARAMETERS = ":19443 check check-ssl verify none inter 5s rise 1 fall 2"

    # VARIABLE
    survey_file = "survey.csv"
    install_config_file = "CloudianInstallConfiguration.txt"
    template_file = "haproxy_template.cfg"
    haproxy_file = "haproxy.cfg"
    cmc_endpoint = ""
    cmc_https_list = []
    s3_endpoint = ""
    s3_http_list = []
    s3_https_list = []
    admin_endpoint = ""
    admin_https_list = []

    # Test arguments from command line
    # Define VARIABLE : install_config_file and survey_file if arguments exist
    nb_arg = len(sys.argv)
    if nb_arg != 1:
        if nb_arg != 3:
            print("Usage : " + sys.argv[0] + " " + survey_file + " " + install_config_file)
            sys.exit(1)
        else:
            survey_file = sys.argv[1]
            install_config_file = sys.argv[2]

    # Retrieve list of nodes + IPs and build lists for each TCP service
    # source : file "survey.csv"
    with open(survey_file, "r") as filein:
        line = filein.readline()
        while line != "":
            listing = line.split(",")
            cmc_https_list.append(HEADER + listing[1] + " " + listing[2] + CMC_HTTPS_PARAMETERS)
            s3_http_list.append(HEADER + listing[1] + " " + listing[2] + S3_HTTP_PARAMETERS)
            s3_https_list.append(HEADER + listing[1] + " " + listing[2] + S3_HTTPS_PARAMETERS)
            admin_https_list.append(HEADER + listing[1] + " " + listing[2] + ADMIN_HTTPS_PARAMETERS)
            line = filein.readline()

    # Retrieve Endpoint information (s3 domain, admin domain, cmc domain)
    # source : file "CloudianInstallConfiguration.txt"
    with open(install_config_file, "r") as filein:
        for line in filein:
            if "cloudian_s3_domain_region1=" in line:
                s3_endpoint = line.strip().split('=')[1]
            elif "cloudian_admin_host=" in line:
                admin_endpoint = line.strip().split('=')[1]
            elif "cloudian_cmc_domain" in line:
                cmc_endpoint = line.strip().split('=')[1]

    # Create the HA proxy config file
    # destination : file "haproxy.cfg" based on the template "haproxy_template.txt"
    with open(template_file, "r") as filein:
        # Read template file
        src = Template(filein.read())
        # Concatenate infos
        d = {'cmc_endpoint': cmc_endpoint, 's3_endpoint': s3_endpoint, 'admin_endpoint': admin_endpoint,
             'cmc_https_list': '\n'.join(cmc_https_list),
             's3_http_list': '\n'.join(s3_http_list), 's3_https_list': '\n'.join(s3_https_list),
             'admin_https_list': '\n'.join(admin_https_list)}
        # Substitution in the template --> result
        result = src.substitute(d)
        # Write result into haproxy file
        fileout = open(haproxy_file, "w")
        fileout.write(result)
        fileout.close()

    print("Done.\nHAProxy config file is : " + haproxy_file)
    print("Please copy the file " + haproxy_file + " on the haproxy server")
    print("Then reload the config + restart the haproxy service on the haproxy server")


if __name__ == "__main__":
    main()

