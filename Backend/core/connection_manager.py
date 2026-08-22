class ConnectionManager():
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket, chat_id):
        await websocket.accept()
        if chat_id not in self.active_connections: self.active_connections[chat_id] = []
        self.active_connections[chat_id].append(websocket)

    def disconnect(self, websocket, chat_id):
        if websocket in self.active_connections.get(chat_id, []):
            self.active_connections[chat_id].remove(websocket)
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]

    async def broadcast(self, message, chat_id, exclude=None):
        for connection in list(self.active_connections.get(chat_id, [])):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection, chat_id)

class NotificationManager():
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket, user_id):
            await websocket.accept()
            if user_id not in self.active_connections: self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket, user_id):
        if websocket in self.active_connections.get(user_id, []):
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_to_user(self, message, user_id):
        for connection in list(self.active_connections.get(user_id, [])):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection, user_id)
