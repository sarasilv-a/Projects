from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, List
from core.protocols import TransportType, MedicalSpecialty

# ----------------------------
# Estados
# ----------------------------
class EmergencyStatus(str, Enum):
    RECEIVED = "received"
    ACKNOWLEDGED = "acknowledged"
    TRIAGED = "triaged"
    DISPATCHED = "dispatched"
    IN_TRANSIT = "in_transit"
    ADMITTED = "admitted"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"

class TransportStatus(str, Enum):
    AVAILABLE = "available"
    DISPATCHED = "dispatched"
    AT_SCENE = "at_scene"
    IN_TRANSIT = "in_transit"
    AT_HOSPITAL = "at_hospital"
    DONE = "done"

class AppointmentStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# ----------------------------
# Estruturas de payload (tipadas)
# ----------------------------
@dataclass
class Vitals:
    hr: int
    spo2: int
    bp: str  # "120/80"

    def to_dict(self) -> Dict[str, Any]:
        return {"hr": self.hr, "spo2": self.spo2, "bp": self.bp}

@dataclass
class EmergencyAlertPayload:
    patient_id: str
    patient_name: str
    emergency_id: str
    location: str
    severity: int
    description: str
    vitals: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    source: str = "patient"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "patient_id": self.patient_id,
            "patient_name": self.patient_name,
            "emergency_id": self.emergency_id,
            "location": self.location,
            "severity": self.severity,
            "description": self.description,
            "vitals": self.vitals,
            "timestamp": self.timestamp,
            "source": self.source,
        }

@dataclass
class TriageResult:
    emergency_id: str
    severity: int
    priority: int
    transport_type: TransportType
    required_specialty: MedicalSpecialty
    notes: str = ""
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "emergency_id": self.emergency_id,
            "severity": self.severity,
            "priority": self.priority,
            "transport_type": self.transport_type.value,
            "required_specialty": self.required_specialty.value,
            "notes": self.notes,
            "timestamp": self.timestamp,
        }

@dataclass
class TransportDispatch:
    emergency_id: str
    patient_id: str
    patient_jid: str
    location: str
    transport_type: TransportType
    severity: int
    required_specialty: MedicalSpecialty
    vitals: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "emergency_id": self.emergency_id,
            "patient_id": self.patient_id,
            "patient_jid": self.patient_jid,
            "location": self.location,
            "transport_type": self.transport_type.value,
            "severity": self.severity,
            "required_specialty": self.required_specialty.value,
            "vitals": self.vitals,
            "timestamp": self.timestamp,
        }

@dataclass
class SpecialistRequest:
    emergency_id: str
    hospital_jid: str
    required_specialty: MedicalSpecialty
    priority: int = 0
    notes: str = ""
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "emergency_id": self.emergency_id,
            "hospital_jid": self.hospital_jid,
            "required_specialty": self.required_specialty.value,
            "priority": self.priority,
            "notes": self.notes,
            "timestamp": self.timestamp,
        }
