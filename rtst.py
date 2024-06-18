import argparse
import requests
import urllib3
import os
from functions import *
from clearSEL import clear_sel

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    reboot_system(irmc_ip)
