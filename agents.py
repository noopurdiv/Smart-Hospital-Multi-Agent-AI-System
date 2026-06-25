from typing import TypedDict, List
from langchain_core.messages import HumanMessage
import os, random, json
from langchain_groq import ChatGroq
import pytz
from datetime import datetime, timedelta
import psycopg2
from dotenv import load_dotenv, find_dotenv
import logging
from logging import debug

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(_env_path, override=True)
if not os.getenv("GROQ_API_KEY"):
    load_dotenv(find_dotenv(), override=True)

MODEL_NAME = "llama-3.3-70b-versatile"

conn = psycopg2.connect(
    host="localhost",
    database="hospital",
    user="postgres",
    password="password",
    port="5432",
)
cursor = conn.cursor()
queued_patients = []


def _safe_rollback():
    try:
        conn.rollback()
    except Exception:
        pass


def _get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Check your .env file.")
    return ChatGroq(api_key=api_key, model_name=MODEL_NAME)


def get_beds():
    _safe_rollback()
    query = """
        SELECT DISTINCT type,
            (SELECT COUNT(*) FROM rooms r1 WHERE r1.type = r.type AND is_occupied = FALSE) available,
            (SELECT COUNT(*) FROM rooms r1 WHERE r1.type = r.type AND is_occupied = TRUE) blocked
        FROM rooms r;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    output = {}
    for data in rows:
        output[data[0]] = data[1:]
    return output


def get_doctor_status():
    debug("Getting doctor status update...")
    _safe_rollback()
    cursor.execute("SELECT refresh_data();")
    conn.commit()
    query = """
        SELECT
            d.name AS doctor_name,
            d.specialist AS department,
            (CASE WHEN d.is_busy = TRUE THEN 'BUSY' ELSE 'AVAILABLE' END) AS status,
            (CASE WHEN d.is_busy = TRUE THEN p.patient_name ELSE NULL END) AS with_patient,
            (CASE WHEN d.is_busy = TRUE
                THEN ROUND(EXTRACT(EPOCH FROM (d.busy_till - CURRENT_TIMESTAMP)) / 60, 2)
                ELSE NULL END) AS time_remaining,
            (CASE WHEN d.is_busy = TRUE THEN d.busy_till ELSE NULL END) AS finish_time,
            (CASE WHEN d.is_busy = TRUE THEN d.busy_from ELSE NULL END) AS start_time
        FROM doctors d
        LEFT JOIN ongoing_cases oc ON d.doctor_id = oc.doctor_id
        LEFT JOIN patient_info p ON oc.patient_id = p.patient_id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cols = ["doctor_name", "department", "status", "with_patient",
            "time_remaining", "finish_time", "start_time"]
    return [dict(zip(cols, row)) for row in rows]


def get_block_duration(triage_level):
    return timedelta(minutes=max(1, triage_level))


def get_current_est_time():
    return datetime.now(pytz.timezone("US/Eastern"))


def get_current_time_with_ms():
    return datetime.now(pytz.timezone("US/Eastern")).strftime("%H:%M:%S.%f")[:-3]


