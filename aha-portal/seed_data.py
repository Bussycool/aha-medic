"""
seed_data.py

Synthetic seed data for the AHA Intern Capstone:
Patient Portal & AI Appointment Assistant.

Every name, email and note here is made up. No real patient information.

Usage:
    python seed_data.py                    # creates aha_portal.db
    python seed_data.py --csv seed_csv     # also exports CSVs (handy for David's analysis)
    python seed_data.py --db other.db --seed 7

Only the Python standard library is used, so there is nothing to install.
Running it again rebuilds the database from scratch.
"""

import argparse
import csv
import hashlib
import hmac
import os
import random
import secrets
import sqlite3
from datetime import date, datetime, timedelta

# ---------------------------------------------------------------------------
# Password hashing (PBKDF2-SHA256 from the standard library).
# Covenant can swap this for bcrypt or argon2 later. David can import
# hash_password and verify_password into the login code.
# ---------------------------------------------------------------------------
ITERATIONS = 200_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), ITERATIONS
    ).hex()
    return f"pbkdf2_sha256${ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    _, iterations, salt, digest = stored.split("$")
    check = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), int(iterations)
    ).hex()
    return hmac.compare_digest(check, digest)


# ---------------------------------------------------------------------------
# Synthetic people
# ---------------------------------------------------------------------------
EMAIL_DOMAIN = "ahademo.test"  # .test is reserved, so these can never be real

STAFF = ["Dr. Amina Bello", "Dr. Chinedu Okafor", "Nurse Funmi Adeyemi"]

PATIENTS = [
    "Tunde Bakare", "Ngozi Eze", "Ibrahim Musa", "Blessing Okon",
    "Emeka Nwosu", "Halima Abubakar", "Seun Ogunleye", "Grace Ekanem",
    "Yusuf Danjuma", "Chiamaka Obi",
]

STAFF_PASSWORD = "Staff@123"
PATIENT_PASSWORD = "Patient@123"

# Generic, non-diagnostic notes. Nothing here should read like real medical advice.
RECORD_NOTES = [
    "Routine check-up. No concerns raised. Follow up in 3 months.",
    "Blood pressure reading taken and logged. Review at next visit.",
    "Medication refill discussed. Patient to collect from pharmacy.",
    "Annual wellness visit completed. Lifestyle advice given.",
    "Follow-up visit. Patient reports feeling better. No further action.",
    "Lab test requested. Results to be reviewed at next appointment.",
    "Vaccination record updated.",
    "Patient asked about diet and exercise. Information leaflet provided.",
    "Missed dose reminder discussed. Patient to set a phone alarm.",
    "Referral letter prepared for specialist review.",
]

# ---------------------------------------------------------------------------
# Appointment slots, with built-in patterns so the staff insight view has
# something to show: mornings and Mondays are busiest, Friday afternoons quiet.
# ---------------------------------------------------------------------------
SLOT_WEIGHTS = {"09:00": 5, "10:00": 4, "11:00": 3, "13:00": 2, "14:00": 2, "15:00": 1}
DAY_WEIGHTS = {0: 5, 1: 3, 2: 3, 3: 2, 4: 1}  # Monday=0 ... Friday=4

DAYS_BACK = 21
DAYS_FORWARD = 14
TARGET_APPOINTMENTS = 55
TARGET_RECORDS = 25

SCHEMA = """
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS records;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('patient', 'staff'))
);

CREATE TABLE records (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL REFERENCES users(id),
    staff_id   INTEGER NOT NULL REFERENCES users(id),
    notes      TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE appointments (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id       INTEGER NOT NULL REFERENCES users(id),
    staff_id         INTEGER NOT NULL REFERENCES users(id),
    appointment_time TEXT NOT NULL,
    status           TEXT NOT NULL CHECK (status IN ('booked', 'cancelled'))
);
"""


def email_for(name: str) -> str:
    parts = name.replace("Dr. ", "").replace("Nurse ", "").lower().split()
    return f"{'.'.join(parts)}@{EMAIL_DOMAIN}"


def build_users():
    users, accounts = [], []
    for name in STAFF:
        users.append((name, email_for(name), hash_password(STAFF_PASSWORD), "staff"))
        accounts.append((name, email_for(name), STAFF_PASSWORD, "staff"))
    for name in PATIENTS:
        users.append((name, email_for(name), hash_password(PATIENT_PASSWORD), "patient"))
        accounts.append((name, email_for(name), PATIENT_PASSWORD, "patient"))
    return users, accounts


def build_records(patient_ids, staff_ids, now):
    # Every patient gets at least one record, then the rest are spread randomly.
    owners = list(patient_ids) + random.choices(
        patient_ids, k=TARGET_RECORDS - len(patient_ids)
    )
    records = []
    for patient_id in owners:
        created = now - timedelta(
            days=random.randint(1, 180),
            hours=random.randint(0, 7),
            minutes=random.choice([0, 15, 30, 45]),
        )
        created = created.replace(hour=max(9, min(created.hour, 16)))
        records.append((
            patient_id,
            random.choice(staff_ids),
            random.choice(RECORD_NOTES),
            created.strftime("%Y-%m-%d %H:%M"),
        ))
    records.sort(key=lambda r: r[3])
    return records


def status_for(when, now):
    cancel_rate = 0.15 if when < now else 0.10
    return "cancelled" if random.random() < cancel_rate else "booked"


