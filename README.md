# SHMAS: Smart Hospital Multi-Agent AI System
🏆 **Second Winner of the Luddy Hackathon** ---

## 📌 Inspiration

In the fast-paced world of healthcare, even the smallest delays in hospital operations can have life-or-death consequences. With multiple processes happening simultaneously—patient triage, resource allocation, and doctor scheduling—hospital workflows can quickly become overwhelmed. Our solution to this complex problem? **SHMAS (Smart Hospital Multi-Agent System).** This innovative system leverages the power of AI and multi-agent coordination to streamline hospital operations, reduce wait times, and ultimately enhance patient care. By automating and optimizing key tasks, SHMAS ensures that hospital staff can focus on providing care, rather than managing logistics.



---

## 🔗 Project Links
* **Product Demo:** [View on Devpost](https://devpost.com/software/shmas-smart-hospital-multi-agent-system)

---

## 🚀 What it does

*SHMAS* is an AI-driven system designed to automate and optimize hospital workflows using multiple autonomous agents. Each agent handles a specific part of operations, from triage to resource allocation.

### Key Features:
- **Mental Health State Detection**: Real-time medical data analysis for intelligent prioritization.
- **Agent Collaboration**: Five specialized agents sharing data and making real-time decisions.
- **Conflict Resolution**: Automated resource allocation logic during peak demand.
- **Priority Scoring Formula**: Dynamic algorithm prioritizing patients based on vitals, age, and symptoms.

### The Five Agents:
1. **Mental Health Analyzer**: Assesses conditions to prioritize cases by urgency.
2. **Triage Agent**: Directs patients to the appropriate department based on severity.
3. **Bed Manager**: Allocates hospital beds based on patient needs and real-time capacity.
4. **Doctor Scheduler**: Automates scheduling based on availability and patient requirements.
5. **Conflict Resolver**: Mediates resource contention between other agents.

<img width="425" alt="SHMAS Agent Flow" src="https://github.com/user-attachments/assets/c78942af-192d-40a0-8d4b-a0078233a150" />

---

## 🛠 How we built it

- **LangGraph**: Orchestrated the complex workflows and state transitions of our five-agent system.
- **Groq APIs**: Leveraged `deepseek-r1-distill-llama-70b` for high-speed, complex reasoning.
- **PostgreSQL**: Secured, high-consistency storage for real-time hospital data.
- **Priority Algorithm**: Custom logic factoring in vital signs and symptom severity for triage.

---

## 🚧 Challenges we ran into

* **Agent Orchestration**: Coordinating interdependencies required sophisticated state management. We used **LangGraph** to ensure smooth transitions and avoid logical deadlocks.
* **Conflict Resolution**: Peak demand created resource contention. We solved this via a variables-based **Priority Scoring System** (vitals, age, severity).
* **Real-Time Data Integrity**: To prevent race conditions between agents, we utilized **PostgreSQL transaction management** and database triggers.

---

## 🏆 Accomplishments & Learnings

* Successfully developed a fully autonomous **Conflict Resolution System** for resource allocation.
* Implemented five-agent collaboration using **LangGraph** for clear state transitions.
* Deepened understanding of **LLM Integration** for deterministic healthcare protocols using Groq.

---

## 🔮 What's next for SHMAS

- **Predictive Analytics**: Using ML to forecast patient flow and peak hours.
- **EHR Integration**: Connecting directly to Electronic Health Records for historical context.
- **Mobile Interface**: Enabling remote monitoring for hospital administrators.

---

## 👤 Contact
**Noopur Shekhar Divekar** | [LinkedIn](https://www.linkedin.com/in/noopurd/) | [Email](mailto:noopur.div188@gmail.com)
