import argparse
from bs4 import BeautifulSoup
import pyperclip
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from functions import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="USN")
    parser.add_argument('USN', type=str, help="USN")
    args = parser.parse_args()
    
    if not args.USN.startswith("EW"):
        print("ERROR: Unknown user input. USN must start with EW..")
        os._exit(0)
    
    if not args.USN.startswith(("EWCC", "EWCE", "EWCD", "EWCP", "EWCM", "EWCR", "EWCQ", "EWCT", "EWCS", "EWBT", "EWCL")):
        print("\n############################")
        print("This model is not supported.\nSupported models are:\n-RX2540M7 (EWCE...)\n-RX2530M7 (EWCD,EWCP...)\n-TX2550M7 (EWCC...)\n-RX1440M2 (EWCM...)\n-all MM6(EWCR, EWCQ, EWCT, EWCS)")
        print("############################")
        os._exit(0)
        
    if len(args.USN) != 10:
        print("\nUSN length is not correct! Please check it.")
        os._exit(0)
    
    try:
        irmc_ip = get_irmc_ip(args.USN)
        print(f"\niRMC IP for {args.USN} is: {irmc_ip["ip"]}")
        pyperclip.copy(irmc_ip["ip"])
        print("IP has been found and copied to your clipboard")
    except:
        print(irmc_ip)
