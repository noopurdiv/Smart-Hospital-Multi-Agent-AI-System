"""One-time script to seed doctors and rooms into the hospital database."""
from agents import conn, cursor, _safe_rollback

_safe_rollback()

cursor.execute("""
    DELETE FROM ongoing_cases;
    DELETE FROM queue;
""")
conn.commit()

doctors = [
    ("Dr. Smith", "Cardiology"),
    ("Dr. Adams", "Cardiology"),
    ("Dr. Jones", "Pediatrics"),
    ("Dr. Williams", "Pediatrics"),
    ("Dr. Lee", "Neurology"),
    ("Dr. Chen", "Neurology"),
    ("Dr. Patel", "Dentist"),
    ("Dr. Garcia", "Dentist"),
]

for name, spec in doctors:
    cursor.execute(
        "INSERT INTO doctors (name, specialist) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        (name, spec),
    )

rooms = [
    (101, "ICU"), (102, "ICU"),
    (201, "Emergency"), (202, "Emergency"),
    (301, "Ward"), (302, "Ward"), (303, "Ward"),
    (401, "Normal"), (402, "Normal"), (403, "Normal"),
]

for num, rtype in rooms:
    cursor.execute(
        "INSERT INTO rooms (room_number, type) VALUES (%s, %s::room_type) ON CONFLICT DO NOTHING",
        (num, rtype),
    )

conn.commit()

cursor.execute("SELECT COUNT(*) FROM doctors")
print(f"Doctors: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM rooms")
print(f"Rooms:   {cursor.fetchone()[0]}")
print("Database seeded successfully!")