class Patient:
    def __init__(self, name, vitals, email, gender, age, symptoms, symptom_duration):
        self.name = name
        self.symptoms = symptoms
        self.symptom_duration = symptom_duration
        self.email = email
        self.phone = None
        self.age = age
        self.vitals = vitals
        self.gender = gender
        self.mood = None
        self.triage_level = None
        self.department = None
        self.assigned_doctor = None
        self.assigned_bed = None
        self.bed_priority = None
        self.priority_score = 0.0
        self.entry_time = get_current_est_time()
        self.treatment_completed = False
        self.treatment_end_time = None

    def calculate_priority(self):
        triage_weight = 10
        triage_score = (self.triage_level or 1) * triage_weight

        if self.age >= 50:
            age_score = 8
        elif self.age < 15:
            age_score = 5
        else:
            age_score = 0

        hr = self.vitals.get("heart_rate", 80)
        bp_sys = self.vitals.get("blood_pressure", {}).get("systolic", 120)
        bp_dia = self.vitals.get("blood_pressure", {}).get("diastolic", 80)

        hr_dev = max(hr - 100, 60 - hr, 0)
        bp_sys_dev = abs(bp_sys - 120) if bp_sys > 140 or bp_sys < 90 else 0
        bp_dia_dev = abs(bp_dia - 80) if bp_dia > 90 or bp_dia < 60 else 0
        vital_score = (hr_dev + bp_sys_dev + bp_dia_dev) * 0.7

        duration_score = self.symptom_duration * 0.2

        self.priority_score = round(triage_score + age_score + vital_score + duration_score, 1)

    def to_dict(self):
        self.calculate_priority()
        end_time = None
        if self.treatment_end_time:
            end_time = self.treatment_end_time.strftime("%H:%M:%S.%f")[:-3]
        return {
            "name": self.name,
            "symptoms": self.symptoms,
            "symptom_duration": self.symptom_duration,
            "contact_number": self.phone,
            "age": self.age,
            "email": self.email,
            "gender": self.gender,
            "mood": self.mood,
            "triage_level": self.triage_level,
            "department": self.department,
            "assigned_doctor": self.assigned_doctor,
            "assigned_bed": self.assigned_bed,
            "priority_score": self.priority_score,
            "treatment_completed": self.treatment_completed,
            "treatment_end_time": end_time,
            "entry_time": self.entry_time.strftime("%H:%M:%S.%f")[:-3],
        }


class AgentState(TypedDict):
    patient: Patient
    logs: List[str]
    status: dict
    cache: dict


def adjust_mood_based_on_vitals(patient, detected_mood):
    symptoms_str = " ".join(patient.symptoms).lower()
    bp_diastolic = patient.vitals.get("blood_pressure", {}).get("diastolic", 80)
    hr = patient.vitals.get("heart_rate", 80)

    if hr > 120 or bp_diastolic < 60:
        return "panicked"
    if "cardiac arrest" in symptoms_str:
        return "panicked"
    if "mild cough" in symptoms_str and hr < 100:
        return "calm"
    return detected_mood