def build_appointments(patient_ids, staff_ids, now):
    today = now.date()
    taken_staff = set()    # (staff_id, datetime): one appointment per staff slot
    taken_patient = set()  # (patient_id, datetime): no double booking a patient
    appointments = []

    def add(day, slot, staff_id, patient_id=None, status=None):
        when = datetime.combine(day, datetime.strptime(slot, "%H:%M").time())
        if (staff_id, when) in taken_staff:
            return False
        candidates = [p for p in patient_ids if (p, when) not in taken_patient]
        if patient_id is not None:
            candidates = [patient_id] if patient_id in candidates else []
        if not candidates:
            return False
        chosen = random.choice(candidates)
        taken_staff.add((staff_id, when))
        taken_patient.add((chosen, when))
        appointments.append((
            chosen, staff_id, when.strftime("%Y-%m-%d %H:%M"),
            status or status_for(when, now),
        ))
        return True

    # Always seed today's schedule (even on a weekend) so the staff view has data.
    for slot in ["09:00", "10:00", "11:00", "14:00"]:
        add(today, slot, random.choice(staff_ids), status="booked")

    # Weighted candidates on weekdays across the window, excluding today.
    candidates, weights = [], []
    for offset in range(-DAYS_BACK, DAYS_FORWARD + 1):
        day = today + timedelta(days=offset)
        if day == today or day.weekday() > 4:
            continue
        for slot, slot_w in SLOT_WEIGHTS.items():
            for staff_id in staff_ids:
                candidates.append((day, slot, staff_id))
                weights.append(DAY_WEIGHTS[day.weekday()] * slot_w)

    attempts = 0
    while len(appointments) < TARGET_APPOINTMENTS and attempts < 5000:
        attempts += 1
        day, slot, staff_id = random.choices(candidates, weights=weights, k=1)[0]
        add(day, slot, staff_id)

    # Make sure every patient has at least one upcoming booked appointment,
    # so "list my appointments" works in the demo for any login.
    future = [c for c in candidates if c[0] > today]
    for patient_id in patient_ids:
        has_upcoming = any(
            a[0] == patient_id and a[3] == "booked" and a[2] > now.strftime("%Y-%m-%d %H:%M")
            for a in appointments
        )
        random.shuffle(future)
        for day, slot, staff_id in future:
            if has_upcoming:
                break
            has_upcoming = add(day, slot, staff_id, patient_id=patient_id, status="booked")

    appointments.sort(key=lambda a: a[2])
    return appointments


def export_csv(conn, folder):
    os.makedirs(folder, exist_ok=True)
    for table in ["users", "records", "appointments"]:
        cursor = conn.execute(f"SELECT * FROM {table}")
        columns = [c[0] for c in cursor.description]
        with open(os.path.join(folder, f"{table}.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(cursor.fetchall())


def write_test_accounts(accounts, path):
    # Plain test logins live here, NEVER in the database. Keep this file out of git.
    with open(path, "w") as f:
        f.write("TEST ACCOUNTS (synthetic, demo only, do not commit)\n\n")
        for name, email, password, role in accounts:
            f.write(f"{role:<8} {name:<22} {email:<36} {password}\n")


def main():
    parser = argparse.ArgumentParser(description="Seed the AHA capstone database.")
    parser.add_argument("--db", default="aha_portal.db", help="SQLite file to create")
    parser.add_argument("--csv", help="Folder to also export CSVs into")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (same seed, same data)")
    args = parser.parse_args()

    random.seed(args.seed)
    now = datetime.now().replace(second=0, microsecond=0)

    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)

    users, accounts = build_users()
    conn.executemany(
        "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)", users
    )
    staff_ids = [r[0] for r in conn.execute("SELECT id FROM users WHERE role = 'staff'")]
    patient_ids = [r[0] for r in conn.execute("SELECT id FROM users WHERE role = 'patient'")]

    conn.executemany(
        "INSERT INTO records (patient_id, staff_id, notes, created_at) VALUES (?, ?, ?, ?)",
        build_records(patient_ids, staff_ids, now),
    )
    conn.executemany(
        "INSERT INTO appointments (patient_id, staff_id, appointment_time, status) "
        "VALUES (?, ?, ?, ?)",
        build_appointments(patient_ids, staff_ids, now),
    )
    conn.commit()

    write_test_accounts(accounts, "test_accounts.txt")
    if args.csv:
        export_csv(conn, args.csv)

    # Quick summary, including a preview of the staff insight view.
    def count(sql):
        return conn.execute(sql).fetchone()[0]

    today = date.today().isoformat()
    total_users = count("SELECT COUNT(*) FROM users")
    total_records = count("SELECT COUNT(*) FROM records")
    total_appts = count("SELECT COUNT(*) FROM appointments")
    cancelled = count("SELECT COUNT(*) FROM appointments WHERE status = 'cancelled'")
    today_booked = count(
        "SELECT COUNT(*) FROM appointments "
        f"WHERE appointment_time LIKE '{today}%' AND status = 'booked'"
    )

    print(f"Database:      {args.db}")
    print(f"Users:         {total_users} ({len(staff_ids)} staff, {len(patient_ids)} patients)")
    print(f"Records:       {total_records}")
    print(f"Appointments:  {total_appts} ({cancelled} cancelled)")
    print(f"Today's schedule: {today_booked} booked")
    print("Busiest slots:")
    for slot, n in conn.execute(
        "SELECT substr(appointment_time, 12, 5) AS slot, COUNT(*) AS n FROM appointments "
        "WHERE status = 'booked' GROUP BY slot ORDER BY n DESC LIMIT 3"
    ):
        print(f"  {slot}  {n} bookings")
    print("Test logins written to test_accounts.txt")
    if args.csv:
        print(f"CSVs exported to {args.csv}/")
    conn.close()


if __name__ == "__main__":
    main()
