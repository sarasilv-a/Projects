from __future__ import annotations

import asyncio
from spade.behaviour import CyclicBehaviour
from core.protocols import Performative, EmergencyMsg, TransportType
from core.spade_utils import build_spade_message, parse_spade_message
from core.utils import logger, get_current_time

class HelicopterHandleDispatchBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return

        _perf, mtype, payload, _meta = parse_spade_message(msg)
        if mtype != EmergencyMsg.TRANSPORT_DISPATCH.value:
            return

        # Só processa se for helicóptero
        if payload.get("transport_type") != TransportType.HELICOPTER.value:
            return

        sender_center = str(msg.sender)
        emergency_id = payload.get("emergency_id")
        hospital_jid = payload.get("hospital_jid")

        # REROUTE: se já estamos a tratar este emergency_id, aceitamos "novo hospital" mesmo estando ocupados
        if (not self.agent.available) and (emergency_id == self.agent.current_emergency_id):
            incoming_payload = {
                "emergency_id": emergency_id,
                "patient_id": payload.get("patient_id"),
                "location": payload.get("location"),
                "severity": payload.get("severity"),
                "vitals": payload.get("vitals", {}),
                "required_specialty": payload.get("required_specialty"),
                "timestamp": get_current_time(),
                "transport_type": TransportType.HELICOPTER.value,
                "reroute": True,
            }
            to_hospital = build_spade_message(
                to=hospital_jid,
                performative=Performative.INFORM,
                msg_type=EmergencyMsg.PATIENT_INCOMING,
                payload=incoming_payload,
            )
            await self.send(to_hospital)
            logger.info(f"[HELICOPTER] REROUTE emergency_id={emergency_id} -> hospital={hospital_jid}")
            return

        # Ocupado com outro caso -> recusa
        if not self.agent.available:
            refuse_payload = {
                "emergency_id": emergency_id,
                "reason": "helicopter_busy",
                "timestamp": get_current_time(),
            }
            refuse = build_spade_message(
                to=sender_center,
                performative=Performative.REFUSE,
                msg_type=EmergencyMsg.TRANSPORT_REFUSE,
                payload=refuse_payload,
            )
            await self.send(refuse)
            logger.warning(f"[HELICOPTER] REFUSE transport_dispatch: {refuse_payload}")
            return

        # aceitar
        self.agent.available = False
        self.agent.current_emergency_id = emergency_id
        self.agent.center_jid = sender_center

        accept_payload = {"emergency_id": emergency_id, "timestamp": get_current_time()}
        accept = build_spade_message(
            to=sender_center,
            performative=Performative.CONFIRM,
            msg_type=EmergencyMsg.TRANSPORT_ACCEPT,
            payload=accept_payload,
        )
        await self.send(accept)

        # simula deslocação mais rápida
        await asyncio.sleep(2)

        # avisar hospital
        incoming_payload = {
            "emergency_id": emergency_id,
            "patient_id": payload.get("patient_id"),
            "location": payload.get("location"),
            "severity": payload.get("severity"),
            "vitals": payload.get("vitals", {}),
            "required_specialty": payload.get("required_specialty"),
            "timestamp": get_current_time(),
            "transport_type": TransportType.HELICOPTER.value,
        }
        to_hospital = build_spade_message(
            to=hospital_jid,
            performative=Performative.INFORM,
            msg_type=EmergencyMsg.PATIENT_INCOMING,
            payload=incoming_payload,
        )
        await self.send(to_hospital)
