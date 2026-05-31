from __future__ import annotations
from enum import Enum

class Performative(str, Enum):
    REQUEST = "request"
    INFORM = "inform"
    CONFIRM = "confirm"
    REFUSE = "refuse"

# ----------------------------
# Emergências
# ----------------------------
class EmergencyMsg(str, Enum):
    EMERGENCY_ALERT = "emergency_alert"                 # REQUEST
    EMERGENCY_ACK = "emergency_acknowledged"            # INFORM
    EMERGENCY_STATUS_REQ = "emergency_status"           # REQUEST
    EMERGENCY_STATUS = "emergency_status"               # INFORM
    EMERGENCY_RESOLVED = "emergency_resolved"           # INFORM

    TRIAGE_CASE = "triage_case"                         # REQUEST
    TRIAGE_RESULT = "triage_result"                     # INFORM

    TRANSPORT_DISPATCH = "transport_dispatch"           # REQUEST (ambulance/helicopter)
    TRANSPORT_ACCEPT = "transport_accept"               # CONFIRM
    TRANSPORT_REFUSE = "transport_refuse"               # REFUSE
    TRANSPORT_DISPATCHED = "transport_dispatched"       # INFORM
    TRANSPORT_JOB_DONE = "transport_job_done"           # INFORM

    PATIENT_INCOMING = "patient_incoming"               # INFORM (para hospital)
    PATIENT_ADMITTED = "patient_admitted"               # CONFIRM (hospital -> transport/center)
    PATIENT_REFUSED = "patient_refused"                 # REFUSE

# ----------------------------
# Especialistas / tratamento
# ----------------------------
class SpecialistMsg(str, Enum):
    SPECIALIST_REQUEST = "specialist_request"           # REQUEST (hospital -> coordinator)
    SPECIALIST_ASSIGNED = "specialist_assigned"         # INFORM (coordinator -> hospital)
    TREATMENT_UPDATE = "treatment_update"               # INFORM (doctor -> hospital)

# ----------------------------
# Consultas (appointments)
# ----------------------------
class AppointmentMsg(str, Enum):
    APPOINTMENT_REQUEST = "appointment_request"         # REQUEST
    APPOINTMENT_QUEUED = "appointment_queued"           # INFORM
    DOCTOR_AVAILABLE = "doctor_available"               # INFORM
    DOCTOR_ASSIGN = "doctor_assign"                     # REQUEST
    APPOINTMENT_SCHEDULED = "appointment_scheduled"     # INFORM
    APPOINTMENT_COMPLETED = "appointment_completed"     # INFORM
    DOCTOR_DONE = "doctor_done"                         # INFORM

# ----------------------------
# Monitoring
# ----------------------------
class MonitoringMsg(str, Enum):
    VITALS_UPDATE = "vitals_update"                     # INFORM

# ----------------------------
# Enums de decisão
# ----------------------------
class TransportType(str, Enum):
    AMBULANCE = "ambulance"
    HELICOPTER = "helicopter"

class MedicalSpecialty(str, Enum):
    GENERAL = "general"
    CARDIOLOGY = "cardiology"
    DERMATOLOGY = "dermatology"
    NEUROLOGY = "neurology"
    ORTHOPEDICS = "orthopedics"
