# developed by Gabi Zapodeanu, Cisco Systems, TSA, GPO

# !/usr/bin/env python3


import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings


# declarations for Sandbox APIC-EM API url, username and password

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

    ip_address = input('Input q to exit or the IP address to be validated: ')
    return ip_address


def check_client_ip_address(client_ip):
    """
    The function will find out if APIC-EM has a client device configured with the specified IP address
    The function will require two values, the Auth ticket and the client IP address
    API call to /host, get host with hostIp (string): IP address of the host
    The JSON response is different for wired and wireless client
    :param client_ip: client IP address
    :param ticket: APIC-EM ticket
    :return:
    """

    interfaceName = None
    hostname = None
    host_info = None
    url = 'https://' + APIC_EM + '/host'
    header = {'accept': 'application/json', 'X-Auth-Token': APIC_EM_TICKET}
    payload = {'hostIp': client_ip}
    host_response = requests.get(url, params=payload, headers=header, verify=False)
    host_json = host_response.json()
    if host_json['response'] == []:
        print ('The IP address ', client_ip, ' is not used by any client devices')
    else:
        host_info = host_json['response'][0]
        hostType = host_info['hostType']
        if hostType == 'wireless':     # verification required for wireless clients, JSON output is different for wireless vs. wired clients
            deviceId = host_info['connectedNetworkDeviceId']
            interfaceName = 'VLAN '+ host_info['vlanId']
        else:
            interfaceName = host_info['connectedInterfaceName']
            deviceId = host_info['connectedNetworkDeviceId']
        hostName = get_hostname_id(deviceId)[0]
        devicetype = get_hostname_id(deviceId)[1]
        print('The IP address ', client_ip, ' is connected to the network device ', hostName, ',  ', devicetype, ',  interface ', interfaceName)
        return hostName, interfaceName


def get_interface_name(interface_ip):
    """
    The function will find out if APIC-EM has a network device with the specified IP address configured on an interface
    API call to /interface/ip-address/{ipAddress}, gets list of interfaces with the given IP address.
    The JSON response is different for wireless AP's comparing with switches and routers.
    There is a nested function, get_hostname_IP , to find out the information about wireless
    AP's based on the management IP address
    :param interface_ip: IP address to check
    :param ticket: APIC-EM ticket
    :return: network device hostname
    """

    interfaceInfo = None
    url = 'https://' + APIC_EM + '/interface/ip-address/' + interface_ip
    header = {'accept': 'application/json', 'X-Auth-Token': APIC_EM_TICKET}
    interfaceInfo_response = requests.get(url, headers=header, verify=False)
    if not interfaceInfo_response:
        deviceIP = interface_ip
        url = 'https://' + APIC_EM + '/network-device/ip-address/' + deviceIP    # verification required by wireless AP's IP address
        header = {'accept': 'application/json', 'X-Auth-Token': APIC_EM_TICKET}
        deviceInfo_response = requests.get(url, headers=header, verify=False)
        if not deviceInfo_response:
            print ('The IP address ', interface_ip, ' is not configured on any network devices')
        else:
            hostName = get_hostname_IP(deviceIP)[0]
            devicetype = get_hostname_IP(deviceIP)[1]
            print('The IP address ', deviceIP, ' is configured on network device ', hostName, ',  ', devicetype)
            return hostName
    else:
        interfaceInfo_json = interfaceInfo_response.json()
        # print (json.dumps(interfaceInfo_json, indent=4, separators=(' , ', ' : ')))  # sample print json output, optional, remove the comment from the beginning of the line
        interfaceInfo = interfaceInfo_json['response'][0]
        interfaceName = interfaceInfo['portName']
        deviceId = interfaceInfo['deviceId']
        hostName = get_hostname_id(deviceId)[0]
        devicetype = get_hostname_id(deviceId)[1]
        print('The IP address ', interface_ip, ' is configured on network device ', hostName, ',  ', devicetype, ',  interface ', interfaceName)
        return hostName


def get_hostname_id(deviceId):
    """
    The function will find out the hostname of the network device with the specified device ID
    API call to /network-device/{id}
    :param deviceId: APIC-EM device id
    :param ticket: APIC-EM ticket
    :return: network device hostname and type
    """

    hostname = None
    url = 'https://' + APIC_EM + '/network-device/' + deviceId
    header = {'accept': 'application/json', 'X-Auth-Token': APIC_EM_TICKET}
    hostname_response = requests.get(url, headers=header, verify=False)
    hostname_json = hostname_response.json()
    hostname = hostname_json['response']['hostname']
    devicetype =  hostname_json['response']['type']
    return hostname, devicetype




def get_hostname_IP(deviceIP):
    """
    The function will find out the hostname of the network device with the specified management IP address
    API call to sandboxapic.cisco.com/api/v1/network-device/ip-address/{ip-address}
    :param deviceIP: IP address to check
    :param ticket: APIC-EM ticket
    :return: network device hostname and type
    """

    hostname = None
    url = 'https://' + APIC_EM + '/network-device/ip-address/' + deviceIP
    header = {'accept': 'application/json', 'X-Auth-Token': APIC_EM_TICKET}
    hostname_response = requests.get(url, headers=header, verify=False)
    hostname_json = hostname_response.json()
    hostname = hostname_json['response']['hostname']
    devicetype =  hostname_json['response']['type']
    return hostname, devicetype



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

    global APIC_EM_TICKET    # make the ticket a global variable in this module
    APIC_EM_TICKET = get_service_ticket()

    # this loop will allow running the validation multiple times, until user input is 'q'

    ip_address = None
    while ip_address != "q":
        interface_ip = get_input_ip()
        if interface_ip != 'q':
            check_client_ip_address(ip_address)
            get_interface_name(ip_address)


if __name__ == '__main__':
    main()

