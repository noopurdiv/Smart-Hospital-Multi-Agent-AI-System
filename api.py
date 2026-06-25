"""FastAPI backend wrapping the existing SHMAS agent pipeline."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from smart_hospital import run_patient_flow, get_doctor_status, get_beds

app = FastAPI(title="SHMAS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PatientRequest(BaseModel):
    name: str
    email: str
    gender: str
    age: int
    symptoms: List[str]
    symptom_duration: int
    vitals: dict


class PatientResponse(BaseModel):
    patient: dict
    logs: List[str]
    status: dict


@app.get("/api/doctors")
def doctors():
    try:
        return get_doctor_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/beds")
def beds():
    try:
        return get_beds()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admit", response_model=PatientResponse)
def admit_patient(req: PatientRequest):
    try:
        result = run_patient_flow(
            name=req.name,
            vitals=req.vitals,
            email=req.email,
            gender=req.gender,
            age=req.age,
            symptoms=req.symptoms,
            symptom_duration=req.symptom_duration,
        )
        return {
            "patient": result["patient"].to_dict(),
            "logs": result["logs"],
            "status": result["status"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