# ---------------------------------------------------------------------------
# Agent 1 : Mental Health / Mood Analyzer
# ---------------------------------------------------------------------------
class MentalHealthAnalyzerAgent:
    def __call__(self, state: AgentState) -> AgentState:
        debug("Entering MentalHealthAnalyzerAgent...")
        _safe_rollback()
        patient = state["patient"]
        bp = patient.vitals.get("blood_pressure", {})
        systolic = bp.get("systolic", 120)
        diastolic = bp.get("diastolic", 80)
        hr = patient.vitals.get("heart_rate", 80)

        symptoms_str = ", ".join(patient.symptoms)
        vitals_str = json.dumps(patient.vitals)
        try:
            cursor.execute(
                """INSERT INTO patient_info
                   (patient_name, email, phone, gender, symptoms, symptoms_duration, vitals)
                   VALUES (%s, %s, NULL, %s, %s, %s, %s)
                   ON CONFLICT (email) DO UPDATE SET
                       patient_name = EXCLUDED.patient_name,
                       gender = EXCLUDED.gender,
                       symptoms = EXCLUDED.symptoms,
                       symptoms_duration = EXCLUDED.symptoms_duration,
                       vitals = EXCLUDED.vitals,
                       visit_datetime = CURRENT_TIMESTAMP""",
                (patient.name, patient.email, patient.gender,
                 symptoms_str, str(patient.symptom_duration), vitals_str),
            )
            conn.commit()
            debug("Patient information inserted successfully...")
        except Exception as e:
            debug(f"Error inserting patient: {e}")
            _safe_rollback()

        prompt = (
            f"Analyze patient's emotional state based on:\n"
            f"- Vitals: BP {systolic}/{diastolic}, HR {hr}\n"
            f"- Symptoms: {patient.symptoms}\n"
            f"- Duration: {patient.symptom_duration} hours\n"
            f"- Age: {patient.age}\n"
            'Return JSON: { "mood": "chosen_mood" }\n'
            "chosen_mood must be one of: calm, frustrated, anxious, stressed, confused, panicked"
        )

        try:
            llm = _get_llm()
            response = llm.invoke([HumanMessage(content=prompt)])
            debug("Got mood estimate from LLM...")
            if "{" in response.content:
                start = response.content.find("{")
                end = response.content.rfind("}") + 1
                mood_info = json.loads(response.content[start:end])
                if "mood" in mood_info:
                    detected_mood = adjust_mood_based_on_vitals(patient, mood_info["mood"])
                    patient.mood = detected_mood
                    mood_emoji = {
                        "calm": "😌", "frustrated": "😖", "anxious": "😥",
                        "stressed": "😧", "confused": "😵‍💫", "panicked": "🫨",
                    }
                    emoji = mood_emoji.get(patient.mood, "")
                    ts = get_current_time_with_ms()
                    state["logs"].append(
                        f"[{ts}] MentalHealthAnalyzerAgent : Detected Mood is {patient.mood} {emoji}"
                    )
                    state["status"]["MoodAnalyzer"] = "Success"
        except Exception as e:
            debug(f"Error estimating mood: {e}")
            ts = get_current_time_with_ms()
            state["logs"].append(f"[{ts}] MentalHealthAnalyzerAgent : {e}")
            state["status"]["MoodAnalyzer"] = "Failed"

        if patient.mood is None:
            patient.mood = adjust_mood_based_on_vitals(patient, "stressed")
            ts = get_current_time_with_ms()
            state["logs"].append(
                f"[{ts}] MentalHealthAnalyzerAgent : Fallback — defaulted mood to {patient.mood}"
            )
            state["status"]["MoodAnalyzer"] = "Success"

        debug("Exiting MentalHealthAnalyzerAgent...")
        return state


# ---------------------------------------------------------------------------
# Agent 2 : Emergency Triage
# ---------------------------------------------------------------------------
class EmergencyTriageAgent:
    def __call__(self, state: AgentState) -> AgentState:
        debug("Entering EmergencyTriageAgent...")
        _safe_rollback()
        patient = state["patient"]
        bp = patient.vitals.get("blood_pressure", {})
        hr = patient.vitals.get("heart_rate", 80)

        prompt = (
            f"Assign triage_level (1-5) and department based on:\n"
            f"- Symptoms: {patient.symptoms}\n"
            f"- BP: {bp.get('systolic', 120)}/{bp.get('diastolic', 80)}\n"
            f"- HR: {hr}\n"
            f"- Mood: {patient.mood}\n"
            f"- Age: {patient.age}\n"
            f"- Duration: {patient.symptom_duration}h\n"
            'Return JSON: {"triage_level": number, "department": "string"}\n'
            'department must be one of: Cardiology, Pediatrics, Neurology, Dentist'
        )

        try:
            llm = _get_llm()
            response = llm.invoke([HumanMessage(content=prompt)])
            debug("Got triage level from the LLM...")
            if "{" in response.content:
                start = response.content.find("{")
                end = response.content.rfind("}") + 1
                triage_info = json.loads(response.content[start:end])
                if "triage_level" in triage_info and "department" in triage_info:
                    patient.triage_level = triage_info["triage_level"]
                    patient.department = triage_info["department"]
                    tl = triage_info['triage_level']
                    dept = triage_info['department']
                    debug(f"triage level: {tl}, department: {dept}")
                    ts = get_current_time_with_ms()
                    state["logs"].append(
                        f"[{ts}] EmergencyTriageAgent : Level {patient.triage_level} -> {patient.department}"
                    )
                    state["status"]["EmergencyTriage"] = "Success"
        except Exception as e:
            debug(f"Error estimating triage: {e}")
            ts = get_current_time_with_ms()
            state["logs"].append(f"[{ts}] EmergencyTriageAgent : Error - {e}")
            state["status"]["EmergencyTriage"] = "Failed"

        if patient.triage_level is None:
            patient.triage_level = 3
            patient.department = patient.department or "Cardiology"
            ts = get_current_time_with_ms()
            state["logs"].append(
                f"[{ts}] EmergencyTriageAgent : Fallback — defaulted to Level 3 / {patient.department}"
            )
            state["status"]["EmergencyTriage"] = "Success"

        debug("Exiting EmergencyTriageAgent...")
        return state


