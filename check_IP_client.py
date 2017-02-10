# developed by Gabi Zapodeanu, Cisco Systems, TSA, GPO

# !/usr/bin/env python3

import requests
import json
import time
import requests.packages.urllib3
import base64
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth  # for Basic Auth

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings
