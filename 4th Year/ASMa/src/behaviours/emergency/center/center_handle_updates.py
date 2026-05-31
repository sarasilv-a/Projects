from __future__ import annotations

from spade.behaviour import CyclicBehaviour
from core.config import AMBULANCE_JIDS, HELICOPTER_JIDS, HOSPITAL_JIDS
from core.protocols import Performative, EmergencyMsg, TransportType
from core.spade_utils import build_spade_message, parse_spade_message
from core.utils import logger, get_current_time

class HandleUpdatesBehaviour(CyclicBehaviour):
    async def _notify_patient_resolved(self, rec, emergency_id: str):
        patient_jid = rec.get("patient_jid")
        if not patient_jid:
            return
        resolved_payload = {
            "emergency_id": emergency_id,
            "status": "resolved",
            "timestamp": get_current_time(),
        }
        resolved = build_spade_message(
            to=patient_jid,
            performative=Performative.INFORM,
            msg_type=EmergencyMsg.EMERGENCY_RESOLVED,
            payload=resolved_payload,
        )
        await self.send(resolved)

    async def _dispatch_transport(self, emergency_id: str, rec: dict, *, transport_type: str, transport_jid: str, hospital_jid: str, reroute: bool = False):
        base = rec["payload"]
        dispatch_payload = {
            "emergency_id": emergency_id,
            "patient_id": base.get("patient_id"),
            "patient_jid": rec.get("patient_jid"),
            "location": base.get("location"),
            "severity": base.get("severity"),
            "vitals": base.get("vitals", {}),
            "transport_type": transport_type,
            "required_specialty": rec.get("required_specialty", "general"),
            "hospital_jid": hospital_jid,
            "timestamp": get_current_time(),
            "reroute": bool(reroute),
        }
        dispatch = build_spade_message(
            to=transport_jid,
            performative=Performative.REQUEST,
            msg_type=EmergencyMsg.TRANSPORT_DISPATCH,
            payload=dispatch_payload,
        )
        await self.send(dispatch)
        rec["status"] = "dispatched"
        rec["transport_type"] = transport_type
        rec["transport_jid"] = transport_jid
        rec["hospital_jid"] = hospital_jid

    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return

        perf, mtype, payload, _meta = parse_spade_message(msg)
        emergency_id = payload.get("emergency_id")

        if not emergency_id or emergency_id not in self.agent.active_emergencies:
            return

        rec = self.agent.active_emergencies[emergency_id]

        # Guardar um log do último update
        rec["last_update"] = {"type": mtype, "perf": perf, "payload": payload, "ts": get_current_time()}

        # 1) TRANSPORT_ACCEPT (apenas informativo)
        if mtype == EmergencyMsg.TRANSPORT_ACCEPT.value:
            rec["status"] = "transport_accepted"
            return

        # 2) TRANSPORT_JOB_DONE (não fecha emergência)
        if mtype == EmergencyMsg.TRANSPORT_JOB_DONE.value:
            # agora só serve para métricas/visibilidade
            rec["transport_job_done"] = payload
            return

        # 3) PATIENT_ADMITTED -> FECHA a emergência
        if mtype == EmergencyMsg.PATIENT_ADMITTED.value:
            rec["status"] = "admitted"
            await self._notify_patient_resolved(rec, emergency_id)
            self.agent.active_emergencies.pop(emergency_id, None)
            logger.info(f"[CENTER] Emergency resolved/closed (admitted): {emergency_id}")
            return

        # 4) PATIENT_REFUSED -> tenta outro hospital (se hospital_full)
        if mtype == EmergencyMsg.PATIENT_REFUSED.value:
            status = payload.get("status")
            rec["status"] = f"refused:{status or 'unknown'}"

            # hospital_full -> tenta outro hospital (reroute)
            if status == "hospital_full":
                rec.setdefault("tried_hospitals", [])
                old_hospital = rec.get("hospital_jid")
                if old_hospital and old_hospital not in rec["tried_hospitals"]:
                    rec["tried_hospitals"].append(old_hospital)

                new_hospital = self.agent.pick_hospital(HOSPITAL_JIDS, avoid=rec["tried_hospitals"])
                if new_hospital:
                    rec["tried_hospitals"].append(new_hospital)
                    transport_jid = rec.get("transport_jid")
                    transport_type = rec.get("transport_type", TransportType.AMBULANCE.value)
                    if transport_jid:
                        await self._dispatch_transport(
                            emergency_id,
                            rec,
                            transport_type=transport_type,
                            transport_jid=transport_jid,
                            hospital_jid=new_hospital,
                            reroute=True,
                        )
                        logger.warning(
                            f"[CENTER] hospital_full -> reroute emergency_id={emergency_id} transport={transport_jid} hospital={new_hospital}"
                        )
                        return

                # sem hospitais alternativos
                rec["status"] = "awaiting_capacity"
                logger.warning(f"[CENTER] hospital_full and no alternative hospital: emergency_id={emergency_id}")
                return

            # outra recusa (não recuperável) -> fecha
            await self._notify_patient_resolved(rec, emergency_id)
            self.agent.active_emergencies.pop(emergency_id, None)
            logger.info(f"[CENTER] Emergency resolved/closed (refused): {emergency_id}")
            return

        # 5) TRANSPORT_REFUSE -> fallback helicopter->ambulance + round-robin
        if mtype == EmergencyMsg.TRANSPORT_REFUSE.value:
            reason = payload.get("reason")
            rec["status"] = f"transport_refused:{reason or 'unknown'}"

            desired = rec.get("transport_type", TransportType.AMBULANCE.value)
            hospital_jid = rec.get("hospital_jid") or (HOSPITAL_JIDS[0] if HOSPITAL_JIDS else None)
            if not hospital_jid:
                rec["status"] = "awaiting_capacity"
                return

            # se helicóptero ocupado -> tenta outro helicóptero, senão ambulância
            if desired == TransportType.HELICOPTER.value:
                other_heli = self.agent.pick_helicopter(HELICOPTER_JIDS)
                if other_heli and other_heli != rec.get("transport_jid"):
                    await self._dispatch_transport(
                        emergency_id, rec,
                        transport_type=TransportType.HELICOPTER.value,
                        transport_jid=other_heli,
                        hospital_jid=hospital_jid,
                    )
                    logger.warning(f"[CENTER] helicopter_busy -> trying another helicopter {other_heli} for {emergency_id}")
                    return

                amb = self.agent.pick_ambulance(AMBULANCE_JIDS)
                if amb:
                    await self._dispatch_transport(
                        emergency_id, rec,
                        transport_type=TransportType.AMBULANCE.value,
                        transport_jid=amb,
                        hospital_jid=hospital_jid,
                    )
                    logger.warning(f"[CENTER] helicopter_busy -> fallback ambulance {amb} for {emergency_id}")
                    return

            # se ambulância ocupada -> tenta outra ambulância, senão helicóptero
            if desired == TransportType.AMBULANCE.value:
                other_amb = self.agent.pick_ambulance(AMBULANCE_JIDS)
                if other_amb and other_amb != rec.get("transport_jid"):
                    await self._dispatch_transport(
                        emergency_id, rec,
                        transport_type=TransportType.AMBULANCE.value,
                        transport_jid=other_amb,
                        hospital_jid=hospital_jid,
                    )
                    logger.warning(f"[CENTER] ambulance_busy -> trying another ambulance {other_amb} for {emergency_id}")
                    return

                heli = self.agent.pick_helicopter(HELICOPTER_JIDS)
                if heli:
                    await self._dispatch_transport(
                        emergency_id, rec,
                        transport_type=TransportType.HELICOPTER.value,
                        transport_jid=heli,
                        hospital_jid=hospital_jid,
                    )
                    logger.warning(f"[CENTER] ambulance_busy -> fallback helicopter {heli} for {emergency_id}")
                    return

            rec["status"] = "awaiting_transport"
            logger.warning(f"[CENTER] No transport available after refuse: emergency_id={emergency_id}")
