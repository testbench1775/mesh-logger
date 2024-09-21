import argparse
import time
import meshtastic.tcp_interface
import sys
import traceback
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(message)s',
    datefmt='%H:%M:%S'
)

try:
    mesh_interface = meshtastic.tcp_interface.TCPInterface(hostname='192.168.1.151')
except Exception as e:
    logger.info(f"Error connecting to the mesh interface: {e}")
    sys.exit(1)

def list_functions():
    functions = {
        "1": ("Show Nodes", mesh_interface.showNodes),
        "2": ("Send Text", mesh_interface.sendText),
        "3": ("Send Position", mesh_interface.sendPosition),
        "4": ("Send Trace Route", mesh_interface.sendTraceRoute),
        "5": ("Send Telemetry", mesh_interface.sendTelemetry),
        "6": ("Request Node Config", request_node_config),
        "7": ("Reboot Node", reboot_node),
        "8": ("Show Channels", show_node_channels),
        "9": ("Set Fixed Position", set_fixed_position)
    }
    return functions

def show_menu():
    logger.info("\nSelect a function to run:")
    functions = list_functions()
    for key, (description, _) in functions.items():
        logger.info(f"{key}. {description}")
    return functions

def execute_function(choice, functions):
    func_name, func = functions[choice]
    try:
        if func_name == "Show Nodes":
            logger.info(func())
        elif func_name == "Send Text":
            text = input("Enter the text to send: ")
            destination = hex_to_decimal(input("Enter the destination ID (or leave blank for broadcast): ")) or None
            wantAck = input("Want acknowledgment? (y/n): ").lower() == 'y'
            func(text, destination, wantAck)
        elif func_name == "Send Position":
            lat = float(input("Enter latitude: "))
            lon = float(input("Enter longitude: "))
            alt = int(input("Enter altitude: "))
            func(lat, lon, alt)
        elif func_name == "Send Trace Route":
            dest = hex_to_decimal(input("Enter destination ID: "))
            hop_limit = int(input("Enter hop limit: "))
            try:
                func(dest, hop_limit)
            except meshtastic.mesh_interface.MeshInterface.MeshInterfaceError as mie:
                logger.info(f"Timed out waiting for traceroute: {mie}")
        elif func_name == "Send Telemetry":
            func()
        elif func_name == "Request Node Config":
            node_num = hex_to_decimal(input("Enter node number: "))
            config_type = input("Enter config type (e.g., device, power): ")
            request_node_config(node_num, config_type)
        elif func_name == "Reboot Node":
            node_num = hex_to_decimal(input("Enter node number: "))
            reboot_node(node_num)
        elif func_name == "Show Channels":
            node_num = hex_to_decimal(input("Enter node number: "))
            show_node_channels(node_num)
        elif func_name == "Set Fixed Position":
            node_num = hex_to_decimal(input("Enter node number: "))
            lat = float(input("Enter latitude: "))
            lon = float(input("Enter longitude: "))
            alt = int(input("Enter altitude: "))
            set_fixed_position(node_num, lat, lon, alt)
    except ValueError as ve:
        logger.info(f"Input error: {ve}. Please enter the correct type of values.")
        logger.info(traceback.format_exc())
    except Exception as e:
        logger.info(f"An error occurred while executing the function: {e}")
        logger.info(traceback.format_exc())

def request_node_config(node_num, config_type):
    try:
        node = mesh_interface.getNode(node_num)
        logger.info(f"Requesting {config_type} config for node {node_num}...")

        # Mapping config_type string to the appropriate index for each field
        config_index_map = {
            "device": 0,     # Index for device configuration
            "position": 1,   # Index for position configuration
            "power": 2,      # Index for power configuration
            "network": 3,    # Index for network configuration
            "display": 4,    # Index for display configuration
            "lora": 5,       # Index for LoRa configuration
            "bluetooth": 6,  # Index for Bluetooth configuration
            "security": 7    # Index for security configuration
        }

        if config_type in config_index_map:
            node.requestConfig(config_index_map[config_type])
            logger.info(f"Config request for {config_type} sent successfully.")
        else:
            logger.info(f"Invalid config type: {config_type}")
    except Exception as e:
        logger.info(f"Failed to request config for node {node_num}: {e}")
        logger.info(traceback.format_exc())


def reboot_node(node_num):
    try:
        node = mesh_interface.getNode(node_num)
        logger.info(f"Rebooting node {node_num}...")
        node.reboot()
        logger.info(f"Node {node_num} reboot command sent.")
    except Exception as e:
        logger.info(f"Failed to reboot node {node_num}: {e}")
        logger.info(traceback.format_exc())

def show_node_channels(node_num):
    try:
        node = mesh_interface.getNode(node_num)
        logger.info(f"Showing channels for node {node_num}:")
        node.showChannels()
    except Exception as e:
        logger.info(f"Failed to show channels for node {node_num}: {e}")
        logger.info(traceback.format_exc())

def set_fixed_position(node_num, lat, lon, alt):
    try:
        node = mesh_interface.getNode(node_num)
        logger.info(f"Setting fixed position for node {node_num}: Lat: {lat}, Lon: {lon}, Alt: {alt}")
        node.setFixedPosition(lat, lon, alt)
        logger.info(f"Fixed position set for node {node_num}.")
    except Exception as e:
        logger.info(f"Failed to set fixed position for node {node_num}: {e}")
        logger.info(traceback.format_exc())

def hex_to_decimal(value):
    if value.startswith('!'):
        # Remove '!' or other non-hexadecimal characters if present
        hex_value = value.lstrip('!')
        decimal_value = int(hex_value, 16)
    else:
        decimal_value = int(value)    
    
    return decimal_value


def main():
    parser = argparse.ArgumentParser(description="MeshInterface CLI")
    args = parser.parse_args()
    try:
        while True:
            functions = show_menu()
            choice = input("\nEnter the number of the function to run (or 'q' to quit): ").strip()
            if choice == 'q':
                break
            elif choice in functions:
                try:
                    execute_function(choice, functions)
                except Exception as e:
                    logger.info(f"Error executing the selected function: {e}")
            else:
                logger.info("Invalid choice. Please try again.")

            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("\nProgram interrupted. Exiting...")

if __name__ == "__main__":
    main()
