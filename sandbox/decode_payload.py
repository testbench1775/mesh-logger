import struct

def decode_telemetry(payload_bytes, telemetry_type):
    # Based on telemetry type, we know what to expect in the payload.
    if telemetry_type == 'deviceMetrics':
        # Example: Decoding battery level, voltage, etc.
        # Assuming: batteryLevel (float), voltage (float), channelUtilization (float),
        # airUtilTx (float), uptimeSeconds (integer)
        decoded = struct.unpack('<f f f f I', payload_bytes[:20])
        telemetry_data = {
            'batteryLevel': round(decoded[0], 2),
            'voltage': round(decoded[1], 3),
            'channelUtilization': round(decoded[2], 2),
            'airUtilTx': round(decoded[3], 2),
            'uptimeSeconds': decoded[4]
        }
    elif telemetry_type == 'environmentMetrics':
        # Example: Decoding temperature, humidity, and pressure.
        # Assuming: temperature (float), relativeHumidity (float), barometricPressure (float)
        decoded = struct.unpack('<f f f f f', payload_bytes[:20])
        telemetry_data = {
            'temperature': round(decoded[2], 2),
            'relativeHumidity': round(decoded[1], 2),
            'barometricPressure': round(decoded[0], 2)
        }
    else:
        raise ValueError("Unknown telemetry type")

    return telemetry_data, decoded

# Example usage:
payload = b'\rF\xee\xeef\x1a\x0f\r\xf6(\xc8A\x15\x00d\xf3A\x1d|\x94fD'  # Example payload bytes
telemetry_type = 'environmentMetrics'  # Change to 'deviceMetrics' as necessary
# telemetry_type = 'deviceMetrics'  # Change to 'deviceMetrics' as necessary
telemetry_data, decoded_data = decode_telemetry(payload, telemetry_type)

# Displaying the decoded telemetry data
print(telemetry_data, '\n\n')
print(decoded_data)

