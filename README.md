# APIC-EM-code
This folder includes sample code to be used with APIC-EM DevNet Sandbox, or other APIC-EM controllers
Reccomendation - run the scripts with the IP or MAC addresses provided at the beginning of the sample code

1.   check_IP_client.py
    This simple script will find out if there is a client connected to the Enterprise network
    It will ask the user to input an IP address for a client device.
    It will print information if the input IP address is being used by a client or not

2.   check_IP_network_device.py
    This simple script will find out if there is a network device interface configured with an IP address
    It will ask the user to input an IP address to be validated
    It will print information if the input IP address is configured on a network device interface or not

3.   get_IP_client_info.py
    This simple script will find out if there is a client connected to the Enterprise network
    It will ask the user to input an IP address for a client device.
    It will print information if the input IP address is being used by a client or not
    It will find out information about the client, and the connectivity info, switch and wireless AP,
    interface connectivity, VLAN information
    There is a loop that will allow running the validation multiple times, until user input is 'q'

4.   get_mac_client_info.py
    This simple script will find out if there is a client connected to the Enterprise network
    It will ask the user to input a MAC address for a client device.
    It will print information if the input MAC address is being used by a client or not
    It will find out information about the client, and the connectivity info, switch and wireless AP,
    interface connectivity, VLAN information, and IP address associated with the MAC
    There is a loop that will allow running the validation multiple times, until user input is 'q'

5.   check_duplicate_IP.py
    This script will validate if user provided IP addresses are already configured on a network device,
    either if the interface is up or down. It will also validate if a client may be using the IP address.
    If the IP address is being used, it will return the hostname of the network device
    the model and the interface configured with the IP address.
    If the IP address is used by a client it will provide or the hostname of the network device connected to the client,
    the model, and the interface connected to the client using the IP address.
    A while loop will allow to check multiple IP addresses, until user input is 'q'