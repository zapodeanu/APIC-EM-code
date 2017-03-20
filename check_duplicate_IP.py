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

# client IP addresses to test 10.2.1.22 - ethernet connected
# client IP addresses to test 10.1.15.117 - wifi connected
# wireless AP IP address to test 10.1.14.3
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
    The function will return the IP address as a string
    :return: the IP address
    """

    ip_address = input('Input the IP address to be validated, (or q to exit) ? ')
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

    # pprint(host_json)  # needed for troubleshooting

    # verification if client found or not

    if not host_json['response']:
        print('The IP address', client_ip, 'is not used by any client devices')
    else:
        print('The IP address', client_ip, 'is used by a client device')
        host_info = host_json['response'][0]
        host_type = host_info['hostType']
        host_vlan = host_info['vlanId']

        # verification required for wireless clients, JSON output is different for wireless vs. wired clients

        if host_type == 'wireless':

            # info for wireless clients

            apic_em_device_id = host_info['connectedNetworkDeviceId']
            hostname = get_hostname_id(apic_em_device_id)[0]
            device_type = get_hostname_id(apic_em_device_id)[1]
            print('The IP address', client_ip, ', is connected to the network device:', hostname, ', model:', device_type, ', interface VLAN:', host_vlan)
            interface_name = host_vlan
        else:

            # info for ethernet connected clients

            interface_name = host_info['connectedInterfaceName']
            apic_em_device_id = host_info['connectedNetworkDeviceId']
            hostname = get_hostname_id(apic_em_device_id)[0]
            device_type = get_hostname_id(apic_em_device_id)[1]
            print('The IP address', client_ip, ', is connected to the network device:', hostname, ', model:',
                  device_type, ', interface:', interface_name, ', VLAN:', host_vlan)


def get_interface_name(interface_ip):
    """
    The function will find out if APIC-EM has a network device with the specified IP address configured on an interface
    API call to /interface/ip-address/{ipAddress}, gets list of interfaces with the given IP address.
    The JSON response is different for wireless AP's comparing with switches and routers.
    There is a nested function, get_hostname_ip , to find out the information about wireless
    AP's based on the management IP address
    :param interface_ip: IP address to check
    :return: network device hostname
    """

    url = 'https://' + APIC_EM + '/interface/ip-address/' + interface_ip
    header = {'accept': 'application/json', 'X-Auth-Token': APIC_EM_TICKET}
    interface_info_response = requests.get(url, headers=header, verify=False)
    if not interface_info_response:
        device_ip = interface_ip
        url = 'https://' + APIC_EM + '/network-device/ip-address/' + device_ip  # verification required by
        # wireless AP's IP address
        header = {'accept': 'application/json', 'X-Auth-Token': APIC_EM_TICKET}
        device_info_response = requests.get(url, headers=header, verify=False)
        if not device_info_response:
            print('The IP address ', interface_ip, ' is not configured on any network devices')
        else:
            hostname = get_hostname_ip(device_ip)[0]
            device_type = get_hostname_ip(device_ip)[1]
            print('The IP address ', device_ip, ' is configured on network device ', hostname, ',  ', device_type)
            return hostname
    else:
        interface_info_json = interface_info_response.json()
        interface_info = interface_info_json['response'][0]
        interface_name = interface_info['portName']
        device_id = interface_info['deviceId']
        hostname = get_hostname_id(device_id)[0]
        device_type = get_hostname_id(device_id)[1]
        print('The IP address ', interface_ip, ' is configured on network device ', hostname, ',  ',
              device_type, ',  interface ', interface_name)
        return hostname


def get_hostname_id(device_id):
    """
    The function will find out the hostname of the network device with the specified device ID
    API call to /network-device/{id}
    :param device_id: APIC-EM device id
    :return: network device hostname and type
    """

    url = 'https://' + APIC_EM + '/network-device/' + device_id
    header = {'accept': 'application/json', 'X-Auth-Token': APIC_EM_TICKET}
    hostname_response = requests.get(url, headers=header, verify=False)
    hostname_json = hostname_response.json()
    hostname = hostname_json['response']['hostname']
    device_type = hostname_json['response']['type']
    return hostname, device_type


def get_hostname_ip(device_ip):
    """
    The function will find out the hostname of the network device with the specified management IP address
    API call to sandboxapic.cisco.com/api/v1/network-device/ip-address/{ip-address}
    :param device_ip: IP address to check
    :return: network device hostname and type
    """

    url = 'https://' + APIC_EM + '/network-device/ip-address/' + device_ip
    header = {'accept': 'application/json', 'X-Auth-Token': APIC_EM_TICKET}
    hostname_response = requests.get(url, headers=header, verify=False)
    hostname_json = hostname_response.json()
    hostname = hostname_json['response']['hostname']
    device_type = hostname_json['response']['type']
    return hostname, device_type


def main():
    """
    This script will validate if user provided IP addresses are already configured on a network device,
    either if the interface is up or down. It will also validate if a client may be using the IP address.
    If the IP address is being used, it will return the hostname of the network device
    the model and the interface configured with the IP address.
    If the IP address is used by a client it will provide or the hostname of the network device connected to the client,
    the model, and the interface connected to the client using the IP address.
    A while loop will allow to check multiple IP addresses, until user input is 'q'
    """

    # create an auth ticket for APIC-EM

    global APIC_EM_TICKET  # make the ticket a global variable in this module
    APIC_EM_TICKET = get_service_ticket()

    # this loop will allow running the validation multiple times, until user input is 'q'

    ip_address = None
    while ip_address != "q":
        ip_address = get_input_ip()
        if ip_address != 'q':
            check_client_ip_address(ip_address)
            get_interface_name(ip_address)


if __name__ == '__main__':
    main()
