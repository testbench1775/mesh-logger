import argparse
import meshtastic.tcp_interface
import sys

try:
    mesh_interface = meshtastic.tcp_interface.TCPInterface(hostname='192.168.1.151')
except Exception as e:
    print(f"Error connecting to the mesh interface: {e}")
    sys.exit(1)

def list_functions():
    functions = {
        "1": ("Show Nodes", mesh_interface.showNodes),
        "2": ("Send Text", mesh_interface.sendText),
        "3": ("Send Position", mesh_interface.sendPosition),
        "4": ("Send Trace Route", mesh_interface.sendTraceRoute),
        "5": ("Send Telemetry", mesh_interface.sendTelemetry)
    }
    return functions

def show_menu():
    print("Select a function to run:")
    functions = list_functions()
    for key, (description, _) in functions.items():
        print(f"{key}. {description}")
    return functions

def execute_function(choice, functions):
    func_name, func = functions[choice]
    try:
        if func_name == "Show Nodes":
            print(func())
        elif func_name == "Send Text":
            text = input("Enter the text to send: ")
            destination = input("Enter the destination ID (or leave blank for broadcast): ") or None
            wantAck = input("Want acknowledgment? (y/n): ").lower() == 'y'
            func(text, destination, wantAck)
        elif func_name == "Send Position":
            lat = float(input("Enter latitude: "))
            lon = float(input("Enter longitude: "))
            alt = int(input("Enter altitude: "))
            func(lat, lon, alt)
        elif func_name == "Send Trace Route":
            dest = input("Enter destination ID: ")
            hop_limit = int(input("Enter hop limit: "))
            func(dest, hop_limit)
        elif func_name == "Send Telemetry":
            func()
    except ValueError as ve:
        print(f"Input error: {ve}. Please enter the correct type of values.")4
        
    except Exception as e:
        print(f"An error occurred while executing the function: {e}")

def main():
    parser = argparse.ArgumentParser(description="MeshInterface CLI")
    args = parser.parse_args()

    while True:
        functions = show_menu()
        choice = input("Enter the number of the function to run (or 'q' to quit): ").strip()
        if choice == 'q':
            break
        elif choice in functions:
            try:
                execute_function(choice, functions)
            except Exception as e:
                print(f"Error executing the selected function: {e}")
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
