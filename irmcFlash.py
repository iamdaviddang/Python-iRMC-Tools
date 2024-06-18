import argparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from functions import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="iRMCIP/USN + File")
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
        
    file_path, file = get_newest_file()   
    print(f"\niRMC will be flashed with file: {file}\n") 
    
    if not check_file_type(file):
        print("Wrong file type! Allowed file extensions: bin, bin_enc, ima, ima_enc")
        os._exit(0)
        
    answer = input("Is the file correct? y/n and then ENTER:\n")
    if answer == "n" or answer == "N":
        print("Exiting..")
        os._exit(0)
           
    password = find_password(irmc_ip)
    power_off(irmc_ip)
    time.sleep(10)
    print("Flash starting:")
    update_irmc_firmware(irmc_ip, password, file_path)
