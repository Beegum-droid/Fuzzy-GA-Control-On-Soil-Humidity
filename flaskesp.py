import os
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from fuzzy_controller import compute_control_signal
from fuzzygacontroller import compute_control_signalga
from functools import wraps
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables for database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "esp32")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_db_connection():
    """Establish a connection to the database."""
    try:
        return psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection error: {e}")
        raise

def db_error_handler(func):
    """Decorator for handling database-related errors."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error: {e}")
            return jsonify({"status": "error", "message": "Database error occurred."}), 500
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return jsonify({"status": "error", "message": "An unexpected error occurred."}), 500
    return wrapper

def init_db():
    """Initialize the database with required tables."""
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS esp_data (
                    id SERIAL PRIMARY KEY,
                    humidity DOUBLE PRECISION NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS error (
                    id SERIAL PRIMARY KEY,
                    error DOUBLE PRECISION NOT NULL,
                    derror DOUBLE PRECISION NOT NULL,
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS espdata2 (
                    id SERIAL PRIMARY KEY,
                    humidity DOUBLE PRECISION NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS error2 (
                    id SERIAL PRIMARY KEY,
                    error DOUBLE PRECISION NOT NULL,
                    derror DOUBLE PRECISION NOT NULL,
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS uhistory (
                    id SERIAL PRIMARY KEY,
                    uhistory DOUBLE PRECISION NOT NULL,
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS uhistoryga (
                    id SERIAL PRIMARY KEY,
                    uhistory DOUBLE PRECISION NOT NULL,
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

@app.route('/')
def index():
    return jsonify({"message": "Server is running and ready to communicate with ESP!"})

@app.route('/send', methods=['POST'])
@db_error_handler
def receive_data():
    """Receive and store humidity data."""
    data = request.get_json()
    humidity = data.get('humidity')
    
    if humidity is None:
        return jsonify({"status": "error", "message": "Missing 'humidity' key in payload."}), 400

    try:
        humidity = float(humidity)
    except ValueError:
        return jsonify({"status": "error", "message": "'humidity' must be an integer."}), 400

    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO esp_data (humidity) VALUES (%s)", (humidity,))
        conn.commit()

    logger.info(f"Received and stored humidity: {humidity}")
    return jsonify({"status": "success", "message": "Data received and stored successfully."})

@app.route('/send2', methods=['POST'])
@db_error_handler
def receive_data2():
    """Receive and store humidity data."""
    data = request.get_json()
    humidity = data.get('humidity')
    
    if humidity is None:
        return jsonify({"status": "error", "message": "Missing 'humidity' key in payload."}), 400

    try:
        humidity = float(humidity)
    except ValueError:
        return jsonify({"status": "error", "message": "'humidity' must be an integer."}), 400

    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO espdata2 (humidity) VALUES (%s)", (humidity,))
        conn.commit()

    logger.info(f"Received and stored humidity: {humidity}")
    return jsonify({"status": "success", "message": "Data received and stored successfully."})

@app.route('/get', methods=['GET'])
@db_error_handler
def send_data():
    """Send the most recent humidity data."""
    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, humidity, created_at FROM esp_data ORDER BY created_at DESC LIMIT 1")
        latest_data = cur.fetchone()

    if latest_data:
        return jsonify(latest_data)
    return jsonify({"status": "error", "message": "No data available."}), 404

@app.route('/get_fuzzy', methods=['GET'])
@db_error_handler
def get_fuzzy():
    """Fetch error data, compute the control signal, and store it in the uhistory table."""
    # Fetch error data from the error table
    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT error, derror FROM error ORDER BY created DESC LIMIT 1")
        error_data = cur.fetchone()

    if not error_data:
        return jsonify({"status": "error", "message": "No error data available."}), 404

    error, derror = error_data['error'], error_data['derror']
    control_signal = compute_control_signal(error, derror)
    logger.info(f"Computed control signal: {control_signal} for error: {error}, derror: {derror}")

    # Store the control signal in the uhistory table.
    with get_db_connection() as conn, conn.cursor() as cur:
        # Assuming 'id' is auto-generated and 'created' will be set to the current timestamp via NOW()
        cur.execute(
            "INSERT INTO uhistory (uhistory) VALUES (%s)",
            (control_signal,)
        )
        conn.commit()

    return jsonify({"output": 0})


@app.route('/get_fuzzyga', methods=['GET'])
@db_error_handler
def get_fuzzyga():
    """Fetch error data and compute the control signal."""
    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT error, derror FROM error2 ORDER BY created DESC LIMIT 1")
        error_data = cur.fetchone()

    if not error_data:
        return jsonify({"status": "error", "message": "No error data available."}), 404

    error, derror = error_data['error'], error_data['derror']
    control_signal = compute_control_signalga(error, derror)
    logger.info(f"Computed control signal: {control_signal} for error: {error}, derror: {derror}")

    # Store the control signal in the uhistory table.
    with get_db_connection() as conn, conn.cursor() as cur:
        # Assuming 'id' is auto-generated and 'created' will be set to the current timestamp via NOW()
        cur.execute(
            "INSERT INTO uhistoryga (uhistory) VALUES (%s)",
            (control_signal,)
        )
        conn.commit()

    return jsonify({"output": 0})

@app.route('/send_error', methods=['POST'])
@db_error_handler
def receive_error_data():
    """Receive and store error and derror data."""
    data = request.get_json()
    error = data.get('error')
    derror = data.get('derror')

    if error is None or derror is None:
        return jsonify({"status": "error", "message": "Missing 'error' or 'derror' key in payload."}), 400

    try:
        error = float(error)
        derror = float(derror)
    except ValueError:
        return jsonify({"status": "error", "message": "'error' and 'derror' must be numeric."}), 400

    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO error (error, derror) VALUES (%s, %s)", (error, derror))
        conn.commit()

    logger.info(f"Received and stored error: {error}, derror: {derror}")
    return jsonify({"status": "success", "message": "Error data received and stored successfully."})

@app.route('/send_error2', methods=['POST'])
@db_error_handler
def receive_error_data2():
    """Receive and store error and derror data."""
    data = request.get_json()
    error = data.get('error')
    derror = data.get('derror')

    if error is None or derror is None:
        return jsonify({"status": "error", "message": "Missing 'error' or 'derror' key in payload."}), 400

    try:
        error = float(error)
        derror = float(derror)
    except ValueError:
        return jsonify({"status": "error", "message": "'error' and 'derror' must be numeric."}), 400

    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO error2 (error, derror) VALUES (%s, %s)", (error, derror))
        conn.commit()

    logger.info(f"Received and stored error: {error}, derror: {derror}")
    return jsonify({"status": "success", "message": "Error data received and stored successfully."})

import time

@app.route('/get_fuzzygaa', methods=['GET'])
@db_error_handler
def get_fuzzygaa():
    """Fetch error data and compute the control signal."""
    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT error, derror FROM test ORDER BY created DESC LIMIT 1")
        error_data = cur.fetchone()

    if not error_data:
        return jsonify({"status": "error", "message": "No error data available."}), 404

    error, derror = error_data['error'], error_data['derror']
    control_signal = compute_control_signalga(error, derror)
    logger.info(f"Computed control signal: {control_signal} for error: {error}, derror: {derror}")

    # If control signal is not zero, set output to 255 for 1 second
    if control_signal != 0:
        override_signal = 255
    else:
        override_signal = control_signal

    return jsonify({"output": override_signal})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=9217, debug=True)
