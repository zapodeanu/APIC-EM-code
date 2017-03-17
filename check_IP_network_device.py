# developed by Gabi Zapodeanu, Cisco Systems, TSA, GSSE

# !/usr/bin/env python3

import requests
import json
import requests.packages.urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings

# Declarations for the controller info. The values will need to change for the proper Sandbox info,
# or the customer controller

APIC_EM = 'sandboxapic.cisco.com/api/v1'
APIC_EM_USER = 'devnetuser'
APIC_EM_PASSW = 'Cisco123!'


# AP IP address to test 10.1.14.3
# network device IP address to test 10.2.2.2
# network device IP address to test 10.2.1.1


def pprint(json_data):
    """
    Pretty print JSON formatted data
    :param json_data:
    :return:
    """

    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))


def get_service_ticket():
    """
    This function will generate the Auth apic_em_ticket required to access APIC-EM
    API call to /apic_em_ticket is used to create a new user apic_em_ticket
    :return: apic_em_ticket
    """

    payload = {'username': APIC_EM_USER, 'password': APIC_EM_PASSW}
    url = 'https://' + APIC_EM + '/ticket'
    header = {'content-type': 'application/json'}
    ticket_response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    if not ticket_response:
        print('No data returned!')
    else:
        ticket_json = ticket_response.json()
        ticket = ticket_json['response']['serviceTicket']
        print('Created APIC-EM apic_em_ticket: ', ticket)
        return ticket


def get_input_ip():
    """
    This function will ask the user to input the IP address. The format x.x.x.x of the IP address is not validated
    The function will return the IP address
    :return: the IP address
    """

    ip_address = input('Input the IP address to be validated?  ')
    return ip_address


def check_device(interface_ip):
    """
    This function will find out if there is a network device interface configured with an IP address
    The function will call two APIs:
    /interface/ip-address/{ip-address} - required for most of the network devices
    /network-device/ip-address/{ip-address} - required for access points
    :param interface_ip: ip address to be validated if configured on any network devices
    :return: 
    """

    url = 'https://' + APIC_EM + '/interface/ip-address/' + interface_ip
    header = {'accept': 'application/json', 'X-Auth-Token': apic_em_ticket}
    interface_response = requests.get(url, headers=header, verify=False)
    if not interface_response:
        url = 'https://' + APIC_EM + '/network-device/ip-address/' + interface_ip  # verification required for wireless AP's IP address
        header = {'accept': 'application/json', 'X-Auth-Token': apic_em_ticket}
        device_response = requests.get(url, headers=header, verify=False)
        if not device_response:
            print('The IP address ', interface_ip, ' is not configured on any network devices')
        else:
            print('The IP address ', interface_ip, ' is configured on a wireless access point')
    else:
        print('The IP address ', interface_ip, ' is configured on a network device')


def main():
    """
    This simple script will find out if there is a network device interface configured with an IP address
    It will ask the user to input an IP address to be validated
    It will print information if the input IP address is configured on a network device interface or not
    """

    # create an auth apic_em_ticket for APIC-EM

    global apic_em_ticket  # make the apic_em_ticket a global variable in this module
    apic_em_ticket = get_service_ticket()

    # input IP address for client

    device_ip_address = get_input_ip()
    print('IP Address to be validated:', device_ip_address)

    # check if the input IP address is used by a network device

    check_device(device_ip_address)


if __name__ == '__main__':
    main()

