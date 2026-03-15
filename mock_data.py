import pandas as pd
import random
from datetime import datetime, timedelta

SENSORS = ["S1", "S2", "S3", "S4"]
LOCATIONS = ["Corner A", "Corner B", "Corner C", "Corner D"]

def classify_leak(ppm):
    if ppm > 150:
        return True, "Major Leak"
    elif ppm > 50:
        return True, "Moderate Leak"
    elif ppm > 25:
        return True, "Minor Leak"
    else:
        return False, None

def get_latest_readings():
    rows = []
    for i, sid in enumerate(SENSORS):
        if sid == "S1":
            ppm = round(random.uniform(5, 15), 2)       # Normal
        elif sid == "S2":
            ppm = round(random.uniform(26, 50), 2)      # Minor Leak
        elif sid == "S3":
            ppm = round(random.uniform(51, 150), 2)     # Moderate Leak
        elif sid == "S4":
            ppm = round(random.uniform(151, 300), 2)    # Major Leak

        anomaly, leak_type = classify_leak(ppm)

        rows.append({
            "sensor_id": sid,
            "hydrogen_ppm": ppm,
            "temperature": round(random.uniform(22, 35), 1),
            "humidity": round(random.uniform(40, 70), 1),
            "is_anomaly": anomaly,
            "leak_type": leak_type if leak_type else "Normal",
            "leak_location": LOCATIONS[i],
            "timestamp": datetime.now()
        })
    return pd.DataFrame(rows)

def get_historical_readings(minutes=10):
    rows = []
    now = datetime.now()
    for i, sid in enumerate(SENSORS):
        for m in range(minutes * 6):
            if sid == "S1":
                ppm = round(random.uniform(5, 15), 2)
            elif sid == "S2":
                ppm = round(random.uniform(20, 55), 2)
            elif sid == "S3":
                ppm = round(random.uniform(40, 160), 2)
            elif sid == "S4":
                ppm = round(random.uniform(100, 310), 2)

            rows.append({
                "sensor_id": sid,
                "hydrogen_ppm": ppm,
                "temperature": round(random.uniform(22, 35), 1),
                "humidity": round(random.uniform(40, 70), 1),
                "timestamp": now - timedelta(seconds=(minutes * 60 - m * 10))
            })
    return pd.DataFrame(rows)
