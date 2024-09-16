from utils import get_node_names, format_real_number
from db_operations import insert_telemetry_data
from datetime import datetime, timezone
import traceback

def on_receive(system_config, packet, interface):
    logger = system_config['logger']
    decoded_packet = packet.get('decoded', {})

    if decoded_packet:
        portnum = decoded_packet.get('portnum')
        sender_node_id = packet.get('fromId', None)
        to_node_id = packet.get('toId', None)
        sender_short_name, sender_long_name = get_node_names(interface, sender_node_id)
        to_short_name, to_long_name = get_node_names(interface, to_node_id)
        rx_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        message = decoded_packet.get('text')

        telemetry_data = decoded_packet.get('telemetry', {})
        temperature = format_real_number(telemetry_data.get('environmentMetrics', {}).get('temperature', None))
        humidity = format_real_number(telemetry_data.get('environmentMetrics', {}).get('relativeHumidity', None)) 
        pressure = format_real_number(telemetry_data.get('environmentMetrics', {}).get('barometricPressure', None))
        battery = format_real_number(telemetry_data.get('deviceMetrics', {}).get('batteryLevel', None))
        voltage = format_real_number(telemetry_data.get('deviceMetrics', {}).get('voltage', None))
        uptime = format_real_number(telemetry_data.get('deviceMetrics', {}).get('uptimeSeconds', None))

        location_data = decoded_packet.get('position', {})
        latitude = format_real_number(location_data.get('latitude', None), precision=7)
        longitude = format_real_number(location_data.get('longitude', None), precision=7)
        altitude = format_real_number(location_data.get('altitude', None))
        sats_in_view=format_real_number(location_data.get('satsInView', None))

        user_data = decoded_packet.get('user', {})
        snr = format_real_number(packet.get('rxSnr', None))
        hardware_model = user_data.get('hwModel', None)
        mac_address = user_data.get('macaddr', None)
        role = user_data.get('role', 'CLIENT')
        viaMqtt = packet.get('viaMqtt', False)
        publicKey = packet.get('publicKey', None)

        insert_telemetry_data(system_config, sender_node_id, timestamp=rx_time, sender_short_name=sender_short_name, to_node_id=to_node_id, temperature=temperature, humidity=humidity, pressure=pressure, battery_level=battery, voltage=voltage, uptime_seconds=uptime, latitude=latitude, longitude=longitude, altitude=altitude, sats_in_view=sats_in_view, neighbor_node_id=None, snr=snr, hardware_model=hardware_model, mac_address=mac_address, sender_long_name=sender_long_name, role=role, dst_to_bs=None, viaMqtt=viaMqtt, publicKey=publicKey)

        system_config['logger'].debug(f"rxPacket: {sender_short_name} to {to_short_name} at {rx_time}")
        system_config['logger'].info(f"-------------------------------------------------------- {portnum} ")

        # Handle TEXT_MESSAGE_APP
        if portnum == 'TEXT_MESSAGE_APP':
            try:
                # log_text_to_file(packet, './logs/TEXT_MESSAGE_APP.txt')
                system_config['logger'].info(f"{sender_long_name} ({sender_short_name}) sent a message to {to_long_name} ({to_short_name})")
                system_config['logger'].info(f"--- Message: \n\n{message}\n")
                system_config['logger'].info(f"--------------------------------------------------------")
                # insert_telemetry_data(system_config, sender_node_id=sender_node_id, timestamp=rx_time, to_node_id=to_node_id, sender_short_name=sender_short_name, sender_long_name=sender_long_name, snr=snr, viaMqtt=viaMqtt)
            
            except Exception as e:
                system_config['logger'].error(f"Error processing TEXT_MESSAGE_APP: {e}")
                system_config['logger'].debug(traceback.format_exc())

        # Handle TELEMETRY_APP
        elif portnum == 'TELEMETRY_APP':
            try:
                # log_text_to_file(packet, './logs/TELEMETRY_APP.txt')
                # insert_telemetry_data(system_config, sender_node_id=sender_node_id, timestamp=rx_time, to_node_id=to_node_id, sender_short_name=sender_short_name, sender_long_name=sender_long_name, temperature=temperature, humidity=humidity, pressure=pressure, battery_level=battery, voltage=voltage, uptime_seconds=uptime, viaMqtt=viaMqtt)
                pass
            except Exception as e:
                system_config['logger'].error(f"Error processing TELEMETRY_APP: {e}")
                system_config['logger'].debug(traceback.format_exc())

        # # Handle POSITION_APP
        elif portnum == 'POSITION_APP':
            try:
                # log_text_to_file(packet, './logs/POSITION_APP.txt')
                # insert_telemetry_data(system_config, sender_node_id=sender_node_id, timestamp=rx_time, to_node_id=to_node_id, sender_short_name=sender_short_name, sender_long_name=sender_long_name, latitude=latitude, longitude=longitude, altitude=altitude, viaMqtt=viaMqtt)
                pass
            except Exception as e:
                system_config['logger'].error(f"Error processing POSITION_APP: {e}")
                system_config['logger'].debug(traceback.format_exc())

        # Handle NEIGHBORINFO_APP
        elif portnum == 'NEIGHBORINFO_APP':
            try:
                # log_text_to_file(packet, './logs/NEIGHBORINFO_APP.txt')
                pass
            except Exception as e:
                system_config['logger'].info(f"Error processing NEIGHBORINFO_APP: {e}")
                system_config['logger'].debug(traceback.format_exc())
                

        # Handle WAYPOINT_APP
        elif portnum == 'WAYPOINT_APP':
            try:
                # log_text_to_file(packet, './logs/WAYPOINT_APP.txt')
                pass
            except Exception as e:
                system_config['logger'].info(f"Error processing WAYPOINT_APP: {e}")
                system_config['logger'].debug(traceback.format_exc())

        # Handle ROUTING_APP
        elif portnum == 'ROUTING_APP':
            try:
                # log_text_to_file(packet, './logs/ROUTING_APP.txt')
                pass
            except Exception as e:
                system_config['logger'].info(f"Error processing ROUTING_APP: {e}")
                system_config['logger'].debug(traceback.format_exc())

        # Handle NODEINFO_APP
        elif portnum == 'NODEINFO_APP':
            try:
                # log_text_to_file(packet, './logs/NODEINFO_APP.txt')
                # insert_telemetry_data(system_config, sender_node_id=sender_node_id, timestamp=rx_time, to_node_id=to_node_id, sender_short_name=sender_short_name, sender_long_name=sender_long_name, mac_address=mac_address, hardware_model=hardware_model, role=role, viaMqtt=viaMqtt)
                pass
            except Exception as e:
                system_config['logger'].error(f"Error processing NODEINFO_APP: {e}")
                system_config['logger'].debug(traceback.format_exc())