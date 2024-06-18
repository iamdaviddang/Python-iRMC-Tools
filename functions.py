import os
import shutil
import subprocess
import requests
from bs4 import BeautifulSoup
import socket
import logging
import time
import sys
import json


logging.basicConfig(filename='LOGs/LOG-FRU-rewrite.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_data(usn):
    base_url = "http://172.25.32.4/dev/api/v2/fru-tool/"
    url = f"{base_url}{usn}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Chyba pri volani API: {e}")
        return None

def find_ip_for_mac(formatted_mac):
    url = "http://172.25.32.1/catalyst/kea/ipv4leases"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')

        for row in table.find_all('tr')[1:]:
            columns = row.find_all('td')
            
            if len(columns) >= 3:
                mac_address = columns[1].text.strip().upper().replace(":", "")
                ip_address = columns[2].text.strip()
                
                if mac_address == formatted_mac:
                    return ip_address
    return None

def get_irmc_ip(usn):
  
  url = "http://172.25.32.4/api/v2/monitor/get-irmc-ip"
  
  body = {"usn": usn}

  try:
    response = requests.post(url, json=body)
    return response.json()
  except requests.exceptions.RequestException as e:
    return response.json()

def rewrite_serial_number(motherboard_sn, model):
    file_path = f'models/{model}/idp.INI'
    with open(file_path, 'r') as file:
        file_content = file.readlines()
        
    new_content = []
    
    for line in file_content:
        if line.strip().startswith("BoardSerialNumber"):
            line = f'    BoardSerialNumber=S,"{motherboard_sn.upper()}"\n'
        new_content.append(line)
        
    with open(file_path, 'w') as file:
        file.writelines(new_content)
    logging.info(f"Motherboard SN has been successfully written to idp.INI, MB SN: {motherboard_sn}")

def delete_current_idp():
    try:
        os.remove('idp.INI')
    except FileNotFoundError:
        pass

def move_file(model):
    src_file = f"models/{model}/idp.INI"
    shutil.copy(src_file, os.path.join(os.getcwd(), "idp.INI"))

def reformat_file():
    subprocess.run("IPMI_FRU64.exe -ini2bin=idp.ini")
    logging.info(" Reformat idp.INI to idp.BIN done")

def upload_fru_to_unit(ip,usn):
    try:
        try:
            password = "admin"
            fru_send_command = subprocess.run(f"IPMIVIEW64.exe -host={ip} -ini=WRFRU.INI -usr=admin -pwd={password}", shell=True, check=True)
            if fru_send_command.returncode != 0:
                logging.info("Failed to upload FRU with password: admin!")
            logging.info(f"MB FRU for {usn} has been uploaded successfully. iRMC Password={password}")
        except:
            logging.error("Failed to upload FRU with password: admin")
            logging.warning("Trying to upload FRU with password: Password@123")
            password = "Password@123"
            fru_send_command = subprocess.run(f"IPMIVIEW64.exe -host={ip} -ini=WRFRU.INI -usr=admin -pwd={password}", shell=True, check=True)
            if fru_send_command.returncode == 0:
                logging.info(f"MB FRU for {usn} has been uploaded successfully with iRMC Password: {password}")
        
        if fru_send_command.returncode == 0:
            reboot_irmc(ip, password)

    except subprocess.CalledProcessError:
        logging.error(f"Failed to upload MB FRU into the unit {usn} with iRMC IP: {ip}")

def reboot_irmc(ip, password):
    try:
        socket.gethostbyname(ip)
        url = f"https://{ip}/redfish/v1/Managers/iRMC/Actions/Manager.Reset"
        auth = ('admin', password)
        response = requests.post(url, auth=auth, verify=False)
        logging.info(f"(RESET)Status CODE: {response.status_code}")
        logging.info(f"Password: {password}")
        if response.status_code <300:
            logging.info("iRMC restarts. Wait until it reboots and check the MB SN")
        else:
            logging.info(f"irmc reset failed - code:{response.status_code}")
        logging.info("END")
        
    except socket.error:
        logging.error(f"IP address {ip} is not available")


def is_server_available(host):
    try:
        port = 80
        socket.create_connection((host, port))
        return True
    except OSError:
        return False
    
def find_password(ip):
    
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
    
    
    return password

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
        
    # print(f"Model: {model}")
    # print(f"Rada: {rada_serveru}")
    # print(f"Heslo pro tento model: {password}")
    
    url = f"https://{ip}/redfish/v1/Systems/0"
    auth = ('admin', password)
    response = requests.get(url, auth=auth, verify=False)
    power_status = response.json()['PowerState']
    # print(f"PowerStatus: {power_status}")

    return power_status, password

