# developed by Gabi Zapodeanu, Cisco Systems, TSA, GSSE, Cisco Systems

# !/usr/bin/env python3


import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings

# Declarations for the controller info. The values will need to change for the proper Sandbox info,
# or the customer controller

APIC_EM = 'sandboxapic.cisco.com/api/v1'
APIC_EM_USER = 'devnetuser'
APIC_EM_PASSW = 'Cisco123!'

# wired client mac address: 5c:f9:dd:52:07:78
# wired client mac address: e8:9a:8f:7a:22:99
# wireless client mac address: 00:24:d7:43:59:d8


def pprint(json_data):
    """
    Pretty print JSON formatted data
    :param json_data:
    :return:
    """

    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))


def get_service_ticket():
    """
    This function will generate the Auth ticket required to access APIC-EM
    API call to /ticket is used to create a new user ticket
    :return: ticket
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
        print('Created APIC-EM ticket: ', ticket)
        return ticket


def get_input_mac():
    """
    This function will ask the user to input the IP address. The format of the IP address is not validated
    The function will return the IP address
    :return: the IP address
    """

    mac_address = input('Input the MAC address to be validated, (or q to exit) ?  ')
    return mac_address


def main():
    """
    This simple script will find out if there is a client connected to the Enterprise network
    It will ask the user to input a MAC address for a client device.
    It will print information if the input MAC address is being used by a client or not
    It will find out information about the client, and the connectivity info, switch and wireless AP,
    interface connectivity, VLAN information
    There is a loop that will allow running the validation multiple times, until user input is 'q'
    """

    # create an auth ticket for APIC-EM

    global APIC_EM_TICKET    # make the ticket a global variable in this module
    APIC_EM_TICKET = get_service_ticket()

    # input MAC address for client

    client_mac_address = None
    while client_mac_address != "q":    # this loop will allow running the validation multiple times, until user input is 'q'
        client_mac_address = get_input_mac()
        if client_mac_address != 'q':
            check_client_mac_address(client_mac_address)  # check if the input IP address is used by network clients

if __name__ == '__main__':
    main()


