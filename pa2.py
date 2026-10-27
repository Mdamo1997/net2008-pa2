#Matthew D'Amour 040964438
import xml.etree.ElementTree as ET

class Device:
     """Parent class for devices"""
     def __init__(self, device_id, device_role, os_version):
            """Device class constructor"""
            self.id = device_id
            self.role = device_role
            self.os = os_version
            self.interfaces = []

def parse_inventory(file_xml):
    """"""
    skipped_devices = 0
    total_devices = 0
    device_roles_count = {}
    int_status_count = {"up": 0, "down": 0, "other": 0}

    parsed_file = ET.parse(file_xml)
    root_element = parsed_file.getroot()
    device_list = root_element.findall("device")
    for device in device_list:
         if device.get("id") is None:
              skipped_devices += 1
              continue
         total_devices += 1
         role = device.get("role")
         if role in device_roles_count:
              device_roles_count[role] += 1
         else:
              device_roles_count[role] = 1
            
         interface_list = device.findall("interface")
         for interface in interface_list:
              status = interface.get("status")
              if status != "up" and status != "down":
                   int_status_count["other"] += 1
              else:
                   int_status_count[interface.get("status")] += 1
              
    print (int_status_count)


def main():
    """Main pa2.py script function"""
    parse_inventory("PA2_sample1.xml")

    pass

if __name__ == "__main__":
     main()