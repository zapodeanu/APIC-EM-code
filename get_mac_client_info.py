# developed by Gabi Zapodeanu, Cisco Systems, TSA, GSSE, Cisco Systems

# !/usr/bin/env python3


import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings

# declarations for Sandbox APIC-EM API url, username and password

APIC_EM = 'sandboxapic.cisco.com/api/v1'
APIC_EM_USER = 'devnetuser'
APIC_EM_PASSW = 'Cisco123!'