# ---------------------------------------------------------------------------
# Agent 3 : Doctor Scheduler
# ---------------------------------------------------------------------------
class DoctorSchedulerAgent:
    def __call__(self, state: AgentState) -> AgentState:
        debug("Entering DoctorSchedulerAgent...")
        _safe_rollback()
        patient = state["patient"]
        dept = patient.department
        now = datetime.now(pytz.timezone("US/Eastern"))

        debug(f"Attempting to fetch available {dept} specialist doctors...")
        cursor.execute("SELECT * FROM get_available_doctors(%s);", (dept,))
        available = cursor.fetchall()
        debug("Fetched the available doctors...")

        if available:
            assigned = random.choice(available)
            patient.assigned_doctor = assigned[1]
            state["cache"]["doctor_assigned"] = assigned
            block_duration = get_block_duration(patient.triage_level)
            blocked_until = now + block_duration
            state["cache"]["doctor_blocked_from"] = now
            state["cache"]["doctor_blocked_until"] = blocked_until
            debug("Attempting to allocate doctor...")
            cursor.execute(
                """UPDATE doctors
                   SET is_busy = TRUE, busy_from = %s, busy_till = %s
                   WHERE doctor_id = %s""",
                (now, blocked_until, assigned[0]),
            )
            conn.commit()
            debug("Successfully allocated doctor...")
            state["status"]["DoctorScheduler"] = "Success"
            ts = get_current_time_with_ms()
            state["logs"].append(
                f"[{ts}] DoctorSchedulerAgent : Assigned {patient.assigned_doctor} to {patient.name}"
            )
        else:
            debug("No doctors available...")
            ts = get_current_time_with_ms()
            state["logs"].append(f"[{ts}] DoctorSchedulerAgent : No {dept} doctor available.")
            state["status"]["DoctorScheduler"] = "Failed"

        debug("Exiting DoctorSchedulerAgent...")
        return state


# ---------------------------------------------------------------------------
# Agent 4 : Bed Manager
# ---------------------------------------------------------------------------
class BedManagerAgent:
    def __call__(self, state: AgentState) -> AgentState:
        debug("Entering BedManagerAgent...")
        _safe_rollback()
        patient = state["patient"]
        level = patient.triage_level

        if level == 5:
            bed_priority = ["ICU", "Emergency"]
        elif level in [3, 4]:
            bed_priority = ["Ward", "Emergency"]
        else:
            bed_priority = ["Normal", "Ward", "Emergency"]

        patient.bed_priority = bed_priority

        for bed_type in bed_priority:
            debug(f"Checking bed type {bed_type}...")
            cursor.execute("SELECT * FROM get_available_rooms(%s::room_type)", (bed_type,))
            available_bed_details = cursor.fetchall()
            if available_bed_details:
                debug(f"Found available bed in {bed_type}...")
                patient.assigned_bed = available_bed_details[0][0]
                state["cache"]["bed_assigned"] = available_bed_details
                cursor.execute(
                    "UPDATE rooms SET is_occupied = TRUE WHERE room_number = %s",
                    (available_bed_details[0][0],),
                )
                conn.commit()
                debug("Successfully allocated a bed...")
                ts = get_current_time_with_ms()
                state["logs"].append(
                    f"[{ts}] BedManagerAgent : {patient.name} assigned to {bed_type} bed {patient.assigned_bed} (triage {level})"
                )
                state["status"]["BedManager"] = "Success"
                return state

        debug("No beds found...")
        ts = get_current_time_with_ms()
        state["logs"].append(f"[{ts}] BedManagerAgent : No beds available for {patient.name}")
        state["status"]["BedManager"] = "Failed"
        return state