def reboot_system(irmc_ip):
    try:
        pwr_status, password = check_power_status(irmc_ip)
    
        if pwr_status == "Off":
            url = f'https://{irmc_ip}/redfish/v1/Systems/0/Actions/Oem/FTSComputerSystem.Reset'
            auth = ('admin', password)
            data = {"FTSResetType": "PowerOn"}
            requests.post(url, json=data, verify=False, auth=auth)
            print("\n### The unit is switched off. Switching on the unit.. ###\n")
        elif pwr_status == "On":
            url = f'https://{irmc_ip}/redfish/v1/Systems/0/Actions/Oem/FTSComputerSystem.Reset'
            auth = ('admin', password)
            data = {"FTSResetType": "PowerCycle"}
            requests.post(url, json=data, verify=False, auth=auth)
            print("\n### Rebooting the unit.. ###\n")
    except:
        print("ERROR: Connection to iRMC failed. Please check it.")
        
        
def saveUUID(ip,password):
    try:
        url = f"https://{ip}/redfish/v1/Systems/0"
        auth = ('admin', password)
        response = requests.get(url, auth=auth, verify=False)
        unit_uuid = response.json()['UUID']

        file = open('UUIDdata.txt', 'w')
        file.write(unit_uuid)
        file.close()
        return unit_uuid
    except:
        return False


def update_irmc_firmware(irmc, password, irmcfile):
    user = "admin"
    session = requests.Session()
    session.verify = False

    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json'}
    payload = {'UserName': user, 'Password': password}
    sessions_url = "https://{}/redfish/v1/SessionService/Sessions".format(irmc)
    response = session.post(
        sessions_url,
        headers=headers,
        auth=(user, password),
        data=json.dumps(payload)
    )

    if response.status_code != 201:
        print("ERROR: Could not establish a session to the iRMC")
        sys.exit()
    session.headers.update({"X-Auth-Token": response.headers["X-Auth-Token"]})
    session_info = response.headers["Location"]

    systems_response = session.get(
        "https://{}/redfish/v1/Systems/0".format(irmc))
    power_state = systems_response.json()['PowerState']

    irmc_update_url = "https://{}/redfish/v1/Managers/iRMC/Actions/Oem/FTSManager.FWUpdate".format(
        irmc)
    payload = {'data': open(irmcfile, 'rb')}
    response = session.post(
        irmc_update_url,
        files=payload
    )
    status_code = response.status_code
    if status_code != 200 and status_code != 202 and status_code != 204:
        print("ERROR: The iRMC Update POST request failed (url: {0}, error: {1})".format(
            irmc_update_url, response.json()['error']['message']))
        sys.exit()

    task_url = "https://{0}{1}".format(irmc, response.headers['Location'])
    while True:
        try:
            response = session.get(task_url)
            response_data = response.json()
            state = response_data['TaskState']
            progress = response_data['Oem']['ts_fujitsu']['TotalProgressPercent']

            if state == "Completed":
                if power_state == "On":
                    print("iRMC Update has been completed successfully. Please reboot the iRMC.")
                else:
                    print("iRMC Update has been completed successfully.")
                break
            else:
                print("Progress: {}%".format(progress))
            # check the task status every 10 seconds
            time.sleep(10)
        except Exception as e:
            # If the system is powered off and the current FW is the same as the update file or iRMC Update is completed,
            # iRMC will reboot, so the connection will be disconnected, and that generate an exception.
            if progress == 100:
                print("iRMC Update has been completed successfully, and iRMC will reboot automatically.")
            else:
                print("ERROR: An exception is thrown. Check the network connection to iRMC, or the iRMC status as iRMC may be being rebooted.")
                print("Exception: {}".format(e))
            sys.exit()

    session.delete("https://{0}{1}".format(irmc, session_info))
    
def check_file_type(filename):
    
    allowed_extensions = {'BIN', 'bin_enc', 'ima', 'ima_enc', 'bin'}    
    file_extension = filename.split('.')[-1]
    
    return file_extension in allowed_extensions

def get_newest_file():
  dirpath= os.path.join(os.path.expanduser('~'), 'Downloads')
  files = os.listdir(dirpath)

  if not files:
    return None

  newest_file = None
  newest_file_time = None

  for file in files:
    file_path = os.path.join(dirpath, file)
    file_time = os.path.getmtime(file_path)

    if not newest_file_time or file_time > newest_file_time:
      newest_file = file
      newest_file_time = file_time



  
  newest_file_path = os.path.join(dirpath, newest_file)
  return newest_file_path, newest_file

def power_off(irmc_ip):
    try:
        pwr_status, password = check_power_status(irmc_ip)
    
        if pwr_status == "Off":
            print("\n### The unit is already switched off ###\n")
        elif pwr_status == "On":
            url = f'https://{irmc_ip}/redfish/v1/Systems/0/Actions/Oem/FTSComputerSystem.Reset'
            auth = ('admin', password)
            data = {"FTSResetType": "PowerOff"}
            response = requests.post(url, json=data, verify=False, auth=auth)
            print("\n### Turning off the unit.. ###\n")
    except:
        print("ERROR: Connection to iRMC failed. Please check it.")