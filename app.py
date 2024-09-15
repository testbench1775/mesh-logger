import sqlite3
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, jsonify, request
import pytz
from config_init import initialize_config
import argparse 

app = Flask(__name__)
application = app  # For Elastic Beanstalk deployment

db_path = './nodeData.db'  # Replace with your actual database path      

args = argparse.Namespace()
args.config = None

config_file = None
if args.config is not None:
    config_file = args.config

system_config = initialize_config(config_file)

# Route to serve the HTML template
@app.route('/')
def index():
    return render_template('index.html')  # Ensure index.html is in the 'templates' folder

# Route to serve the HTML template
@app.route('/sidebar')
def sidebar():
    return render_template('sidebar.html')  # Ensure index.html is in the 'templates' folder

# Route to provide telemetry data as JSON
@app.route('/get-telemetry-data', methods=['GET'])
def get_telemetry_data():
    conn = sqlite3.connect(db_path)  # Replace with your actual database path
    cursor = conn.cursor()

    # Query to get the most recent non-null values for each field per sender_node_id
    query = '''
        SELECT
            td.sender_node_id,
            MAX(td.sender_short_name) AS sender_short_name,
            MAX(td.timestamp) AS timestamp,
            (SELECT temperature FROM TelemetryData WHERE temperature IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS temperature,
            (SELECT humidity FROM TelemetryData WHERE humidity IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS humidity,
            (SELECT pressure FROM TelemetryData WHERE pressure IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS pressure,
            (SELECT battery_level FROM TelemetryData WHERE battery_level IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS battery_level,
            (SELECT voltage FROM TelemetryData WHERE voltage IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS voltage,
            (SELECT uptime_seconds FROM TelemetryData WHERE uptime_seconds IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS uptime_seconds,
            (SELECT latitude FROM TelemetryData WHERE latitude IS NOT NULL AND latitude != 0 AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS latitude,
            (SELECT longitude FROM TelemetryData WHERE longitude IS NOT NULL AND longitude != 0 AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS longitude,
            (SELECT altitude FROM TelemetryData WHERE altitude IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS altitude,
            (SELECT sats_in_view FROM TelemetryData WHERE sats_in_view IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS sats_in_view,
            (SELECT snr FROM TelemetryData WHERE snr IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS snr,
            (SELECT hardware_model FROM TelemetryData WHERE hardware_model IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS hardware_model,
            (SELECT sender_long_name FROM TelemetryData WHERE sender_long_name IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS sender_long_name,
            (SELECT role FROM TelemetryData WHERE role IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS role,
            (SELECT miles_to_base FROM TelemetryData WHERE miles_to_base IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS miles_to_base,
            (SELECT mqtt FROM TelemetryData WHERE mqtt IS NOT NULL AND sender_node_id = td.sender_node_id ORDER BY id DESC LIMIT 1) AS mqtt
        FROM TelemetryData td
        GROUP BY td.sender_node_id;
    '''
    
    cursor.execute(query)
    data = cursor.fetchall()

    telemetry_data = []
    timezone_ = pytz.timezone('America/Denver')
    # timezone_ = pytz.timezone(system_config['timezone'])
    current_time = datetime.now(timezone.utc).astimezone(timezone_)

    for row in data:
        # Convert the row[2] timestamp to a datetime object (assuming it's a string, format it accordingly)
        timestamp = datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).astimezone(timezone_)

        # Calculate the difference
        time_difference = current_time - timestamp
        days = time_difference.days
        hours = time_difference.seconds // 3600  # Convert remaining seconds to hours
        minutes = (time_difference.seconds % 3600) // 60  # Convert remaining seconds to minutes
        seconds = time_difference.seconds % 60

        # Generate the last_seen string
        if minutes == 0 and hours == 0 and days == 0:
            last_seen = f"{seconds} seconds"
        elif hours == 0 and days == 0:
            last_seen = f"{minutes} min {seconds} sec"
        elif days == 0:
            last_seen = f"{hours} hours {minutes} min"
        elif days < 2:
            last_seen = f"{days} days {hours} hours"
        else:
            last_seen = f"{days} days"  # Remove hours for days >= 2

        # Process 'uptime_seconds'
        uptime_seconds = int(row[8]) if row[8] is not None else 0
        uptime_timedelta = timedelta(seconds=uptime_seconds)
        uptime_days = uptime_timedelta.days
        uptime_hours, remainder = divmod(uptime_timedelta.seconds, 3600)
        uptime_minutes, uptime_seconds = divmod(remainder, 60)

        # Generate the 'uptime' string
        if uptime_minutes == 0 and uptime_hours == 0 and uptime_days == 0:
            uptime = f"{uptime_seconds} seconds"
        elif uptime_hours == 0 and uptime_days == 0:
            uptime = f"{uptime_minutes} min {uptime_seconds} sec"
        elif uptime_days == 0:
            uptime = f"{uptime_hours} hours {uptime_minutes} min"
        elif uptime_days < 2:
            uptime = f"{uptime_days} day {uptime_hours} hours"
        else:
            uptime = f"{uptime_days} days"

        telemetry_data.append({
            "sender_node_id": row[0],
            "sender_short_name": row[1],  # Check if this value exists in your DB
            "timestamp": row[2],
            "temperature": row[3],
            "humidity": row[4],
            "pressure": row[5],
            "battery_level": row[6],
            "voltage": row[7],
            "uptime_seconds": row[8],
            "latitude": row[9],
            "longitude": row[10],
            "altitude": row[11],
            "sats_in_view": row[12],
            "snr": row[13],
            "hardware_model": row[14],
            "sender_long_name": row[15],
            "role": row[16],
            "miles_to_base": row[17],
            "mqtt": row[18],
            "last_seen": last_seen,
            "uptime_string": uptime,
            "flask_path": system_config['flask_path']
        })

    # drop any rows without latitude
    telemetry_data = [row for row in telemetry_data if row['latitude'] is not None]

    # Change any null values to '---' and handle 'miles_to_base'
    for row in telemetry_data:
        # Replace None values with '---'
        for key, value in row.items():
            if value is None:
                row[key] = '---'
        # Handle 'miles_to_base' value
        miles = row.get('miles_to_base', '---')
        if miles == '---':
            row['miles_to_base'] = 9999.0  # Default value as float
        else:
            try:
                row['miles_to_base'] = float(miles)
            except ValueError:
                # Assign default value if conversion fails
                row['miles_to_base'] = 9999.0
        
    # Create two lists, one for nodes within 100 miles of Boise, and everything else
    close_nodes = [node for node in telemetry_data if int(node['miles_to_base']) < 100]
    far_nodes = [node for node in telemetry_data if int(node['miles_to_base']) >= 100]

    # Sort both lists based on miles_to_base
    close_nodes = sorted(close_nodes, key=lambda x: x['miles_to_base'])
    far_nodes = sorted(far_nodes, key=lambda x: x['miles_to_base'])

    conn.close()
    return jsonify({"close_nodes": close_nodes, "far_nodes": far_nodes})


