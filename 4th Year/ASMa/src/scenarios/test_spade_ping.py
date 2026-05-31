from __future__ import annotations

import asyncio
import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.abspath(os.path.join(_THIS_DIR, ".."))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.template import Template

from core.config import account
from core.protocols import Performative
from core.spade_utils import build_spade_message, parse_spade_message
from core.utils import logger, get_current_time


PING_TYPE = "ping"
PONG_TYPE = "pong"


class PingReceiverAgent(Agent):
    async def setup(self):
        tpl = Template()
        tpl.set_metadata("type", PING_TYPE)
        self.add_behaviour(ReceivePingBehaviour(), tpl)
        logger.info("[PING-RECEIVER] ready")


class ReceivePingBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return

        perf, mtype, payload, _meta = parse_spade_message(msg)
        logger.info(f"[PING-RECEIVER] got perf={perf} type={mtype} payload={payload}")

        reply = build_spade_message(
            to=str(msg.sender),
            performative=Performative.INFORM,
            msg_type=PONG_TYPE,
            payload={"ts": get_current_time(), "echo": payload},
        )
        await self.send(reply)


class PingSenderAgent(Agent):
    async def setup(self):
        tpl = Template()
        tpl.set_metadata("type", PONG_TYPE)
        self.add_behaviour(WaitPongBehaviour(), tpl)
        self.add_behaviour(SendPingBehaviour())
        logger.info("[PING-SENDER] ready")


class SendPingBehaviour(OneShotBehaviour):
    async def run(self):
        msg = build_spade_message(
            to=str(self.agent.receiver_jid),
            performative=Performative.INFORM,
            msg_type=PING_TYPE,
            payload={"hello": "world", "ts": get_current_time()},
        )
        logger.info("[PING-SENDER] sending ping")
        await self.send(msg)


class WaitPongBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            logger.error("[PING-SENDER] did not receive pong (timeout)")
            await self.agent.stop()
            return

        perf, mtype, payload, _meta = parse_spade_message(msg)
        logger.info(f"[PING-SENDER] got perf={perf} type={mtype} payload={payload}")
        logger.info("[PING] SUCCESS OK")
        await self.agent.stop()


async def main():
    print("\n" + "=" * 70)
    print("TEST: SPADE PING/PONG")
    print("=" * 70 + "\n")

    recv_acc = account("emergency_center")
    send_acc = account("patient_emergency")

    receiver = PingReceiverAgent(recv_acc.jid, recv_acc.password)
    sender = PingSenderAgent(send_acc.jid, send_acc.password)
    sender.receiver_jid = recv_acc.jid

    await receiver.start()
    await sender.start()

    await asyncio.sleep(5)

    await receiver.stop()
    await sender.stop()

    await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
