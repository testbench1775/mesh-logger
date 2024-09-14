import logging
import sqlite3
import threading
import requests
from utils import log_text_to_file, haversine_distance


from meshtastic import BROADCAST_NUM

thread_local = threading.local()

def get_db_connection(db_file='nodeData.db'):
    try:
        if not hasattr(thread_local, 'connection'):
            thread_local.connection = sqlite3.connect(db_file, check_same_thread=False)
        return thread_local.connection
    except sqlite3.Error as e:
        logging.error(f"Error connecting to database: {e}")
        return None

def initialize_database(system_config):
    logger = system_config['logger']
    try:
        conn = system_config['conn']
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS TelemetryData (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL DEFAULT (datetime('now','localtime')),
                    sender_node_id TEXT NOT NULL UNIQUE,
                    to_node_id TEXT,
                    sender_long_name TEXT,
                    sender_short_name TEXT,
                    latitude REAL,
                    longitude REAL,
                    temperature REAL,
                    humidity REAL,
                    pressure REAL,
                    battery_level REAL,
                    voltage REAL,
                    uptime_seconds REAL,
                    altitude REAL,
                    sats_in_view REAL,
                    snr REAL,
                    role TEXT,
                    hardware_model TEXT,
                    mac_address TEXT,
                    neighbor_node_id TEXT,
                    miles_to_base REAL,
                    mqtt bool DEFAULT 0
                );
                ''')

        conn.commit()

        logger.info("Database initialized.")
    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {e}")


def insert_telemetry_data(system_config, sender_node_id, timestamp=None, sender_short_name=None, to_node_id=None, temperature=None, humidity=None,
                          pressure=None, battery_level=None, voltage=None, uptime_seconds=None, latitude=None, longitude=None, altitude=None, 
                          sats_in_view=None, neighbor_node_id=None, snr=None, hardware_model=None, mac_address=None, sender_long_name=None, 
                          role=None, dst_to_bs=None, viaMqtt=False, set_timestamp=True):
    logger = system_config['logger']

    try:
        conn = system_config['conn']

        # Ensure the connection is open
        if conn is None or conn.cursor() is None:
            logging.error("Cannot operate on a closed database.")
            return
        
        with conn:
            # create the initial row with the ID, then update what is not None
            conn.execute('''INSERT INTO TelemetryData (sender_node_id) VALUES (?) ON CONFLICT(sender_node_id) DO NOTHING''', (sender_node_id,))
            logger.info(f"Inserted data for {sender_long_name} ({sender_short_name}) [{sender_node_id}]")

            if sender_long_name:
                conn.execute('''UPDATE TelemetryData SET sender_long_name = ? WHERE sender_node_id = ?''', (sender_long_name, sender_node_id))
                logger.debug(f"--- Updated sender_long_name: {sender_long_name}")
            if sender_short_name:
                conn.execute('''UPDATE TelemetryData SET sender_short_name = ? WHERE sender_node_id = ?''', (sender_short_name, sender_node_id))
                logger.debug(f"--- Updated sender_short_name: {sender_short_name}")
            if to_node_id:
                conn.execute('''UPDATE TelemetryData SET to_node_id = ? WHERE sender_node_id = ?''', (to_node_id, sender_node_id))
                logger.debug(f"--- Updated to_node_id: {to_node_id}")
            if temperature:
                conn.execute('''UPDATE TelemetryData SET temperature = ? WHERE sender_node_id = ?''', (temperature, sender_node_id))
                logger.debug(f"--- Updated temperature: {temperature}")
            if humidity:
                conn.execute('''UPDATE TelemetryData SET humidity = ? WHERE sender_node_id = ?''', (humidity, sender_node_id))
                logger.debug(f"--- Updated humidity: {humidity}")
            if pressure:
                conn.execute('''UPDATE TelemetryData SET pressure = ? WHERE sender_node_id = ?''', (pressure, sender_node_id))
                logger.debug(f"--- Updated pressure: {pressure}")
            if battery_level:
                conn.execute('''UPDATE TelemetryData SET battery_level = ? WHERE sender_node_id = ?''', (battery_level, sender_node_id))
                logger.debug(f"--- Updated battery_level: {battery_level}")
            if voltage:
                conn.execute('''UPDATE TelemetryData SET voltage = ? WHERE sender_node_id = ?''', (voltage, sender_node_id))
                logger.debug(f"--- Updated voltage: {voltage}")
            if uptime_seconds:
                conn.execute('''UPDATE TelemetryData SET uptime_seconds = ? WHERE sender_node_id = ?''', (uptime_seconds, sender_node_id))
                logger.debug(f"--- Updated uptime_seconds: {uptime_seconds}")
            if latitude and longitude:
                conn.execute('''UPDATE TelemetryData SET latitude = ? WHERE sender_node_id = ?''', (latitude, sender_node_id))
                logger.debug(f"--- Updated latitude: {latitude}")
                conn.execute('''UPDATE TelemetryData SET longitude = ? WHERE sender_node_id = ?''', (longitude, sender_node_id))
                logger.debug(f"--- Updated longitude: {longitude}")
                # calculate distance to base station
                # These are for boise, ID. Maybe change to a variable later
                distance = haversine_distance(43.6008608,-116.2750972, latitude, longitude)
                conn.execute('''UPDATE TelemetryData SET miles_to_base = ? WHERE sender_node_id = ?''', (distance, sender_node_id))
                logger.debug(f"--- Updated miles_to_base: {distance}")
            if altitude:
                conn.execute('''UPDATE TelemetryData SET altitude = ? WHERE sender_node_id = ?''', (altitude, sender_node_id))
                logger.debug(f"--- Updated altitude: {altitude}")
            if sats_in_view:
                conn.execute('''UPDATE TelemetryData SET sats_in_view = ? WHERE sender_node_id = ?''', (sats_in_view, sender_node_id))
                logger.debug(f"--- Updated sats_in_view: {sats_in_view}")
            if neighbor_node_id:
                conn.execute('''UPDATE TelemetryData SET neighbor_node_id = ? WHERE sender_node_id = ?''', (neighbor_node_id, sender_node_id))
                logger.debug(f"--- Updated neighbor_node_id: {neighbor_node_id}")
            if snr:
                conn.execute('''UPDATE TelemetryData SET snr = ? WHERE sender_node_id = ?''', (snr, sender_node_id))
                logger.debug(f"--- Updated snr: {snr}")
            if hardware_model:
                conn.execute('''UPDATE TelemetryData SET hardware_model = ? WHERE sender_node_id = ?''', (hardware_model, sender_node_id))
                logger.debug(f"--- Updated hardware_model: {hardware_model}")
            if mac_address:
                conn.execute('''UPDATE TelemetryData SET mac_address = ? WHERE sender_node_id = ?''', (mac_address, sender_node_id))
                logger.debug(f"--- Updated mac_address: {mac_address}")
            if role:
                conn.execute('''UPDATE TelemetryData SET role = ? WHERE sender_node_id = ?''', (role, sender_node_id))
                logger.debug(f"--- Updated role: {role}")
            if dst_to_bs:
                conn.execute('''UPDATE TelemetryData SET miles_to_base = ? WHERE sender_node_id = ?''', (dst_to_bs, sender_node_id))
                logger.debug(f"--- Updated miles_to_base: {dst_to_bs}")
            if viaMqtt:
                conn.execute('''UPDATE TelemetryData SET mqtt = ? WHERE sender_node_id = ?''', (viaMqtt, sender_node_id))
                logger.debug(f"--- Updated mqtt: {viaMqtt}")
            if timestamp and set_timestamp:
                conn.execute('''UPDATE TelemetryData SET timestamp = ? WHERE sender_node_id = ?''', (timestamp, sender_node_id))
                logger.debug(f"--- Updated timestamp: {timestamp}")
            elif set_timestamp:
                conn.execute('''UPDATE TelemetryData 
                                SET timestamp = datetime('now','localtime') 
                                WHERE sender_node_id = ?;''', (sender_node_id,))
            

            logger.info(f"--------------------------------------------------------")

    except sqlite3.Error as e:
        logging.error(f"Error inserting or updating telemetry data: {e}")

def process_and_insert_telemetry_data(system_config, interface):
    logger = system_config['logger']

    try:
        conn = system_config['conn']

        # Ensure the connection is open
        if conn is None or conn.cursor() is None:
            logging.error("Cannot operate on a closed database.")
            return
        
        interface_values = interface.nodes.values()
        #  Disable logging for the loop
        logging.getLogger().setLevel(logging.CRITICAL + 1)

        log_text_to_file('', './logs/INTERFACE_DATA.txt', clear_first=True)

        for node in interface_values:
            # Directly access the user, position, and metrics dictionaries
            user_data = node.get('user', {})
            position_data = node.get('position', {})
            device_metrics = node.get('deviceMetrics', {})

            log_text_to_file(f'{user_data}\n{position_data}\n{device_metrics}', './logs/INTERFACE_DATA.txt')
            
            # Fetch the sender_node_id
            sender_node_id = user_data.get('id')

            # Check if sender_node_id exists and log the error if it is None
            if not sender_node_id:
                logging.error(f"Missing sender_node_id for node: {user_data}")
                continue  # Skip inserting data for this node if sender_node_id is missing

            # logger.info(f"Processing node: {sender_node_id}, position: {position_data}, metrics: {device_metrics}")
            
            insert_telemetry_data(
                conn,
                sender_node_id=sender_node_id,
                sender_short_name=user_data.get('shortName'),
                sender_long_name=user_data.get('longName'),
                mac_address=user_data.get('macaddr'),
                hardware_model=user_data.get('hwModel'),
                latitude=position_data.get('latitude'),
                longitude=position_data.get('longitude'),
                altitude=position_data.get('altitude'),
                sats_in_view=position_data.get('satsInView'),  # Note case sensitivity here
                battery_level=device_metrics.get('batteryLevel'),
                voltage=device_metrics.get('voltage'),
                uptime_seconds=device_metrics.get('uptimeSeconds'),
                snr=node.get('snr'),
                role=user_data.get('role'),
                set_timestamp=False
            )
        # Re-enable logging
        logging.getLogger().setLevel(logging.INFO)
        logger.info("Telemetry data processed and inserted.")

    except Exception as e:
        logging.error(f"Error processing and inserting telemetry data: {e}")

    finally:
        logging.getLogger().setLevel(logging.INFO)
        logger.info("Telemetry data processing complete.")

def sync_data_to_server(system_config):
    logger = system_config['logger']
    try:
        conn = system_config['conn']

        # Ensure the connection is open
        if conn is None or conn.cursor() is None:
            logging.error("Cannot operate on a closed database.")
            return
        
        if not system_config['api_path'] is not None:
            logging.error("DB Push to API Failed. No API path is not set in config file.")
            return
        
        # Connect to the offline database
        cursor = conn.cursor()

        # Fetch all data from the TelemetryData table
        cursor.execute("SELECT * FROM TelemetryData")
        rows = cursor.fetchall()

        # Dynamically get the column names from the database cursor description
        column_names = [description[0] for description in cursor.description]

        # Prepare data as a list of dictionaries
        data = [dict(zip(column_names, row)) for row in rows]

        # Debug logging to verify data structure
        logger.info(f"Database synced with {system_config['api_path']}")

        # Send the data to the server using a POST request
        response = requests.post(system_config['api_path'], json=data, headers={'Content-Type': 'application/json'})

        # Handle the server response
        if response.status_code == 200:
            logger.info("Data synced successfully: %s", response.json())
        else:
            logger.info("Failed to sync data: %d %s", response.status_code, response.text)

    except Exception as e:
        logger.info("An error occurred during data sync: %s", str(e))