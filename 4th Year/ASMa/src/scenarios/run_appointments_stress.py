from __future__ import annotations
import asyncio
from core.config import account
from agents.appointments.scheduler_agent import SchedulerAgent
from agents.appointments.doctor_agent import DoctorAgent
from agents.support.chatbot_patient_agent import ChatbotPatientAgent

def banner():
    print("=" * 70)
    print("DEMO: APPOINTMENTS STRESS (many chatbot patients + doctors)")
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

    scheduler = None
    doctors = []
    chatbots = []
    RUN_SECONDS = 50

    try:
        sched_acc = account("scheduler")
        scheduler = SchedulerAgent(sched_acc.jid, sched_acc.password)
        await scheduler.start()

        # 6 doctors
        specs = ["cardiology", "general", "general", "general", "general", "cardiology"]
        for idx, spec in enumerate(specs, start=1):
            username = "doctor" if idx == 1 else f"doctor{idx}"
            acc = account(username)
            d = DoctorAgent(acc.jid, acc.password, specialty=spec)
            doctors.append(d)
            await d.start()

        # 3 pacientes chatbot
        for idx, username in enumerate(["chatbot_patient", "chatbot_patient2", "chatbot_patient3"], start=1):
            acc = account(username)
            cb = ChatbotPatientAgent(acc.jid, acc.password, patient_id=f"P-CHAT-{idx}")
            chatbots.append(cb)
            await cb.start()
            await asyncio.sleep(0.3)

        await asyncio.sleep(RUN_SECONDS)

    finally:
        for idx, cb in enumerate(chatbots, start=1):
            await safe_stop(cb, name=f"chatbot{idx}")
        for idx, d in enumerate(doctors, start=1):
            await safe_stop(d, name=f"doctor{idx}")
        await safe_stop(scheduler, name="scheduler")
        print("[APPOINTMENTS STRESS] finished")
        await asyncio.sleep(0.5)
        raise SystemExit(0)


if __name__ == "__main__":
    asyncio.run(main())
