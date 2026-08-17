# Enteka

A real-time messaging application built with React 19 and FastAPI. Enteka delivers instant communication through WebSocket-backed chat rooms, live typing indicators, a friends system with push notifications, and encrypted message storage.

---

## Features

- **Real-time messaging** — Messages appear instantly across all connected clients via WebSocket, with no page refreshes or polling. Message data is encrypted at rest with Fernet before being stored.
- **User authentication** — Secure signup and login with bcrypt password hashing and JWT tokens. Sessions persist across page reloads via token verification.
- **Contact search** — Find other users by username prefix (debounced, with suggestions) and start new conversations.
- **Friends system** — Send, accept, and reject friend requests; friend requests are blocked in both directions (A→B and B→A) and self-requests are prevented. The friend list click-to-chat opens an existing or new conversation.
- **Live push notifications** — A global `/ws/notifications` socket pushes `new_message` and `new_friend_request` events (no content, just signals) so the sidebar conversation list and friend requests update in real time, with exponential-backoff reconnection.
- **Typing indicators** — See when someone is composing a message, with an animated indicator that clears after a short period of inactivity.
- **Conversation sidebar** — Your chat list updates in real time as new conversations are created or new messages arrive, showing the most recent message and timestamp. Empty chats are filtered out.
- **Account settings** — Edit username, email, and password from a settings panel with inline backend error display. Username changes re-issue the JWT.
- **Dark theme** — A cohesive dark color palette across all surfaces, from the app background to inputs and hover states.

---

## Tech Stack

**Frontend**
- React 19 with Vite
- React Router v7 for client-side routing
- Tailwind CSS 4 for styling
- Axios for HTTP requests
- Lucide React for icons

**Backend**
- FastAPI (Python) for the REST API and WebSocket server
- SQLite for the database (WAL mode, busy timeout; planned migration to Turso/PostgreSQL)
- PyJWT for token-based authentication
- bcrypt for password hashing
- WebSocket protocol for real-time message delivery and push notifications
- Fernet (symmetric AES) for at-rest encryption of message content

---

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.10+
- pip

### Backend Setup

```bash
cd Backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the Backend directory (copy from `.env.example`):

```
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
P_IP=your-pc-ip-here           # e.g. 192.0.2.100, for phone testing
ENCRYPTION_KEY=your-fernet-key-here
```

- `ENCRYPTION_KEY` — Fernet key for at-rest message encryption. Generate one with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`. If unset, messages are stored as plaintext.

Start the server:

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

### Frontend Setup

Create a root `.env` file (copy from `.env.example`):

```
VITE_PERSONAL_IP=your-laptop-ip-here   # e.g. 192.0.2.100; empty/omitted uses localhost
```

```bash
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

### Running from your phone (same WiFi)

Set `VITE_PERSONAL_IP` (root `.env`) and `P_IP` (Backend `.env`) to your laptop's local network IP, then open `http://<IP>:5173` on your phone.

---

## API Endpoints

### Auth & Users

| Method | Path | Description |
|---|---|---|
| POST | `/signup` | Create a new user account (returns a JWT) |
| POST | `/login` | Authenticate and receive a JWT |
| POST | `/verify` | Validate a JWT and return the username |
| GET | `/users/search?query=` | Search users by username prefix (JWT) |
| GET | `/users/suggestions` | Get random user suggestions (JWT) |
| GET | `/users/me` | Get the current user's profile (JWT) |
| PUT | `/users/me/username` | Update username (re-issues a JWT) |
| PUT | `/users/me/email` | Update email |
| PUT | `/users/me/password` | Update password (verifies current password) |

### Chats & Messages

| Method | Path | Description |
|---|---|---|
| POST | `/chats` | Create or retrieve an existing chat |
| GET | `/chats` | List the user's chats with last message/timestamp (empty chats filtered out) |
| POST | `/messages` | Send a message |
| GET | `/messages/{chat_id}` | Get all messages in the user's chat |

### Friends

| Method | Path | Description |
|---|---|---|
| POST | `/friends/request/{user_id}` | Send a friend request (409 on duplicate, blocks self-requests) |
| GET | `/friends/requests` | List incoming pending requests |
| POST | `/friends/accept/{request_id}` | Accept a pending request (recipient only) |
| POST | `/friends/reject/{request_id}` | Reject a pending request (recipient only) |
| GET | `/friends` | List accepted friends |
| GET | `/friends/search?query=` | Search accepted friends by username prefix |
| DELETE | `/friends/{friend_id}` | Remove a friend |

### WebSockets

| Path | Description |
|---|---|
| `/ws/notifications?token=` | Per-user push notifications: receives `new_friend_request` and `new_message` events (JWT required) |
| `/ws/{chat_id}?token=` | Real-time chat: send/receive `message`, `typing`, and `stop_typing` events (participant only) |

---

## Project Structure

```
Backend/
  main.py                -- FastAPI app, routers, CORS, WS managers init
  setup.py               -- loads .env, validates required vars, configures logging
  db/
    database.py          -- SQLite connection + all query functions
    schemas.py           -- Pydantic request body models
  security/
    auth.py              -- JWT create/verify
    encryption.py        -- bcrypt password hashing, Fernet at-rest encryption
  core/
    connection_manager.py -- per-chat ConnectionManager + per-user NotificationManager
    state.py             -- global app state (db conn, WS managers)
    utils.py             -- authenticate_caller helper
  routers/
    auth.py              -- /signup, /login, /verify
    chats.py             -- /chats, /messages
    friends.py           -- /friends/*
    ws.py                -- /ws/notifications, /ws/{chat_id}
    settings.py          -- /users/me*
  tests/                 -- pytest + conftest.py (fresh app/DB per test)
  Enteka.db              -- SQLite database (gitignored)

src/
  components/
    api/client.js        -- Axios service for backend communication (exports API_BASE, WS_BASE)
    auth/                -- LoginForm, SignUpForm
    layout/              -- NavBar, Sidebar
    chat/                -- WelcomeView, NewMessage, ChatView, ChatHeader,
                             MessageList, MessageBubble, MessageInput
    friends/             -- FriendsView
    settings/            -- SettingsPanel
  pages/
    AuthPage.jsx         -- Login/signup toggle page
    HomePage.jsx         -- Main app shell: sidebar, chat/friends/settings views,
                             global /ws/notifications socket
  App.jsx                -- Router setup and auth state
  main.jsx               -- Application entry point
```

---

## WebSocket Overview

- **Per-chat socket** (`/ws/{chat_id}`): opened when a conversation is active. Handles `message`, `typing`, and `stop_typing` events. All are broadcast to the chat room; typing events exclude the sender. Messages are persisted and encrypted before storage.
- **Notification socket** (`/ws/notifications`): opened once in `HomePage`. Receives lightweight `{ type }` signals — `new_message` (targeted at the other participant) and `new_friend_request` (from the friend request endpoint) — that trigger sidebar re-fetches on the frontend. Reconnects with exponential backoff (max 5 attempts, 1s × 2^n delay).

---

## Running Tests

The backend ships a full pytest suite (`Backend/tests/`) — 56 tests covering auth, chats, messages, friends, settings, and WebSockets. Each test builds a fresh app with a temp SQLite DB, so the real database is never touched.

```bash
cd Backend
.venv/bin/python -m pytest
```

---

## License

Apache 2.0