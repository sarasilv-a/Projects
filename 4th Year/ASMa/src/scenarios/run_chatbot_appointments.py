from __future__ import annotations
import asyncio
from core.config import account
from agents.support.chatbot_patient_agent import ChatbotPatientAgent
from agents.appointments.scheduler_agent import SchedulerAgent
from agents.appointments.doctor_agent import DoctorAgent

def banner():
    print("=" * 70)
    print("DEMO: CHATBOT + APPOINTMENTS (chatbot_patient -> scheduler -> doctors)")
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

    scheduler = chatbot = None
    doctors = []
    RUN_SECONDS = 40

    try:
        sched_acc = account("scheduler")
        scheduler = SchedulerAgent(sched_acc.jid, sched_acc.password)
        await scheduler.start()

        # doctors
        doctor_specs = ["cardiology", "general", "general", "general"]
        for idx, spec in enumerate(doctor_specs, start=1):
            username = "doctor" if idx == 1 else f"doctor{idx}"
            acc = account(username)
            d = DoctorAgent(acc.jid, acc.password, specialty=spec)
            doctors.append(d)
            await d.start()

        chatbot_acc = account("chatbot_patient")
        chatbot = ChatbotPatientAgent(chatbot_acc.jid, chatbot_acc.password, patient_id="P-CHAT")
        await chatbot.start()

        await asyncio.sleep(RUN_SECONDS)

    finally:
        await safe_stop(chatbot, name="chatbot")
        for idx, d in enumerate(doctors, start=1):
            await safe_stop(d, name=f"doctor{idx}")
        await safe_stop(scheduler, name="scheduler")
        print("[CHATBOT APPOINTMENTS] finished")
        await asyncio.sleep(0.5)
        raise SystemExit(0)


if __name__ == "__main__":
    asyncio.run(main())
