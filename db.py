import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:yourpassword@localhost:5432/hydrogen_db")
engine = create_engine(DB_URL)

def get_latest_readings():
    query = """
        SELECT DISTINCT ON (sensor_id)
            sensor_id, hydrogen_ppm, temperature, humidity,
            is_anomaly, leak_location, timestamp
        FROM sensor_readings
        ORDER BY sensor_id, timestamp DESC;
    """
    return pd.read_sql(query, engine)

def get_historical_readings(minutes=10):
    query = f"""
        SELECT sensor_id, hydrogen_ppm, temperature, humidity, timestamp
        FROM sensor_readings
        WHERE timestamp >= NOW() - INTERVAL '{minutes} minutes'
        ORDER BY timestamp ASC;
    """
    return pd.read_sql(query, engine)
