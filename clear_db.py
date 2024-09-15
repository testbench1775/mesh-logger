import sqlite3

def get_db_connection(db_file='nodeData.db'):
    return sqlite3.connect(db_file)

def clear_telemetry_data(conn):
    conn.execute('DELETE FROM TelemetryData')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    conn = get_db_connection()
    clear_telemetry_data(conn)