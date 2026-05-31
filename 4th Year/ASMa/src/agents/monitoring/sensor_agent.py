from __future__ import annotations

from spade.agent import Agent
from core.utils import logger
from behaviours.monitoring.sensor.sensor_send_vitals import SensorSendVitalsBehaviour

class SensorAgent(Agent):
    def __init__(self, jid: str, password: str, *, patient_id: str):
        super().__init__(jid, password)
        self.patient_id = patient_id

    async def setup(self):
        self.add_behaviour(SensorSendVitalsBehaviour(period=1))
        logger.info(f"[SENSOR] Agent started: {self.jid} patient_id={self.patient_id}")
