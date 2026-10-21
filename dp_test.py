import keyring
from netmiko import ConnectHandler

#=========================
# KEYRING SETTINGS
#=========================

service_name = ""
username = ""
password = keyring.get_password(service_name, username)

if not password:
    raise ValueError(
        f"Password for {username} not found in keyring "
        f"under service name '{service_name}'"
    )

# =========================
# SWITCH SETTINGS
# =========================

SWITCH = {
    "device_type": "cisco_ios",
    "host": "",
    "username": username,
    "password": password,
}

#========================
# VARIABLES
#========================

connection = None
notconnect_interfaces = []
excluded_interfaces = []
ports_to_disable = []
IGNORE_PREFIXES = ("OR-", "NS-", "PX-", "SL-", "PVM-", "LENEL")
Week_Threshold = 26

print("Connecting to Switch...")
connection = ConnectHandler(**SWITCH)

show_interfaces = connection.send_command("show interface g1/0/2", use_textfsm=True)

#print(show_interfaces)

#=============================================
# Finding excluded ports by port description
#=============================================

print("\nFinding Excluded Interfaces Based on Description")
for interface in show_interfaces:
    if interface['description'].startswith(IGNORE_PREFIXES):
        excluded_interfaces.append(interface['interface'])

if excluded_interfaces == []:
    print("\nNo Interfaces Being Excluded Based on Description")
else:
    print(excluded_interfaces)

#==========================
# Finding notconnect ports
#==========================

print("\nFinding Notconnect Interfaces")
for interface in show_interfaces:
    if interface['interface'] in excluded_interfaces:
        continue
    else:
        if interface['protocol_status'] == 'down (notconnect)':
            notconnect_interfaces.append(interface['interface'])

if notconnect_interfaces == []:
    print("\nNo Interfaces to Disable")
    exit
else:
    print(f"\nList of Notconnect Interfaces: {notconnect_interfaces}")

#===========================
#Finding Last Time Port Used
#===========================
print("\nChecking Notconnect Interfaces Last Input and Output")
for interface in show_interfaces:
    if interface['interface'] not in notconnect_interfaces:
        continue
    else:
        if "w" in 'last_input':
            text = 'last_input'
            
            spaced_text = text.replace("w", " w ").replace("d", " d ")
            
            result_last_input = spaced_text.split()
            
            print(result_last_input)
        else:
            continue

        if "w" in 'last_output':
            text = 'last_output'
            
            spaced_text = text.replace("w", " w ").replace("d", " d ")
            
            result_last_output = spaced_text.split()
            
            print(result_last_output)
        else:
            continue

        if (interface['last_input'] == 'never' or interface[result_last_input[0]] >= Week_Threshold) and (interface['last_output'] == 'never' or interface[result_last_output[0]] >= Week_Threshold):
            ports_to_disable.append(interface['interface'])
        else:
            continue
if ports_to_disable == []:
    print("\nNo Interfaces to Disable")
else:
    print(f"\nList of Ports To Disable: {ports_to_disable}")














if connection:
        connection.disconnect()
        print("\nDisconnected from switch.")