# ---------------------------------------------------------------------------
# Agent 5 : Conflict Resolver
# ---------------------------------------------------------------------------
class ConflictResolverAgent:
    def __call__(self, state: AgentState) -> AgentState:
        debug("Entering ConflictResolverAgent...")
        _safe_rollback()
        patient = state["patient"]
        bed_status = state["status"]["BedManager"]
        doctor_status = state["status"]["DoctorScheduler"]

        patient.calculate_priority()
        debug(f"Calculated priority score: {patient.priority_score}")
        ts = get_current_time_with_ms()
        state["logs"].append(
            f"[{ts}] ConflictResolverAgent : Calculated priority score : {patient.priority_score}"
        )

        if bed_status == "Success" and doctor_status == "Success":
            debug("No conflicts found. Creating case...")
            doctor_id = state["cache"]["doctor_assigned"][0]
            room_number = state["cache"]["bed_assigned"][0][0]
            cursor.execute(
                """INSERT INTO ongoing_cases(patient_id, doctor_id, room_number)
                   VALUES (
                       (SELECT patient_id FROM patient_info WHERE email = %s),
                       %s, %s
                   )""",
                (patient.email, doctor_id, room_number),
            )
            conn.commit()
            ts = get_current_time_with_ms()
            state["logs"].append(
                f"[{ts}] ConflictResolverAgent : Assigning available doctor and bed to {patient.name}"
            )
            state["status"]["ConflictResolver"] = "Success"

        elif bed_status == "Success" and doctor_status == "Failed":
            debug("Conflict: Doctor not available. Queuing...")
            cursor.execute(
                "UPDATE rooms SET is_occupied = FALSE WHERE room_number = %s",
                (patient.assigned_bed,),
            )
            conn.commit()
            ts = get_current_time_with_ms()
            state["logs"].append(
                f"[{ts}] ConflictResolverAgent : No doctors available. Queuing the application."
            )
            state["status"]["ConflictResolver"] = "Queued"

        elif bed_status == "Failed" and doctor_status == "Success":
            debug("Conflict: Bed not available. Queuing...")
            doctor_id = state["cache"]["doctor_assigned"][0]
            cursor.execute(
                "UPDATE doctors SET is_busy = FALSE, busy_from = NULL, busy_till = NULL WHERE doctor_id = %s",
                (doctor_id,),
            )
            conn.commit()
            ts = get_current_time_with_ms()
            state["logs"].append(
                f"[{ts}] ConflictResolverAgent : No beds available. Queuing the application."
            )
            state["status"]["ConflictResolver"] = "Queued"

        else:
            debug("No beds or doctors available...")
            ts = get_current_time_with_ms()
            state["logs"].append(
                f"[{ts}] ConflictResolverAgent : No beds and doctors available. Please try nearby hospitals."
            )
            state["status"]["ConflictResolver"] = "Failed"

        if state["status"]["ConflictResolver"] == "Queued":
            bed_type = patient.bed_priority[0] if patient.bed_priority else "Normal"
            cursor.execute(
                """INSERT INTO queue VALUES (
                       (SELECT patient_id FROM patient_info WHERE email = %s),
                       %s, %s::room_type
                   )""",
                (patient.email, patient.priority_score, bed_type),
            )
            conn.commit()
            debug("Application queued...")
            state["status"]["ConflictResolver"] = "Success"

        debug("Exiting ConflictResolverAgent...")
        return state
