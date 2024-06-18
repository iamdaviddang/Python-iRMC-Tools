import argparse
import requests
import urllib3
import os
from functions import *
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from showSEL import get_sel

def check_power_status(ip):
    
    pws = {
        "M2": "Password@123",
        "M5": "admin",
        "M7": "Password@123",
        "RX2530M6": "admin",
        "RX2540M6": "admin",
        "RX4770M6": "admin",
        "TX1310M6": "Password@123",
        "TX1320M6": "Password@123",
        "TX1330M6": "Password@123",
        "RX1310M6": "Password@123",
        "RX1320M6": "Password@123",
        "RX1330M6": "Password@123"
    }
    
    def get_password(model):
        return pws.get(model, "defaultni_heslo")
    
    url = f"https://{ip}/redfish/v1"
    auth = ('', '')
    response = requests.get(url, auth=auth, verify=False)
    data = response.json()["Oem"]["ts_fujitsu"]["AutoDiscoveryDescription"]["ServerNodeInformation"]["Model"]
    rada_serveru = data.split()[2]
    model = data.split()[1]+rada_serveru
    
    password = ""
    if rada_serveru == "M7" or rada_serveru == "M2":
        password = "Password@123"
    elif rada_serveru == "M5":
        password = "admin"
    else:
        password = get_password(model)
        
    
    url = f"https://{ip}/redfish/v1/Systems/0"
    auth = ('admin', password)
    response = requests.get(url, auth=auth, verify=False)
    power_status = response.json()['PowerState']

    return power_status, password

def clear_sel(irmc, password):
    user = "admin"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    url = "https://{}/redfish/v1/Managers/iRMC/LogServices/SystemEventLog/Actions/LogService.ClearLog".format(irmc)
    response = requests.post(url, headers=headers, auth=(user, password), verify=False)

    if response.status_code != 204:
        print("ERROR: Failed to clear the system event log from the iRMC at {}".format(irmc))
        print("DETAILS: {}".format(response.json()['error']['message']))
    else:
        print("\nSEL has been cleared successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="iRMCIP/USN")
    parser.add_argument('userInput', type=str, help="iRMCIP/USN")
    args = parser.parse_args()
    
    irmc_ip = ""
    if args.userInput.startswith("172.25."):
        irmc_ip = args.userInput
        
    elif args.userInput.startswith("EW"):
        if len(args.userInput) != 10:
            print("\nUSN length is not correct! Please check it.")
            os._exit(0)
        irmc_ip = get_irmc_ip(args.userInput)["ip"]
    else:
        print("\nERROR: Unknown input.")
        os._exit(0)
        
    password = find_password(irmc_ip)
    clear_sel(irmc_ip, password)
    print("\nCurrent SEL for double check:\n")
    get_sel(irmc_ip, password)
    print("\n")
    