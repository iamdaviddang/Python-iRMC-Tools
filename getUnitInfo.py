import requests
import argparse
import os
from functions import *
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from sysFWinfo import get_system_fw_info

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
    
    # API request pro zjisteni modelu a rady(M5,M6,M7,M2)
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
        
    # API request pro zjisteni jestli je jednotka zapnuta nebo vypnuta
    url = f"https://{ip}/redfish/v1/Systems/0"
    auth = ('admin', password)
    response = requests.get(url, auth=auth, verify=False)
    power_status = response.json()['PowerState']
    
    print(f"\n Model: {model} \n")
    print(f"\n iRMC IP: {ip} \n")
    print(f"\n iRMC Password: {password} \n")
    print(f"\n Power-Status: {power_status} \n")

    return power_status, password


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="iRMCIP/USN")
    parser.add_argument('userInput', type=str, help="iRMCIP/USN")
    args = parser.parse_args()
    
    irmc_ip = ""
    if args.userInput.startswith("172.25."):
        irmc_ip = args.userInput
        power_status, password = check_power_status(irmc_ip)
        get_system_fw_info(irmc_ip, "admin", password)
        os._exit(0)
    elif args.userInput.startswith("EW"):
        if len(args.userInput) != 10:
            print("USN length is not correct! Please check it.")
        
        irmc_ip = get_irmc_ip(args.userInput)["ip"]
        power_status, password = check_power_status(irmc_ip)
        get_system_fw_info(irmc_ip, "admin", password)
        os._exit(0)
