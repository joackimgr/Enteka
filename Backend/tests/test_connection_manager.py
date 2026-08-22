class DeadSocket:
    def __init__(self): self.accepted = False
    async def accept(self): self.accepted = True
    async def send_json(self, message): raise RuntimeError("connection closed")

class LiveSocket():
    def __init__(self):
        self.accepted = False
        self.received = []
    async def accept(self): self.accepted = True
    async def send_json(self, message): self.received.append(message)

import asyncio
from core.connection_manager import ConnectionManager, NotificationManager

def test_broadcast_survices_dead_socket():
    manager = ConnectionManager()
    live = LiveSocket()
    dead = DeadSocket()

    asyncio.run(manager.connect(live, 1))
    asyncio.run(manager.connect(dead, 1))

    asyncio.run(manager.broadcast({"type": "typing"}, 1))

    assert live.received == [{"type": "typing"}]
    assert dead not in manager.active_connections.get(1, [])

def test_send_to_user_survives_dead_socket():
    manager = NotificationManager()
    live = LiveSocket()
    dead = DeadSocket()

    asyncio.run(manager.connect(live, 42))
    asyncio.run(manager.connect(dead, 42))

    asyncio.run(manager.send_to_user({"type": "new_message", "chat_id": 1}, 42))

    assert live.received == [{"type": "new_message", "chat_id": 1}]
    assert dead not in manager.active_connections.get(42, [])

def test_broadcast_unknown_chat_is_noop():
    manager = ConnectionManager()

    asyncio.run(manager.broadcast({"type": "typing"}, 999))
