import sys
import argparse
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from functions import *
from getUnitInfo import check_power_status


def get_sdcard_info(password, ip_address):

  url = f"https://{ip_address}/redfish/v1/Systems/0/Oem/ts_fujitsu/SDCard"
  auth = requests.auth.HTTPBasicAuth("admin", password)

  try:
    response = requests.get(url, auth=auth, verify=False)
    if response.status_code == 200:
      data = json.loads(response.text)
      return data
    else:
      print(f"Chyba při získávání informací o SD kartě: {response.status_code}")
      return None
  except Exception as e:
    print(f"Neočekávaná chyba: {e}")
    return None

def get_sdcard_summary(data):

  if not data or "@odata.id" not in data:
    return None

  summary = {
    "Id": data.get("Id"),
    # "Name": data.get("Name"),
    "Status": data.get("Status"),
    "Inserted": data.get("Inserted"),
    "Mounted": data.get("Mounted"),
    "CapacityMB": data.get("CapacityMB"),
    "FreeSpacePercent": data.get("FreeSpacePercent"),
    "FreeSpaceMB": data.get("FreeSpaceMB"),
  }

  return summary



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
    summary = get_sdcard_summary(get_sdcard_info(password, irmc_ip))

    if summary:
        print(json.dumps(summary, indent=2))
    else:
        print("Získání informací o SD kartě se nezdařilo.")