@app.route('/sync', methods=['POST'])
def sync_db():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"error": "Expected a list of entries"}), 400

    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for entry in data:
        # Prepare the list of columns and their corresponding values
        columns = [
            'sender_node_id', 'sender_short_name', 'timestamp', 'temperature', 'humidity', 'pressure',
            'battery_level', 'voltage', 'uptime_seconds', 'latitude', 'longitude', 'altitude',
            'sats_in_view', 'snr', 'hardware_model', 'sender_long_name', 'role', 'mqtt', 'miles_to_base'
        ]
        values = [entry.get(col) for col in columns]

        try:
            # Try to update the existing record
            cursor.execute('''
                UPDATE TelemetryData SET
                    sender_short_name = ?,
                    timestamp = ?,
                    temperature = ?,
                    humidity = ?,
                    pressure = ?,
                    battery_level = ?,
                    voltage = ?,
                    uptime_seconds = ?,
                    latitude = ?,
                    longitude = ?,
                    altitude = ?,
                    sats_in_view = ?,
                    snr = ?,
                    hardware_model = ?,
                    sender_long_name = ?,
                    role = ?,
                    mqtt = ?,
                    miles_to_base = ?
                WHERE sender_node_id = ?
            ''', values[1:] + [entry['sender_node_id']])

            # If no rows were updated, insert a new record
            if cursor.rowcount == 0:
                cursor.execute('''
                    INSERT INTO TelemetryData (
                        sender_node_id, sender_short_name, timestamp, temperature, humidity, pressure,
                        battery_level, voltage, uptime_seconds, latitude, longitude, altitude,
                        sats_in_view, snr, hardware_model, sender_long_name, role, mqtt, miles_to_base
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', values)

        except Exception as e: 
            return jsonify({"message": e, "status": "failed"})

    conn.commit()
    conn.close()


    return jsonify({"message": "Data received and stored.", "status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
