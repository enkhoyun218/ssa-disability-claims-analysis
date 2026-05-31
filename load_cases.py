import mysql.connector
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

STAGES = ["Intake", "Review", "Verification", "Approval", "Closed"]
CASE_TYPES = ["Permit", "Benefits", "License", "Appeal", "Complaint"]

# --- Update these with your MySQL credentials ---
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Cheese_cake218",
    database="case_pipeline"
)
cursor = conn.cursor()

events = []
for case_id in range(1, 501):
    case_type = random.choice(CASE_TYPES)
    current_time = fake.date_time_between(start_date="-6m", end_date="-1m")

    for stage in STAGES:
        # Verification is intentionally slow — simulates a real bottleneck
        delay = random.randint(5, 30) if stage == "Verification" else random.randint(1, 10)
        current_time += timedelta(days=delay)

        events.append((case_id, case_type, stage, current_time, fake.name()))

        # ~10% of cases stall and never finish
        if stage != "Closed" and random.random() < 0.1:
            break

cursor.executemany("""
    INSERT INTO case_events (case_id, case_type, stage, entered_at, assigned_to)
    VALUES (%s, %s, %s, %s, %s)
""", events)

conn.commit()
print(f"{cursor.rowcount} events loaded.")
cursor.close()
conn.close()