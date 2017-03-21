# developed by Gabi Zapodeanu, Cisco Systems, TSA, GSSE, Cisco Systems

# !/usr/bin/env python3


import requests
import json
import csv
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings

# Declarations for the controller info. The values will need to change for the proper Sandbox info,
# or the customer controller

APIC_EM = 'sandboxapic.cisco.com/api/v1'
APIC_EM_USER = 'devnetuser'
APIC_EM_PASSW = 'Cisco123!'


def pprint(json_data):
    """
    Pretty print JSON formatted data
    :param json_data:
    :return:
    """

    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))


def get_service_ticket():
    """
    This function will create a new APIC-EM ticket. If successful it will print the ticket
    :param: username and password, global constants
    :return: APIC-EM ticket number
    """

    payload = {'username': APIC_EM_USER, 'password': APIC_EM_PASSW}
    url = 'https://' + APIC_EM + '/ticket'
    header = {'content-type': 'application/json'}
    ticket_response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    if not ticket_response:
        print('Something went wrong, try again!')
    else:
        ticket_json = ticket_response.json()
        ticket = ticket_json['response']['serviceTicket']
        print('APIC-EM ticket: ', ticket)  # print the ticket for reference only, not required
        return ticket


def get_input_file():
    """
    The function will ask the user to input the file name to save data to
    The function will append .csv and return the file name with extension
    :return: filename
    """

    filename = input('Input the file name to save data to:  ') + '.csv'
    return filename
    

def main():
    """
    This application will create a list of all the APIC-EM discovered network switches, their serial numbers and
    active software licenses.
    We will follow by creating an inventory for each access port: native VLAN, voice VLAN, MAC address connected
    to each switchport
    We will access a DevNet Sandbox to run this script.
    Changes to the APIC-EM url, username and password are required if desired to access a different APIC-EM controller.
    :return:
    """

    # create an auth ticket for APIC-EM

    global APIC_EM_TICKET  # make the ticket a global variable in this module
    APIC_EM_TICKET = get_service_ticket()


if __name__ == '__main__':
    main()
