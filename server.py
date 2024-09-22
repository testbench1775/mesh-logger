import time
import logging
import threading
from pubsub import pub
from utils import display_banner
from event_processing import onReceive
from config_init import initialize_config, get_interface, init_cli_parser, merge_config
from db_operations import initialize_database, process_and_insert_telemetry_data, get_db_connection, sync_data_to_server, sync_database_periodically, sync_trend_periodically
import signal


if hasattr(signal, 'SIGPIPE'):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

# Use the variable in the logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(message)s',
    datefmt='%H:%M:%S'
)

def main():
    args = init_cli_parser()
    config_file = None
    if args.config is not None:
        config_file = args.config
    system_config = initialize_config(config_file)
    system_config['logger'] = logging.getLogger(__name__)

    log_level = getattr(logging, system_config['log_level'].upper(), logging.INFO)  # Convert string to logging level
    system_config['logger'].setLevel(logging.DEBUG)

    merge_config(system_config, args)

    interface = get_interface(system_config)

    host_node_num = interface.myInfo.my_node_num

    # if the base location is not set, use the base nodes location, otherwise, use boise as hard sp.
    if system_config['general']['location']['base_lat'] == 0.0 or system_config['general']['location']['base_lon'] == 0.0:
        system_config['general']['location']['latitude'] = interface.nodesByNum[host_node_num]['position']['latitude']
        system_config['general']['location']['longitude'] = interface.nodesByNum[host_node_num]['position']['longitude']

    # Start the database connection here so we can close it on KeyboardInterrupt
    system_config['conn'] = get_db_connection()

    initialize_database(system_config)

    # Prime the database with data contained in the interface
    process_and_insert_telemetry_data(system_config, interface)

    display_banner()

    system_config['logger'].info(f"Testbench Mesh Logger is running on {system_config['interface_type']} interface...")
    system_config['logger'].info(f"Connected to {system_config['hostname']}\n")


    def receive_packet_(packet, interface):
        onReceive(system_config, packet, interface)

    def onConnection_():  # supposed to be called when connecting ¯\_(ツ)_/¯
        system_config['logger'].info(f"Connected to the radio!")

    pub.subscribe(receive_packet_, "meshtastic.receive")
    pub.subscribe(onConnection_, "meshtastic.connection.established")

    # Start the database sync in a separate thread
    sync_thread = threading.Thread(target=sync_database_periodically, args=(system_config, 300))  # sync every 5 minutes
    sync_thread.daemon = True
    sync_thread.start()

    # Start the database trending in a separate thread
    trend_thread = threading.Thread(target=sync_trend_periodically, args=(system_config, 60))  # sync every 1 minutes
    trend_thread.daemon = True
    trend_thread.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        sync_data_to_server(system_config)
        system_config['logger'].info("Shutting down the server and DB...")

        system_config['conn'].close()
        interface.close()

if __name__ == "__main__":
    main()