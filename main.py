import os
import logging
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(override=True)




logging.basicConfig(
    level=logging.INFO,
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = FastAPI(
    title="AHA Medic",
    description="AHA Medic API",
    version="1.0.0",
    contact={
        "name": "David & Covenant - Advantage Health Africa",
        "url": "https://www.advantagehealthafrica.com"
    },
)

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://localhost:8443",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8443",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "hello": "world"
    }








## ===========================================================================
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# import sqlite3
# from pydantic import BaseModel

# # THIS IS THE KEY FOR TASK 3 - import from seed_data.py
# from seed_data import verify_password, hash_password

# app = FastAPI(title="AHA Patient Portal API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# DB_PATH = "aha_portal.db"

# def get_connection():
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn

# @app.get("/")
# def home():
#     return {"message": "AHA Portal API - Task 3 Login Ready"}

# @app.get("/check-db")
# def check_db():
#     conn = get_connection()
#     users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
#     appts = conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
#     conn.close()
#     return {"users": users, "appointments": appts}

# # -------- TASK 3: LOGIN WITH verify_password --------
# class LoginRequest(BaseModel):
#     email: str
#     password: str

# @app.post("/login")
# def login(req: LoginRequest):
#     conn = get_connection()
#     user = conn.execute("SELECT * FROM users WHERE email =?", (req.email,)).fetchone()
#     conn.close()

#     if not user:
#         raise HTTPException(status_code=401, detail="Email not found")

#     # Get the hash from DB - could be column named password_hash or password
#     stored_hash = user["password_hash"] if "password_hash" in user.keys() else user["password"]

#     # THIS IS TASK 3 - use verify_password function from seed_data.py
#     if not verify_password(req.password, stored_hash):
#         raise HTTPException(status_code=401, detail="Incorrect password")

#     return {
#         "success": True,
#         "message": f"Welcome {user['name']}",
#         "user": {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"]}
#     }

# # Your appointment code stays same
# class NewAppointment(BaseModel):
#     patient_id: int = 1
#     staff_id: int = 2
#     appointment_time: str = "2026-10-12 10:00"
#     status: str = "booked"

# @app.post("/appointments/new")
# def create_appointment(appt: NewAppointment):
#     conn = get_connection()
#     conn.execute(
#         "INSERT INTO appointments (patient_id, staff_id, appointment_time, status) VALUES (?,?,?,?)",
#         (appt.patient_id, appt.staff_id, appt.appointment_time, appt.status)
#     )
#     conn.commit()
#     count = conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
#     conn.close()
#     return {"success": True, "total_appointments_now": count}

# @app.get("/appointments")
# def show_appointments():
#     conn = get_connection()
#     rows = conn.execute("SELECT * FROM appointments LIMIT 20").fetchall()
#     conn.close()
#     return [dict(r) for r in rows]
    