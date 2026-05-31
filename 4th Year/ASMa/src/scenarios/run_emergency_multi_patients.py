from __future__ import annotations
import asyncio
from core.config import account, AMBULANCE_JIDS, HELICOPTER_JIDS, HOSPITAL_JIDS
from agents.emergency.emergency_center_agent import EmergencyCenterAgent
from agents.emergency.triage_agent import TriageAgent
from agents.emergency.hospital_agent import HospitalAgent
from agents.emergency.ambulance_agent import AmbulanceAgent
from agents.emergency.helicopter_agent import HelicopterAgent
from agents.emergency.patient_agent import PatientAgent


def banner():
    print("=" * 70)
    print("DEMO: EMERGENCY MULTI PATIENTS (3 patients concurrent)")
    print("=" * 70)
    print()


async def safe_stop(agent, *, name: str = "", timeout: float = 5.0):
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

    center = triage = None
    hospitals, ambulances, helicopters = [], [], []
    patients = []
    RUN_SECONDS = 45

    try:
        center_acc = account("emergency_center")
        center = EmergencyCenterAgent(center_acc.jid, center_acc.password)
        await center.start()

        triage_acc = account("triage")
        triage = TriageAgent(triage_acc.jid, triage_acc.password)
        await triage.start()

        # infra mínima
        for i, _ in enumerate(HOSPITAL_JIDS[:2], start=1):
            acc = account("hospital" if i == 1 else f"hospital{i}")
            a = HospitalAgent(acc.jid, acc.password)
            hospitals.append(a)
            await a.start()

        for i, _ in enumerate(AMBULANCE_JIDS[:2], start=1):
            acc = account("ambulance" if i == 1 else f"ambulance{i}")
            a = AmbulanceAgent(acc.jid, acc.password)
            ambulances.append(a)
            await a.start()

        for i, _ in enumerate(HELICOPTER_JIDS[:1], start=1):
            acc = account("helicopter" if i == 1 else f"helicopter{i}")
            a = HelicopterAgent(acc.jid, acc.password)
            helicopters.append(a)
            await a.start()

        # 3 pacientes
        patient_users = ["patient_emergency", "patient_emergency2", "patient_emergency3"]
        for idx, username in enumerate(patient_users, start=1):
            acc = account(username)
            p = PatientAgent(acc.jid, acc.password, patient_id=f"P{idx:03d}", name=f"Patient{idx}")
            patients.append(p)
            await p.start()
            await asyncio.sleep(0.4)  # pequeno desfasamento

        await asyncio.sleep(RUN_SECONDS)

    finally:
        for idx, p in enumerate(patients, start=1):
            await safe_stop(p, name=f"patient{idx}")

        for idx, h in enumerate(helicopters, start=1):
            await safe_stop(h, name=f"helicopter{idx}")
        for idx, a in enumerate(ambulances, start=1):
            await safe_stop(a, name=f"ambulance{idx}")
        for idx, h in enumerate(hospitals, start=1):
            await safe_stop(h, name=f"hospital{idx}")

        await safe_stop(triage, name="triage")
        await safe_stop(center, name="center")
        print("[EMERGENCY MULTI] finished")
        await asyncio.sleep(0.5)
        raise SystemExit(0)


if __name__ == "__main__":
    asyncio.run(main())
