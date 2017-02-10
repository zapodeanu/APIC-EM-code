# developed by Gabi Zapodeanu, Cisco Systems, TSA, GPO

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

# client IP addresses to test 10.2.1.22 - ethernet
# client IP addresses to test 10.1.15.117 - wifi


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


def get_input_ip():
    """
    This function will ask the user to input the IP address. The format of the IP address is not validated
    The function will return the IP address
    :return: the IP address
    """

    ip_address = input('Input the IP address to be validated?  ')
    return ip_address


def check_client_ip_address(client_ip):
    """
    The function will find out if APIC-EM has a client device configured with the specified IP address.
    API call to /host
    It will print if a client device exists or not.
    :param client_ip: client IP address
    :return: None
    """

    url = 'https://' + APIC_EM + '/host'
    header = {'accept': 'application/json', 'X-Auth-Token': APIC_EM_TICKET}
    payload = {'hostIp': client_ip}
    host_response = requests.get(url, params=payload, headers=header, verify=False)
    host_json = host_response.json()
    if not host_json['response']:
        print('The IP address ', client_ip, ' is not used by any client devices')
    else:
        print('The IP address ', client_ip, ' is used by a client device')
        # print (json.dumps(host_json, indent=4, separators=(' , ', ' : ')))    # sample print json output, optional
        host_info = host_json['response'][0]
        host_type = host_info['hostType']
        if host_type == 'wireless':     # verification required for wireless clients, JSON output is different for wireless vs. wired clients
            apic_em_device_id = host_info['connectedNetworkDeviceId']
            interface_name = 'VLAN '+ host_info['vlanId']
        else:
            interface_name = host_info['connectedInterfaceName']
            apic_em_device_id = host_info['connectedNetworkDeviceId']
        hostname = get_hostname_id(deviceId)[0]
        device_type = get_hostname_id(deviceId)[1]
        print('The IP address ', clientIP, ' is connected to the network device ', hostname, ',  ', device_type, ',  interface ', interfaceName)
        return hostname, interface_name


def get_hostname_id(device_id):
    """
    The function will find out the hostname of the network device with the specified device ID
    The function will require two values, the Auth ticket and device id
    The function with return the hostname and the device type of the network device
    API call to sandboxapic.cisco.com/api/v1/network-device/{id}
    :param device_id: APIC-EM device id
    :return:
    """
    hostname = None
    url = 'https://' + APIC_EM + '/network-device/' + device_id
    header = {'accept': 'application/json', 'X-Auth-Token': apic_em_ticket}
    hostname_response = requests.get(url, headers=header, verify=False)
    hostname_json = hostname_response.json()
    hostname = hostname_json['response']['hostname']
    devicetype =  hostname_json['response']['type']
    return hostname, devicetype


def main():
    """
    This simple script will find out if there is a client connected to the Enterprise network
    It will ask the user to input an IP address for a client device.
    It will print information if the input IP address is being used by a client or not
    It will find out information about the client, the MAC address and connectivity
    """

    # create an auth ticket for APIC-EM

    global APIC_EM_TICKET    # make the ticket a global variable in this module
    APIC_EM_TICKET = get_service_ticket()

    # input IP address for client

    client_ip_address = get_input_ip()
    print('IP Address to be validated:', client_ip_address)

    # check if the input IP address is used by network clients

    check_client_ip_address(client_ip_address)


if __name__ == '__main__':
    main()
