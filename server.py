import time
import logging
import threading
from pubsub import pub
from utils import display_banner
from message_processing import on_receive
from config_init import initialize_config, get_interface, init_cli_parser, merge_config
from db_operations import initialize_database, process_and_insert_telemetry_data, get_db_connection, sync_data_to_server
import signal

if hasattr(signal, 'SIGPIPE'):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

# Use the variable in the logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(message)s',
    datefmt='%H:%M:%S'
)

def sync_database_periodically(system_config, interval=60):
    """
    This function will run in a separate thread to sync the database to the server periodically.
    """
    while True:
        time.sleep(interval)
        system_config['logger'].info("Syncing database to server...")
        sync_data_to_server(system_config)
        system_config['logger'].info("Database synced successfully.")

def main():
    args = init_cli_parser()
    config_file = None
    if args.config is not None:
        config_file = args.config
    system_config = initialize_config(config_file)
    system_config['logger'] = logging.getLogger(__name__)

    log_level = getattr(logging, system_config['log_level'].upper(), logging.INFO)  # Convert string to logging level
    system_config['logger'].setLevel(log_level)

    merge_config(system_config, args)

    interface = get_interface(system_config)

    # Start the database connection here so we can close it on KeyboardInterrupt
    system_config['conn'] = get_db_connection()

    initialize_database(system_config)

    # Prime the database with data contained in the interface
    process_and_insert_telemetry_data(system_config, interface)

    display_banner()
    system_config['logger'].info(f"Testbench Mesh Logger is running on {system_config['interface_type']} interface...")

    def receive_packet(packet, interface):
        on_receive(system_config, packet, interface)

    def onConnection(interface, topic=pub.AUTO_TOPIC):  # called when we (re)connect to the radio
        system_config['logger'].info(f"Connected to the radio!")
        pass

    pub.subscribe(receive_packet, system_config['mqtt_topic'])
    pub.subscribe(onConnection, "meshtastic.connection.established")

    # Start the database sync in a separate thread
    sync_thread = threading.Thread(target=sync_database_periodically, args=(system_config, 300))  # sync every 5 minutes
    sync_thread.daemon = True
    sync_thread.start()

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