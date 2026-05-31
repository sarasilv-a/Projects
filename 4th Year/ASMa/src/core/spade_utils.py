from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple
import jsonpickle
from spade.message import Message as SpadeMessage

# ---------- Serialization (Serialized Objects) ----------
def encode_payload(payload: Any) -> str:
    """
    Serializa payload para string.
    Preferimos jsonpickle (aguenta dataclasses/Enums/classes),
    mas mantemos output em formato JSON-like.
    """
    return jsonpickle.encode(payload, unpicklable=True)

def decode_payload(body: Optional[str]) -> Any:
    """Desserializa o body para objeto."""
    if not body:
        return None
    try:
        return jsonpickle.decode(body)
    except Exception:
        # fallback simples
        try:
            return json.loads(body)
        except Exception:
            return body

# ---------- SPADE message helpers ----------
def build_spade_message(
    to: str,
    performative: str,
    msg_type: str,
    payload: Any,
    *,
    sender: Optional[str] = None,
    conversation_id: Optional[str] = None,
) -> SpadeMessage:
    """
    Cria uma mensagem SPADE com metadata (performative + type) e body serializado.
    """
    msg = SpadeMessage(to=to)
    if sender:
        msg.sender = sender
    msg.set_metadata("performative", getattr(performative, "value", str(performative)))
    msg.set_metadata("type", getattr(msg_type, "value", str(msg_type)))


    if conversation_id:
        msg.set_metadata("conversation_id", conversation_id)

    msg.body = encode_payload(payload)
    return msg


def parse_spade_message(msg: SpadeMessage) -> Tuple[str, str, Any, Dict[str, str]]:
    """
    Extrai (performative, type, payload, metadata) de uma mensagem SPADE.
    """
    metadata = dict(msg.metadata or {})
    performative = metadata.get("performative", "")
    msg_type = metadata.get("type", "")
    payload = decode_payload(msg.body)
    return performative, msg_type, payload, metadata
