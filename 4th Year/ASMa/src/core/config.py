from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Carrega .env
load_dotenv()

# =========================
# XMPP / Openfire settings
# =========================
XMPP_DOMAIN = os.getenv("XMPP_DOMAIN", "localhost")          # ex: win-ie3cff71up4
XMPP_HOST = os.getenv("XMPP_HOST", "localhost")              # ex: localhost
XMPP_PORT = int(os.getenv("XMPP_PORT", "5222"))              # default 5222
XMPP_PASSWORD = os.getenv("XMPP_PASSWORD", "password123")    # password comum


def jid(username: str) -> str:
    """Constrói um JID completo a partir do username."""
    return f"{username}@{XMPP_DOMAIN}"


# =========================
# Agent JIDs
# =========================
PATIENT_EMERGENCY_JID = jid("patient_emergency")
EMERGENCY_CENTER_JID = jid("emergency_center")
TRIAGE_JID = jid("triage")

AMBULANCE_JID = jid("ambulance")
HELICOPTER_JID = jid("helicopter")
HOSPITAL_JID = jid("hospital")

CHATBOT_JID = jid("chatbot_patient")
SCHEDULER_JID = jid("scheduler")
DOCTOR_JID = jid("doctor")

SENSOR_JID = jid("sensor")
MONITORING_JID = jid("monitoring")

# =========================
# Agent JIDs (multi-instância)
# =========================
AMBULANCE_JIDS = [jid("ambulance"), jid("ambulance2")]
HELICOPTER_JIDS = [jid("helicopter"), jid("helicopter2")]
HOSPITAL_JIDS = [jid("hospital"), jid("hospital2")]

DOCTOR_JIDS = [jid("doctor"), jid("doctor2"), jid("doctor3"), jid("doctor4")]

# =========================
# Passwords
# =========================
def _pw(env_key: str) -> str:
    return os.getenv(env_key, XMPP_PASSWORD)


PASSWORDS = {
    "patient_emergency": _pw("PATIENT_EMERGENCY_PW"),
    "emergency_center": _pw("EMERGENCY_CENTER_PW"),
    "triage": _pw("TRIAGE_PW"),

    "ambulance": _pw("AMBULANCE_PW"),
    "ambulance2": _pw("AMBULANCE2_PW"),

    "helicopter": _pw("HELICOPTER_PW"),
    "helicopter2": _pw("HELICOPTER2_PW"),

    "hospital": _pw("HOSPITAL_PW"),
    "hospital2": _pw("HOSPITAL2_PW"),

    "chatbot_patient": _pw("CHATBOT_PW"),
    "scheduler": _pw("SCHEDULER_PW"),

    "doctor": _pw("DOCTOR_PW"),
    "doctor2": _pw("DOCTOR2_PW"),
    "doctor3": _pw("DOCTOR3_PW"),
    "doctor4": _pw("DOCTOR4_PW"),

    "sensor": _pw("SENSOR_PW"),
    "monitoring": _pw("MONITORING_PW"),
}

# =========================
# Logging & misc
# =========================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "sma_saude.log")

DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30"))
MESSAGE_RETRY_ATTEMPTS = int(os.getenv("MESSAGE_RETRY_ATTEMPTS", "3"))
MESSAGE_RETRY_DELAY = int(os.getenv("MESSAGE_RETRY_DELAY", "2"))  # seconds

@dataclass(frozen=True)
class XmppAccount:
    jid: str
    password: str


def account(username: str) -> XmppAccount:
    """Retorna conta (jid+password) para um username do sistema.

    Se não existir entry em PASSWORDS, usa XMPP_PASSWORD.
    """
    return XmppAccount(jid=jid(username), password=PASSWORDS.get(username, XMPP_PASSWORD))
