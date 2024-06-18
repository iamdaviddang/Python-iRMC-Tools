import sys
import argparse
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from functions import *
from getUnitInfo import check_power_status

def get_sel(irmc, password):
    user = "admin"
    ascend = False
    event_id = None
    
    
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    response = requests.get(
        "https://{}/redfish/v1/Managers/iRMC/LogServices/SystemEventLog/Entries".format(irmc),
        headers=headers,
        auth=(user, password),
        verify=False
    )

    if response.status_code != 200:
        print("ERROR: Failed to get the system event log information from the iRMC at {}".format(irmc))
        print("DETAILS: {}".format(response.json()['error']['message']))
        sys.exit()

    sel_entries_list = response.json()['Members']

    if ascend == True:
        sel_entries_list.reverse()

    if event_id is None:
        print("ID".rjust(3) + " | " + "Data/Time".ljust(25) +
              " | " + "Severity".ljust(8) + " | Event")
        print("------------------------------------------------------------------")
        for entry in sel_entries_list:
            print(entry["Id"].rjust(3) + " | " + entry["Created"].rjust(25) +
                  " | " + entry['Severity'].ljust(8) + " | " + entry["Message"])
    else:
        found = False
        for entry in sel_entries_list:
            if int(entry['Id']) == event_id:
                print("ID".rjust(3) + " | " + "Data/Time".ljust(25) +
                      " | " + "Severity".ljust(8) + " | Event")
                print("------------------------------------------------------------------")
                print(entry["Id"].rjust(3) + " | " + entry["Created"].rjust(25) +
                      " | " + entry['Severity'].ljust(8) + " | " + entry["Message"])
                found = True
                break

        if found == False:
            print("ERROR: Could not find the specified event (ID: {})".format(event_id))
            
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
    print("\nSEL:\n")
    get_sel(irmc_ip, password)