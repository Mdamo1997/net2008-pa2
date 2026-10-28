#Matthew D'Amour 040964438
import xml.etree.ElementTree as ET
import json
import yaml

class Device:
     """Parent class for devices"""
     def __init__(self, device_id, device_role, os_version):
            """Device class constructor"""
            self.id = device_id
            self.role = device_role
            self.os = os_version
            self.owner = None
            self.interfaces = {}

class InventoryInputError(Exception):
     """Custom exception that handles invalid XML file input"""
     pass

class PolicyInputError(Exception):
     """Custom exception that handles invalid YAML file input"""
     pass
            
def parse_inventory(file_xml): #tier1
    """Parses xml inventory file and extracts root element"""
    #parse file
    parsed_file = ET.parse(file_xml)
    #assign root element and site name
    root_element = parsed_file.getroot()
    site_name = root_element.get("site")
    return root_element, site_name
 
def create_objects(root_element): #tier1
     """Creates a list of device objects from a root element"""
     device_objects = []
     device_list = root_element.findall("device")
     for device in device_list:
          id = device.get("id")
          role = device.get("role")
          version = device.get("os")
          new_device = Device(id, role, version)

          new_device.owner = device.findtext("owner")

          interface_list = device.findall("interface")
          for int in interface_list:
               name = int.get("name")
               status = int.get("status")
               new_device.interfaces[name] = status

          device_objects.append(new_device)
     return device_objects     
          
def count_data(device_objects): #tier1
     """Counts data inside a list of device objects"""
     #counters
     skipped_devices = 0
     total_devices = 0
     role_count = {}
     int_status_count = {"up": 0, "down": 0, "other": 0}
     #loops through device objects
     for device in device_objects: 
          #counts valid and invalid device id's
          if device.id is None:
               skipped_devices +=1
               continue
          else:
               total_devices +=1
          #counts device roles
          if device.role in role_count:
               role_count[device.role] +=1 
          else:
               role_count[device.role] = 1
          #counts interface status
          for status in device.interfaces.values():
               if status != "up" and status != "down":
                    int_status_count["other"] +=1 
               else:
                    int_status_count[status] += 1
     #create dict of object list data 
     object_list_data = {"skipped_devices": skipped_devices, "total_devices": total_devices,"roles": role_count,
                          "interfaces": int_status_count}
     return object_list_data

def generate_report(count_data, violations, compliant, site_name): #tier1
     """Creates audit.json report"""
     report_data ={
          "site": site_name,
          "total_devices": count_data["total_devices"],
          "skipped_devices": count_data["skipped_devices"],
          "roles": count_data["roles"],
          "interfaces": count_data["interfaces"],
          "violations": violations,
          "compliant": compliant
     }
     with open("audit.json", "w") as file:
          json.dump(report_data, file, indent=4)

def parse_policy(file_yaml): #tier2
     """Parses yaml policy file"""
     with open(file_yaml, "r") as file:
          policy_info = yaml.safe_load(file)
     return policy_info

def check_policy(device_objects, policy_info): #tier2
     """Compares a list of device objects to specified policy requirements"""
     violations = []
     compliant = []
     for device in device_objects:
          if device.id is None:
               continue
          role_check = check_role(device, policy_info)
          owner_check = check_owner(device, policy_info)
          int_check = check_interfaces(device, policy_info)
          if role_check is not None:
               violations.append(role_check)
          if owner_check is not None:
               violations.append(owner_check)
          if int_check is not None:
               violations.append(int_check)
          if role_check is None and owner_check is None and int_check is None:
               compliant.append(device.id)
     compliant.sort()
     return violations, compliant
          
def check_role(device, policy_info): #tier2
     """Checks if role in device object is valid according to YAML policy"""
     #ensures min_os is in the policy
     if "min_os" not in policy_info:
          return None
     if device.role not in policy_info["min_os"]:
          unknown_role = {"device": device.id, "type": "unknown_role", "role": device.role}
          return unknown_role
     return None

def check_owner(device, policy_info): #tier2
     """Checks if owner in device object is present and required by YAML policy"""
     #ensures owner requirement is specified in the policy
     if policy_info.get("require_owner") is not True:
          return None
     if device.owner is None or device.owner.strip() == "":
          missing_owner = {"device": device.id, "type": "missing_owner"}
          return missing_owner
     return None

def check_interfaces(device, policy_info): #tier2
     """Checks status of device interfaces, counts number in down status and compares to maximum defined in policy"""
     down_count = 0
     if "max_down_interfaces" not in policy_info:
          return None
     for status in device.interfaces.values():
          if status == "down":
               down_count +=1
     if down_count > policy_info["max_down_interfaces"]:
          too_many_down = {"device": device.id, "type": "too_many_down", "down": down_count}
          return too_many_down
     return None
     
 
def main():
    """Main pa2.py script function"""
    root, site = parse_inventory("PA2_sample1.xml")
    objects = create_objects(root)
    count = count_data(objects)
    policy = parse_policy("PA2_policy.yaml")
    violations, compliant = check_policy(objects, policy)

    generate_report(count, violations, compliant, site)
    


if __name__ == "__main__":
     main()