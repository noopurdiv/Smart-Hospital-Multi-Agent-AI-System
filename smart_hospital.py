from langgraph.graph import StateGraph, END
from agents import (
    AgentState,
    Patient,
    MentalHealthAnalyzerAgent,
    EmergencyTriageAgent,
    DoctorSchedulerAgent,
    BedManagerAgent,
    ConflictResolverAgent,
    get_doctor_status,
    get_beds,
)

graph = StateGraph(AgentState)
graph.add_node("mood", MentalHealthAnalyzerAgent())
graph.add_node("triage", EmergencyTriageAgent())
graph.add_node("doctor", DoctorSchedulerAgent())
graph.add_node("bed", BedManagerAgent())
graph.add_node("checker", ConflictResolverAgent())

graph.set_entry_point("mood")
graph.add_edge("mood", "triage")
graph.add_edge("triage", "doctor")
graph.add_edge("doctor", "bed")
graph.add_edge("bed", "checker")
graph.add_edge("checker", END)

smart_hospital_graph = graph.compile()


def run_patient_flow(name, vitals, email, gender, age, symptoms, symptom_duration):
    patient = Patient(name, vitals, email, gender, age, symptoms, symptom_duration)
    state = {
        "patient": patient,
        "logs": [],
        "status": {
            "MoodAnalyzer": "Pending",
            "EmergencyTriage": "Pending",
            "DoctorScheduler": "Pending",
            "BedManager": "Pending",
            "ConflictResolver": "Pending",
        },
        "cache": {},
    }
    result = smart_hospital_graph.invoke(state)
    return result
