# SHMAS — Smart Hospital Multi-Agent AI System

**Second Place Winner, Luddy Hackathon**

SHMAS is an AI-powered hospital operations platform that uses five autonomous agents orchestrated by LangGraph to automate patient triage, doctor scheduling, bed management, and conflict resolution in real time. It features a Streamlit dashboard for live monitoring and patient admission.

---

## Architecture

```
Patient Admission
       |
       v
+------------------+     +-------------------+     +------------------+
| Mental Health     | --> | Emergency Triage  | --> | Doctor Scheduler |
| Analyzer          |     | Agent             |     | Agent            |
+------------------+     +-------------------+     +------------------+
                                                           |
                                                           v
                                                   +------------------+
                                                   | Bed Manager      |
                                                   | Agent            |
                                                   +------------------+
                                                           |
                                                           v
                                                   +------------------+
                                                   | Conflict         |
                                                   | Resolver Agent   |
                                                   +------------------+
                                                           |
                                                           v
                                                   Admission Result
```

### The Five Agents

| Agent | Role |
|-------|------|
| **Mental Health Analyzer** | Assesses patient mood from symptoms and vitals using LLM analysis. Assigns a mood score that factors into priority. |
| **Emergency Triage** | Determines triage level (1-5) and department assignment based on symptoms, vitals, and duration. |
| **Doctor Scheduler** | Finds an available doctor in the assigned department and schedules the appointment. |
| **Bed Manager** | Allocates an appropriate bed (ICU, Emergency, Ward, Normal) based on triage severity. |
| **Conflict Resolver** | Handles resource contention — if no doctor or bed is available, queues the patient by priority score. |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Orchestration | LangGraph (stateful graph-based workflows) |
| LLM Provider | Groq API (`llama-3.3-70b-versatile`) |
| LLM Framework | LangChain Core + LangChain Groq |
| Database | PostgreSQL |
| Frontend | Streamlit (light theme, custom CSS) |
| Language | Python 3.10+ |

---

## Project Structure

```
Smart-Hospital-Multi-Agent-AI-System/
├── agents.py                 # Agent classes, Patient model, DB utilities
├── smart_hospital.py         # LangGraph workflow definition
├── streamlit_dashboard.py    # Streamlit UI (patient form, agent feed, beds, doctors)
├── hospitals_db.sql          # PostgreSQL schema (tables, types, triggers, seed data)
├── seed_db.py                # Database seeding script
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml           # Streamlit theme configuration (light)
└── .env                      # Environment variables (GROQ_API_KEY)
```

---

## Prerequisites

- **Python 3.10+**
- **PostgreSQL** running locally on port 5432
- **Groq API key** — get one at [console.groq.com](https://console.groq.com)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/noopurdiv/Smart-Hospital-Multi-Agent-AI-System.git
cd Smart-Hospital-Multi-Agent-AI-System
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL

Create a database named `hospital` and run the schema file:

```bash
psql -U postgres -c "CREATE DATABASE hospital;"
psql -U postgres -d hospital -f hospitals_db.sql
```

Then seed the database with doctors and rooms:

```bash
python seed_db.py
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 6. Run the dashboard

```bash
streamlit run streamlit_dashboard.py
```

The dashboard opens at `http://localhost:8501`.

---

## Usage

1. Fill in patient details in the sidebar (name, email, gender, age, symptoms, vitals)
2. Click **Admit Patient**
3. The five-agent pipeline processes the patient automatically:
   - Mood analysis via LLM
   - Triage level and department assignment
   - Doctor scheduling
   - Bed allocation
   - Conflict resolution (queuing if resources unavailable)
4. Results appear in the main dashboard:
   - **Admission result card** with assigned doctor, bed, department, and triage level
   - **Agent Activity Feed** showing each agent's actions with timestamps
   - **Bed Availability** cards with real-time occupancy
   - **Doctor Availability** with status indicators

---

## Priority Scoring

Patients are prioritized using a weighted formula:

```
Priority = (triage_level * 0.4) + (vitals_score * 0.3) + (age_factor * 0.2) + (duration_factor * 0.1)
```

- **Triage level** (1-5): Higher = more critical
- **Vitals score**: Based on heart rate and blood pressure deviation from normal ranges
- **Age factor**: Patients under 12 or over 65 receive higher priority
- **Duration factor**: Longer symptom duration increases priority

---

## Database Schema

Key tables:

- `patients` — Patient demographics, vitals, symptoms, mood, triage level, priority score
- `doctors` — Doctor profiles with department and availability status
- `rooms` — Bed inventory by type (ICU, Emergency, Ward, Normal) with occupancy tracking
- `ongoing_cases` — Active patient-doctor-room assignments
- `queue` — Priority queue for patients when resources are unavailable

---

## Contact

**Noopur Shekhar Divekar** | [LinkedIn](https://www.linkedin.com/in/noopurd/) | [Email](mailto:noopur.div188@gmail.com)

---

## Links

- [Devpost Demo](https://devpost.com/software/shmas-smart-hospital-multi-agent-system)
- [GitHub Repository](https://github.com/noopurdiv/Smart-Hospital-Multi-Agent-AI-System)
