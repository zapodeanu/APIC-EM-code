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


def get_license_device(deviceid):
    """
    The function will find out the active licenses of the network device with the specified device ID
    API call to sandboxapic.cisco.com/api/v1//license-info/network-device/{id}
    :param deviceid: APIC-EM network device id
    :return: license information for the device, as a list with all licenses
    """

    license_info = []
    url = 'https://' + APIC_EM + '/license-info/network-device/' + deviceid
    header = {'accept': 'application/json', 'X-Auth-Token': APIC_EM_TICKET}
    payload = {'deviceid': deviceid}
    device_response = requests.get(url, params=payload, headers=header, verify=False)
    if device_response.status_code == 200:
        device_json = device_response.json()
        device_info = device_json['response']
        # pprint(device_info)    # use this for printing info about each device
        for licenses in device_info:
            try:  # required to avoid errors due to some devices, for example Access Points,
                # that do not have an "inuse" license.
                if licenses.get('status') == 'INUSE':
                    new_license = licenses.get('name')
                    if new_license not in license_info:
                        license_info.append(new_license)
            except:
                pass
    return license_info


def get_hostname_devicetype_serialnumber(deviceid):
    """
    The function will find out the hostname of the network device with the specified device ID
    API call to sandboxapic.cisco.com/api/v1/network-device/{id}
    :param deviceid: APIC-EM network device id
    :return: device hostname, device type, serial number
    """

    url = 'https://' + APIC_EM + '/network-device/' + deviceid
    header = {'accept': 'application/json', 'X-Auth-Token': APIC_EM_TICKET}
    hostname_response = requests.get(url, headers=header, verify=False)
    hostname_json = hostname_response.json()
    hostname = hostname_json['response']['hostname']
    device_type = hostname_json['response']['type']
    serial_number = hostname_json['response']['serialNumber']
    return hostname, device_type, serial_number


def get_input_file():
    """
    The function will ask the user to input the file name to save data to
    The function will append .csv and return the file name with extension
    :return: filename
    """

    filename = input('Input the file name to save data to:  ') + '.csv'
    return filename


def get_switch_ids():
    """
    The function will build the ID's list for all network switches
    API call to sandboxapic.cisco.com/api/v1/network-device
    :return: network switches APIC-EM id list
    """

    device_id_list = []
    url = 'https://' + APIC_EM + '/network-device'
    header = {'accept': 'application/json', 'X-Auth-Token': APIC_EM_TICKET}
    device_response = requests.get(url, headers=header, verify=False)
    device_json = device_response.json()
    device_info = device_json['response']
    for items in device_info:
        if items.get('family') == 'Switches and Hubs':
            device_id = items.get('id')
            device_id_list.append(device_id)
    return device_id_list


def collect_switch_info(device_id_list):
    """
    The function will create a list of lists.
    For each device we will have a list that includes - hostname, Serial Number, and active licenses
    The function will require two values, the list with all device id's and the Auth ticket
    :param device_id_list: APIC-EM devices id list
    :return: all devices license file
    """

    all_switches_info_list = []
    for device_id in device_id_list:  # loop to collect data from each device
        info_list = []
        print('device id ', device_id)  # print device id, printing messages will show progress
        host_name = get_hostname_devicetype_serialnumber(device_id)[0]
        serial_number = get_hostname_devicetype_serialnumber(device_id)[2]
        info_list.append(host_name)
        info_list.append(serial_number)
        device_license = get_license_device(device_id)  # call the function to provide active licenses
        for licenses in device_license:  # loop to append the provided active licenses to the device list
            info_list.append(licenses)
        all_switches_info_list.append(info_list)  # append the created list for this device to the list of lists
    return all_switches_info_list


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

    # build a list with all device id's
    switch_id_list = get_switch_ids()
    switches_info = collect_switch_info(switch_id_list)

    # ask user for filename input and save file
    filename = get_input_file()
    output_file = open(filename, 'w', newline='')
    output_writer = csv.writer(output_file)
    for lists in switches_info:
        output_writer.writerow(lists)
    output_file.close()
    # pprint(switches_info)    # print for data validation


if __name__ == '__main__':
    main()
