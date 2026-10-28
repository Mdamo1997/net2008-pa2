#Matthew D'Amour 040964438
import xml.etree.ElementTree as ET
import json

class Device:
     """Parent class for devices"""
     def __init__(self, device_id, device_role, os_version):
            """Device class constructor"""
            self.id = device_id
            self.role = device_role
            self.os = os_version
            self.owner = None
            self.interfaces = {}
            
def parse_inventory(file_xml):
    """Parses xml file and extracts root element"""
    #parse file
    parsed_file = ET.parse(file_xml)
    #assign root element and site name
    root_element = parsed_file.getroot()
    site_name = root_element.get("site")
    return root_element, site_name

def create_objects(root_element):
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
          
def count_data(device_objects):
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

def generate_report(count_data, site_name):
     """Creates audit.json report"""
     report_data ={
          "site": site_name,
          "total_devices": count_data["total_devices"],
          "skipped_devices": count_data["skipped_devices"],
          "roles": count_data["roles"],
          "interfaces": count_data["interfaces"],
          "violations": [],
          "compliant": []
     }
     with open("audit.json", "w") as file:
          json.dump(report_data, file, indent=4)
 
def main():
    """Main pa2.py script function"""
    root, site = parse_inventory("PA2_sample1.xml")
    objects = create_objects(root)
    count = count_data(objects)
    generate_report(count, site)

if __name__ == "__main__":
     main()