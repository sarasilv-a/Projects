from __future__ import annotations

import asyncio
from core.config import (
    account,
    AMBULANCE_JIDS,
    HELICOPTER_JIDS,
    HOSPITAL_JIDS,
)
from agents.emergency.emergency_center_agent import EmergencyCenterAgent
from agents.emergency.triage_agent import TriageAgent
from agents.emergency.hospital_agent import HospitalAgent
from agents.emergency.ambulance_agent import AmbulanceAgent
from agents.emergency.helicopter_agent import HelicopterAgent
from agents.monitoring.monitoring_agent import MonitoringAgent
from agents.monitoring.sensor_agent import SensorAgent
from agents.support.chatbot_patient_agent import ChatbotPatientAgent
from agents.appointments.scheduler_agent import SchedulerAgent
from agents.appointments.doctor_agent import DoctorAgent
from agents.emergency.patient_agent import PatientAgent

def banner():
    print("=" * 70)
    print("DEMO: FULL SYSTEM (emergency + monitoring + chatbot + appointments + specialists)")
    print("=" * 70)
    print()
    print("Note: This demo starts ONE agent per Openfire user/JID.")
    print()

async def safe_stop(agent, *, name: str = "", timeout: float = 5.0):
    """Tenta parar um agente com timeout para não ficar pendurado."""
    if agent is None:
        return
    try:
        await asyncio.wait_for(agent.stop(), timeout=timeout)
    except asyncio.TimeoutError:
        print(f"[STOP] timeout a parar {name or str(agent)} (continuo...)")
    except Exception as e:
        print(f"[STOP] erro a parar {name or str(agent)}: {e}")

async def main():
    banner()

    center = triage = scheduler = monitoring = sensor = chatbot = patient = None
    hospitals = []
    ambulances = []
    helicopters = []
    doctors = []

    RUN_SECONDS = 40

    try:
        # -------------------------
        # Emergency subsystem
        # -------------------------
        center_acc = account("emergency_center")
        center = EmergencyCenterAgent(center_acc.jid, center_acc.password)
        await center.start()

        triage_acc = account("triage")
        triage = TriageAgent(triage_acc.jid, triage_acc.password)
        await triage.start()

        # 2 hospitals, 2 ambulances, 2 helicopters
        for i, _ in enumerate(HOSPITAL_JIDS, start=1):
            username = "hospital" if i == 1 else f"hospital{i}"
            acc = account(username)
            a = HospitalAgent(acc.jid, acc.password)
            hospitals.append(a)
            await a.start()

        for i, _ in enumerate(AMBULANCE_JIDS, start=1):
            username = "ambulance" if i == 1 else f"ambulance{i}"
            acc = account(username)
            a = AmbulanceAgent(acc.jid, acc.password)
            ambulances.append(a)
            await a.start()

        for i, _ in enumerate(HELICOPTER_JIDS, start=1):
            username = "helicopter" if i == 1 else f"helicopter{i}"
            acc = account(username)
            a = HelicopterAgent(acc.jid, acc.password)
            helicopters.append(a)
            await a.start()

        # -------------------------
        # Appointments subsystem
        # -------------------------
        sched_acc = account("scheduler")
        scheduler = SchedulerAgent(sched_acc.jid, sched_acc.password)
        await scheduler.start()

        # 4 doctors:
        doctor_specs = ["cardiology", "general", "general", "general"]
        for idx, spec in enumerate(doctor_specs, start=1):
            username = "doctor" if idx == 1 else f"doctor{idx}"
            acc = account(username)
            d = DoctorAgent(acc.jid, acc.password, specialty=spec)
            doctors.append(d)
            await d.start()

        # -------------------------
        # Monitoring subsystem
        # -------------------------
        mon_acc = account("monitoring")
        monitoring = MonitoringAgent(mon_acc.jid, mon_acc.password, alert_cooldown_seconds=20)
        await monitoring.start()

        sensor_acc = account("sensor")
        sensor = SensorAgent(sensor_acc.jid, sensor_acc.password, patient_id="P-MON")
        await sensor.start()

        # -------------------------
        # Chatbot subsystem
        # -------------------------
        chatbot_acc = account("chatbot_patient")
        chatbot = ChatbotPatientAgent(chatbot_acc.jid, chatbot_acc.password, patient_id="P-CHAT")
        await chatbot.start()

        # -------------------------
        # One example emergency patient
        # -------------------------
        pat_acc = account("patient_emergency")
        patient = PatientAgent(
            pat_acc.jid,
            pat_acc.password,
            patient_id="P001",
            name="Alice",
        )
        await patient.start()

        await asyncio.sleep(RUN_SECONDS)

    finally:
        # stop everything (com timeout para garantir que não fica infinito)
        await safe_stop(patient, name="patient")
        await safe_stop(chatbot, name="chatbot")
        await safe_stop(sensor, name="sensor")
        await safe_stop(monitoring, name="monitoring")

        for idx, d in enumerate(doctors, start=1):
            await safe_stop(d, name=f"doctor{idx}")
        await safe_stop(scheduler, name="scheduler")

        for idx, h in enumerate(helicopters, start=1):
            await safe_stop(h, name=f"helicopter{idx}")
        for idx, a in enumerate(ambulances, start=1):
            await safe_stop(a, name=f"ambulance{idx}")
        for idx, h in enumerate(hospitals, start=1):
            await safe_stop(h, name=f"hospital{idx}")

        await safe_stop(triage, name="triage")
        await safe_stop(center, name="center")

        print("[FULL DEMO] finished")

        await asyncio.sleep(0.5)

        # Hard-exit para evitar o "fica a correr para sempre" do runtime SPADE
        raise SystemExit(0)


if __name__ == "__main__":
    asyncio.run(main())
