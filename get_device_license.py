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


def get_license_device(deviceid, ticket):
    """
    The function will find out the active licenses of the network device with the specified device ID
    API call to sandboxapic.cisco.com/api/v1//license-info/network-device/{id}
    :param deviceid: APIC-EM network device id
    :param ticket: APIC-EM ticket
    :return: license information for the device, as a list with all licenses
    """

    license_info = []
    url = 'https://' + APIC_EM + '/license-info/network-device/' + deviceid
    header = {'accept': 'application/json', 'X-Auth-Token': ticket}
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
    else:
        pass
    return license_info


def get_hostname_devicetype_serialnumber(deviceid, ticket):
    """
    The function will find out the hostname of the network device with the specified device ID
    API call to sandboxapic.cisco.com/api/v1/network-device/{id}
    :param deviceid: APIC-EM network device id
    :param ticket: APIC-EM ticket
    :return: device hostname, device type, serial number
    """

    url = 'https://' + APIC_EM + '/network-device/' + deviceid
    header = {'accept': 'application/json', 'X-Auth-Token': ticket}
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


def get_device_ids(ticket):
    """
    The function will build the ID's list for all network devices
    API call to sandboxapic.cisco.com/api/v1/network-device
    :param ticket: APIC-EM ticket
    :return: APIC-EM devices id list
    """
    device_id_list = []
    url = 'https://' + APIC_EM + '/network-device'
    header = {'accept': 'application/json', 'X-Auth-Token': ticket}
    device_response = requests.get(url, headers=header, verify=False)
    device_json = device_response.json()
    device_info = device_json['response']
    for items in device_info:
        device_id = items.get('id')
        device_id_list.append(device_id)
    return device_id_list


def collect_device_info(device_id_list, ticket):
    """
    The function will create a list of lists.
    For each device we will have a list that includes - hostname, Serial Number, and active licenses
    The function will require two values, the list with all device id's and the Auth ticket
    :param device_id_list: APIC-EM devices id list
    :param ticket: APIC-EM ticket
    :return: all devices license file
    """

    all_devices_license_file = []
    for device_id in device_id_list:  # loop to collect data from each device
        license_file = []
        print('device id ', device_id)  # print device id, printing messages will show progress
        host_name = get_hostname_devicetype_serialnumber(device_id, ticket)[0]
        serial_number = get_hostname_devicetype_serialnumber(device_id, ticket)[2]
        license_file.append(host_name)
        license_file.append(serial_number)
        device_license = get_license_device(device_id, ticket)  # call the function to provide active licenses
        for licenses in device_license:  # loop to append the provided active licenses to the device list
            license_file.append(licenses)
        all_devices_license_file.append(license_file)  # append the created list for this device to the list of lists
    return all_devices_license_file


def main():
    """
    This application will create a list of all the APIC-EM discovered network devices, their serial numbers and
    active software licenses.
    We will access a DevNet Sandbox to run this script.
    Changes to the APIC-Em url, username and password are required if desired to access a different APIC-EM controller.
    :return:
    """

    # create an APIC-EM Auth ticket
    ticket = get_service_ticket()

    # build a list with all device id's
    device_id_list = get_device_ids(ticket)
    devices_info = collect_device_info(device_id_list, ticket)

    # ask user for filename input and save file
    filename = get_input_file()
    output_file = open(filename, 'w', newline='')
    output_writer = csv.writer(output_file)
    for lists in devices_info:
        output_writer.writerow(lists)
    output_file.close()
    # pprint(devices_info)    # print for data validation


if __name__ == '__main__':
    main()
