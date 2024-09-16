import configparser
import time
from typing import Any
import meshtastic.stream_interface
import meshtastic.serial_interface
import meshtastic.tcp_interface
import serial.tools.list_ports
import argparse
import logging

def init_cli_parser() -> argparse.Namespace:
    """Function build the CLI parser and parses the arguments.

    Returns:
        argparse.ArgumentParser: Argparse namespace with processed CLI args
    """
    parser = argparse.ArgumentParser(description="Meshtastic Logging system")
    
    parser.add_argument(
        "--config", "-c", 
        action="store",
        help="System configuration file (None)",
        default=None)
    
    parser.add_argument(
        "--interface-type", "-i",
        action="store",
        choices=['serial', 'tcp'],
        help="Node interface type (None)",
        default=None)
    
    parser.add_argument(
        "--port", "-p",
        action="store",
        help="Serial port (None)",
        default=None)
    
    parser.add_argument(
        "--host", 
        action="store",
        help="TCP host address (None)",
        default=None)
    
    parser.add_argument(
        "--mqtt-topic", '-t', 
        action="store",
        help="MQTT topic to subscribe (meshtastic.receive)",
        default='meshtastic.receive')
    
    parser.add_argument(
        "--timezone", '-z', 
        action="store",
        help="Timezone for the system (UTC)",
        default='UTC')
    
    parser.add_argument(
        "--log-level", '-l', 
        action="store",
        help="Logging level for the system (INFO)| DEBUG, INFO, WARNING, ERROR, CRITICAL",
        default='INFO')
    
    parser.add_argument(
        "--db-file", '-d', 
        action="store",
        help="Database file path (nodeData.db)",
        default=None)
    parser.add_argument(
        "--api-path", '-a', 
        action="store",
        help="API path for the server",
        default=None)
    #
    # Add extra arguments here
    #...
    
    args = parser.parse_args()
    
    return args
    
    
def merge_config(system_config:dict[str, Any], args:argparse.Namespace) -> dict[str, Any]:
    """Function merges configuration read from the config file and provided on the CLI.
    
    CLI arguments override values defined in the config file.
    system_config argument is mutated by the function.

    Args:
        system_config (dict[str, Any]): System config dict returned by initialize_config()
        args (argparse.Namespace): argparse namespace with parsed CLI args

    Returns:
        dict[str, Any]: system config dict with merged configurations
    """
    
    if args.interface_type is not None:
        system_config['interface_type'] = args.interface_type
        
    if args.port is not None:
        system_config['port'] = args.port
        
    if args.host is not None:
        system_config['hostname'] = args.host

    if args.timezone is not None:
        system_config['timezone'] = args.timezone

    if args.log_level is not None:
        system_config['log_level'] = args.log_level

    if args.db_file is not None:
        system_config['db_file'] = args.db_file

    if args.api_path is not None:
        system_config['api_path'] = args.api_path
    
    return system_config


def initialize_config(config_file: str = None) -> dict[str, Any]:
    """
    Function reads and parses system configuration file

    Returns a dict with the following entries:
    config - parsed config file
    interface_type - type of the active interface
    hostname - host name for TCP interface
    port - serial port name for serial interface
    bbs_nodes - list of peer nodes to sync with

    Args:
        config_file (str, optional): Path to config file. Function reads from './config.ini' if this arg is set to None. Defaults to None.

    Returns:
        dict: dict with system configuration, ad described above
    """
    config = configparser.ConfigParser()

    if config_file is None:
        config_file = "config.ini"
    config.read(config_file)

    # Get the values from the config file ['name of section'] ('name of key', 'default value')
    interface_type = config['interface']['type']
    hostname = config['interface'].get('hostname', None)
    port = config['interface'].get('port', None)
    timezone = config['timezone'].get('timezone', 'UTC')
    log_level = config['logging'].get('log_level', 'INFO').upper()
    db_file = config['database'].get('file', 'nodeData.db')
    api_path = config['API'].get('api_path', None)
    flask_path = config['flask'].get('path', '')
    base_location = { # defaults to Boise, ID
        'base_lat': float(config['general'].get('base_lat', 0.0)),
        'base_lon': float(config['general'].get('base_lon', 0.0))
    }
    base_radius = float(config['general'].get('radius', 100.0))


    # return dict with the configuration. This will be shared across the program.
    return {
        'config': config,
        'interface_type': interface_type,
        'hostname': hostname,
        'port': port,
        'timezone': timezone,
        'log_level': log_level,
        'conn': None,
        'logger': None,
        'db_file': db_file,
        'api_path': api_path,
        'flask_path': flask_path,
        'general': {
            'location': base_location,
            'radius': base_radius
        }
    }

def get_interface(system_config:dict[str, Any]) -> meshtastic.stream_interface.StreamInterface:
    """
    Function opens and returns an instance meshtastic interface of type specified by the configuration
    
    Function creates and returns an instance of a class inheriting from meshtastic.stream_interface.StreamInterface.
    The type of the class depends on the type of the interface specified by the system configuration.
    For 'serial' interfaces, function returns an instance of meshtastic.serial_interface.SerialInterface,
    and for 'tcp' interface, an instance of meshtastic.tcp_interface.TCPInterface.

    Args:
        system_config (dict[str, Any]): A dict with system configuration. See description of initialize_config() for details.

    Raises:
        ValueError: Exception raised in the following cases:
                - Type of interface not provided in the system config
                - Multiple serial ports present in the system, and no port specified in the configuration
                - Serial port interface requested, but no ports found in the system
                - Hostname not provided for TCP interface

    Returns:
        meshtastic.stream_interface.StreamInterface: An instance of StreamInterface
    """
    while True:
        try:
            if system_config['interface_type'] == 'serial':
                if system_config['port']:
                    return meshtastic.serial_interface.SerialInterface(system_config['port'])
                else:
                    ports = list(serial.tools.list_ports.comports())
                    if len(ports) == 1:
                        return meshtastic.serial_interface.SerialInterface(ports[0].device)
                    elif len(ports) > 1:
                        port_list = ', '.join([p.device for p in ports])
                        raise ValueError(f"Multiple serial ports detected: {port_list}. Specify one with the 'port' argument.")
                    else:
                        raise ValueError("No serial ports detected.")
            elif system_config['interface_type'] == 'tcp':
                if not system_config['hostname']:
                    raise ValueError("Hostname must be specified for TCP interface")
                return meshtastic.tcp_interface.TCPInterface(hostname=system_config['hostname'])
            else:
                raise ValueError("Invalid interface type specified in config file")
        except PermissionError as e:
            print(f"PermissionError: {e}. Retrying in 5 seconds...")
            time.sleep(5)
