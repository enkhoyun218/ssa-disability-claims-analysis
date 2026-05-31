import mysql.connector
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

STAGES = ["Intake", "Eligibility Review", "Document Verification", "Approval", "Benefits Issued"]
APPLICANT_TYPES = ["Food Assistance", "Housing", "Medical", "Childcare", "Employment"]
PRIORITIES = ["Standard", "Urgent", "Critical"]
STATUSES = ["Pending", "Approved", "Denied"]

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Cheese_cake218",
    database="benefits_system"
)
cursor = conn.cursor()

events = []
for app_id in range(1, 601):
    applicant_type = random.choice(APPLICANT_TYPES)
    priority = random.choices(PRIORITIES, weights=[70, 20, 10])[0]
    current_time = fake.date_time_between(start_date="-6m", end_date="-1m")

    for stage in STAGES:
        # Critical cases move faster, Standard cases slower
        if priority == "Critical":
            delay = random.randint(1, 5)
        elif priority == "Urgent":
            delay = random.randint(3, 15)
        else:
            delay = random.randint(5, 30)

        # Document Verification is intentionally slow
        if stage == "Document Verification":
            delay = delay * 2

        current_time += timedelta(days=delay)

        # Assign status at final stages
        if stage == "Approval":
            status = random.choices(["Approved", "Denied"], weights=[70, 30])[0]
        elif stage == "Benefits Issued":
            status = "Approved"
        else:
            status = "Pending"

        events.append((
            app_id,
            applicant_type,
            stage,
            status,
            priority,
            current_time,
            fake.name()
        ))

        # ~15% of applications stall and never finish
        if stage != "Benefits Issued" and random.random() < 0.15:
            break

cursor.executemany("""
    INSERT INTO benefits_applications 
    (application_id, applicant_type, stage, status, priority, entered_at, assigned_to)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
""", events)

conn.commit()
print(f"{cursor.rowcount} events loaded.")
cursor.close()
conn.close()