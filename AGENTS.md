# AGENTS.md — EntekaApp

## Project overview

EntekaApp is a real-time messaging app being migrated from vanilla JavaScript (Webpack) to React.

This file exists to give any AI coding agent the context needed to continue helping without re-discovering the same decisions.

## Tech stack

**Frontend**
- React 19 + Vite
- React Router v7 (`react-router-dom`)
- Tailwind CSS (utility classes directly in JSX; shared input styles via `@layer base` in `index.css`)
- Plain JavaScript (no TypeScript)
- `axios` for HTTP calls to the backend

**Backend**
- FastAPI (Python)
- SQLite (`Enteka.db`) via `sqlite3` — may move to PostgreSQL/Turso later for production
- `bcrypt` for password hashing (via `encryption.py`)
- CORS configured for `http://localhost:5173`, `http://localhost:8000`, and `http://{P_IP}:5173` (for phone testing — set `P_IP` in `Backend/.env`)
- JWT auth — **implemented** (via `auth.py`, `PyJWT`, HS256)

**Deployment plan (not started yet)**
- Frontend → Vercel
- Backend → Render
- Database → Turso (or Supabase Postgres)
All free-tier.

## Color palette (dark theme)

| Role | Color |
|---|---|
| App background | `#1E2130` |
| Surface / panels | `#272B3D` |
| Elevated surface / cards / inputs | `#2F3347` |
| Hover state | `#363B52` |
| Accent (buttons, links, active) | `#7C6AF7` |
| Accent hover | `#6A59E0` |
| Primary text | `#F0F0F5` |
| Secondary text | `#9B9DB8` |
| Danger | `#E05C5C` / `text-red-400` (errors) |

Some older components may still have leftover colors from the previous palette (`#474E68`, `#646A84`, `#40465d`, `#3a3f54`, `#D9D9D9`, `#C7C6C6`) — these should be migrated to the table above when touched.

## Component structure

```
src/
  components/
    auth/
      LoginForm.jsx       — controlled form (username, password), calls loginDataPython, shows backend error, navigates to /home on auth success, saves JWT token to localStorage
      SignUpForm.jsx      — controlled form (username, email, password), calls signUpDataPython, same error/nav pattern, saves JWT token to localStorage
    layout/
      NavBar.jsx          — logo + ENTEKA text (logo calls `goHome` prop to reset HomePage), Users icon (toggles friendsMode via `toggleFriendsMode`), settings icon (toggles chat/settings mode via prop), profile icon with dropdown (Log Out button, click-outside-to-close, removes JWT token and navigates to /)
      Sidebar.jsx         — fetches real chat list via `getChats()` on mount and re-fetches on `chatRefresh` prop change. Renders loading/empty/list states. Chat cards use `bg-[#2F3347]` with `overflow-y-auto` scrolling. "Account Settings" entry in settings mode. In friendsMode: fetches friends list + pending requests on mount, renders request blocks with accept/reject (Check/X icons), and friends list with click-to-chat via `createChat`. `handleFriendClick` calls `toggleFriendsMode()` after opening chat.
    chat/
      WelcomeView.jsx     — "Hello, {userName}!" + "Start a new chat!" button (calls turnOffWelcomeMode prop)
      NewMessage.jsx      — "To:" recipient input + suggestions/search list. Accepts `setSelectedChat` and `bumpChatRefresh` props; `handleUserClick` calls `createChat` then `setSelectedChat({ id, username, chat_id })` to open ChatView with a real chat, then calls `bumpChatRefresh()` to refresh sidebar. Has searchText, users state. useEffect on [searchText] with 300ms debounce (calls `searchFriends` from client.js, sets users state, shows "No Users found." card when empty). Resets users on empty input via else branch. Searches friends only (not all users).
      ChatView.jsx        — composes ChatHeader + MessageList + MessageInput. Accepts `selectedChat`, `handleBack`, `bumpChatRefresh`, and `userName` props. Owns messages + loading state; fetches real messages via `getMessages` on mount/chat change. Sends/receives messages via WebSocket (no POST). WebSocket URL built from `WS_BASE` (imported from client.js) + chat_id. Has `handleTyping` function with 1s idle timer, `typingUser` state, and `typingTimerRef`. `onmessage` handles `new_message`, `typing`, and `stop_typing` event types. Calls `bumpChatRefresh()` on new messages to update sidebar. Uses generation counter (`genRef`) to ignore stale WebSocket handlers and prevent duplicate messages. Maps backend `content` → `text`, compares `data.username === userName` for `isMine`.
      ChatHeader.jsx      — profile pic + username. Accepts `username` prop to display the selected chat user's name and `handleBack` prop for back arrow.
      MessageList.jsx     — renders MessageBubble list, scrollable (flex-1 + overflow-y-auto + min-h-0), auto-scrolls to bottom on new messages via `useRef` + `scrollIntoView`. Accepts `typingUser` prop to render animated typing dots.
      MessageBubble.jsx   — { text, timestamp, isMine } → right-aligned purple bubble with `text-white/65` timestamp if isMine, left-aligned dark bubble with `text-gray-400` timestamp otherwise
      MessageInput.jsx    — text input + send icon, styled as pill; accepts `SendMessage` and `onTyping` props. Calls `onTyping()` on every keystroke for typing indicator.
    friends/
      FriendsView.jsx     — search input + debounce + send friend request on user card click. Filters self out of search results via `props.userName`. Shows "Request Sent" confirmation after sending.
    settings/
      SettingsPanel.jsx   — big settings icon by default; account options list (username/password/email/profile picture) when activeSettings prop is true
    api/
      client.js           — axios calls to backend: loginDataPython(data), signUpDataPython(data), verifyToken(token), search(query), searchFriends(query), createChat(user2Id), sendMessages(chatId, content), getMessages(chatId), getFriendsList(), getFriendRequests(), sendFriendRequest(user_id), acceptFriendRequest(request_id), rejectFriendRequest(request_id), deleteFriend(friend_id). Returns { auth, message, token } or network-error fallback. search returns response.data (list of user dicts) or null on network error. searchFriends returns { auth, friends } with JWT auth. createChat/sendMessages/getMessages send JWT in Authorization header. Exports `API_BASE` and `WS_BASE` constants at the top — change `localhost` in `VITE_PERSONAL_IP` to laptop IP in root `.env` for phone testing. (Moved from SendDataPython.jsx)
  pages/
    AuthPage.jsx          — toggles LoginForm/SignUpForm via showSignUp state + toggleSwitch (prevState => !prevState pattern)
      HomePage.jsx          — owns chatMode, welcome, activeSettings, selectedChat, chatRefresh, friendsMode state. Renders NavBar + Sidebar + (ChatView | WelcomeView | NewMessage | SettingsPanel | FriendsView) depending on state combo. `handleBack` function sets `selectedChat(null)` to return to WelcomeView/NewMessage. `goHome` function resets all state (closes chat, shows Welcome, switches to chat mode). `bumpChatRefresh()` increments `chatRefresh` counter; passed to ChatView and NewMessage so they can trigger Sidebar re-fetch. Passes `userName` to ChatView for isMine detection and to FriendsView for self-filtering. `toggleFriendsMode` toggles friendsMode boolean (same prev => !prev pattern).
  App.jsx                 — React Router routes: "/" → AuthPage, "/home" → HomePage (guarded by isAuthenticated), "*" → redirect to "/". Owns isAuthenticated + userName + loading state, restores session via /verify on mount.
  main.jsx                 — wraps App in BrowserRouter
```

### Key state-lifting patterns already established
- Toggle-between-two-views pattern: `const [x, setX] = useState(bool); function toggle() { setX(prev => !prev) }` — used in AuthPage (showSignUp) and HomePage (chatMode, friendsMode).
- One-way state (no toggle needed): `welcome` in HomePage only ever goes true → false via `turnOffWelcomeMode`.
- Auth state (`isAuthenticated`, `userName`) lives in `App.jsx` and is passed down as props — not in context or a global store (no Redux/Zustand currently in use, despite earlier discussion of Zustand as an option).
- `selectedChat` in HomePage gates whether ChatView shows; must be initialized to `null` (not `{}`, which is truthy and broke conditional rendering early on).
- `chatRefresh` counter in HomePage: bumping it (`setChatRefresh(prev => prev + 1)`) triggers Sidebar's `useEffect` to re-fetch chat list. `bumpChatRefresh` function is passed to `ChatView` (called after send) and `NewMessage` (called after chat creation) so the sidebar updates in real-time.

## Backend status

**Implemented (files in `db/`, `security/`, `core/`, `routers/`, root `main.py` + `setup.py`):**
- `POST /signup` — { username, email, password } → checks username uniqueness via `get_user_hash`, hashes password with bcrypt, inserts user, returns JWT token → { auth, token, username }
- `POST /login` — { username, password } → looks up hash, verifies with bcrypt, returns JWT token → { auth, token, username }
- `POST /verify` — { token } → verifies JWT, returns username → { auth, username }
- `GET /` — health check
- `GET /users/search?query=username` — JWT auth → searches users by username prefix via `search_users(conn, query)` in `database.py`, returns `[{ id, username }]` or `null`
- `GET /users/suggestions` — JWT auth → returns random user suggestions (excluding caller) for NewMessage default list
- `POST /chats` — { user2_id } (user1 from JWT) → normalizes IDs, generates UUID → SHA-256 hash, inserts into `chats`, prevents duplicates via UNIQUE constraint, returns `{ chat_id, passkey_hash }`. On UNIQUE violation (duplicate chat), catches `IntegrityError` and returns the existing chat instead of failing.
- `GET /chats` — JWT auth → returns all chats for the authenticated user (`{ auth, chats: [...] }`). Filters out empty chats (no messages). Each chat includes `last_message`, `last_image`, and `last_timestamp` (formatted as `HH:MM`).
- `POST /upload` — JWT auth → accepts multipart file via `UploadFile`, validates extension allowlist (jpg/jpeg/png/gif/webp), enforces 5 MB size limit via `MAX_UPLOAD_SIZE_MB` (chunked read), verifies image magic bytes (JPEG/PNG/GIF/WEBP), rejects empty files, saves encrypted to `uploads/` with UUID filename, returns `{ image_url }`. Served via custom `GET /uploads/{filename}` endpoint that requires a `token` query param (valid JWT) and decrypts on the fly.
- `POST /friends/request/{user_id}` — JWT auth → send friend request (status: pending). Prevents self-requests (`from_id == to_id` returns None) and duplicate requests in either direction (`(A→B)` or `(B→A)` via SELECT check before INSERT).
- `GET /friends/requests` — JWT auth → list incoming pending requests with sender's username
- `POST /friends/accept/{request_id}` — JWT auth → accept friend request (status → accepted). Only the recipient (`to_id`) can accept; others get 404.
- `POST /friends/reject/{request_id}` — JWT auth → reject friend request (status → rejected). Only the recipient (`to_id`) can reject; others get 404.
- `GET /friends` — JWT auth → list accepted friends
- `GET /friends/search?query=...` — JWT auth → search accepted friends by username prefix (joins friends table, excludes caller via `u.id != ?`, deduplicates with DISTINCT)
- `DELETE /friends/{friend_id}` — JWT auth → remove friend
- WebSocket `/ws/{chat_id}` — connects via JWT token as query param, verifies the caller is a participant in the chat (closes with code 1008 otherwise), broadcasts new messages to all connected clients in the chat room in real-time via `ConnectionManager`. Handles `message`, `image`, `typing`, `stop_typing`, `call_offer`, `call_answer`, `ice_candidate`, `call_end`, and `call_reject` event types. `image` type accepts `image_url` (from prior upload) and optional `content` caption. Typing, stop_typing, and all VoIP signaling events broadcast to others only (excludes sender via `exclude` parameter on `broadcast`). VoIP message types forward `data` payload (SDP offer/answer, ICE candidate) without inspecting it — the backend is purely a signaling relay.
- `POST /messages` — { chat_id, content } (sender from JWT) → verifies sender is a chat participant (`403` otherwise), inserts into `messages`, returns `{ auth, message_id }`
- `GET /messages/{chat_id}` — JWT auth → verifies caller is a chat participant (`403` otherwise), returns all messages for a chat ordered by timestamp, each message has `is_mine` (boolean) based on authenticated user. Messages include optional `image` field. Timestamps formatted as `HH:MM` on the backend.
- `users` table: id, username (UNIQUE), email (UNIQUE), password (hashed)
- `chats` table: id, user1_id, user2_id, passkey_hash (SHA-256 of UUID), created_at, UNIQUE(user1_id, user2_id)
- `messages` table: id, chat_id, sender_id, content, image (TEXT, nullable), timestamp
- `friends` table: id, from_id, to_id, status (pending/accepted/rejected), created_at, UNIQUE(from_id, to_id)
- `database.py` functions: `create_connection`, `create_table`, `insert_user`, `get_user_hash`, `search_users`, `create_chat`, `get_chat_passkey_hash`, `get_user_by_username`, `get_user_by_id`, `insert_message`, `get_messages_by_chat_id`, `get_last_message_by_chat_id`, `get_chats_by_user_id`, `get_user_suggestions`, `send_friend_request`, `accept_friend_request`, `reject_friend_request`, `get_pending_requests`, `get_friends`, `remove_friend`, `search_friends`, `chat_belongs_to_user`
- CORS enabled for localhost:5173, localhost:8000, and http://{P_IP}:5173 (for phone testing — set P_IP in Backend/.env)
- `authenticate_caller(conn, authorization)` helper in `core/utils.py` — reduces 15-line repeated auth block across 5 endpoints to 3 lines each. Raises `HTTPException(401)` on failure, returns `caller_id` on success.
- Image upload: `POST /upload` saves files to `Backend/uploads/` with UUID filenames, served via custom `GET /uploads/{filename}` endpoint that decrypts on the fly.
- Friends system: single `friends` table with `status` column (pending/accepted/rejected) handles request/accept flow. No separate `friend_requests` table needed.
- At-rest encryption: message content is encrypted with Fernet (symmetric AES) before being stored in the database. `ENCRYPTION_KEY` in `Backend/.env` controls the key. If unset, messages are stored as plaintext. Decryption happens transparently at the database layer — no changes needed in API or WebSocket endpoints. Image files are also encrypted on disk and decrypted on the fly when served via `GET /uploads/{filename}`.

**Known issues fixed so far:**
- ~~Passwords stored in plain text~~ → fixed with bcrypt
- ~~No UNIQUE constraint on username~~ → fixed
- ~~Signup checked username+password together~~ → fixed, now checks username only via `get_user_hash`
- ~~`create_chat` returns `None` on UNIQUE violation (duplicate chat), crashing the frontend~~ → fixed, `IntegrityError` caught, existing chat returned instead
- ~~Sidebar crashes on `null.map()` when `chats` initial state is `null`~~ → fixed with `(chats || []).map(...)` guard in render and `data && data.chats` guard on setChats
- ~~Empty chats (no messages) show in sidebar~~ → fixed, backend filters out chats with no messages in `GET /chats`, only appends when `last_msg` is truthy
- ~~Sidebar doesn't update after creating a new chat or sending a message~~ → fixed, `chatRefresh` counter in HomePage triggers Sidebar re-fetch; `bumpChatRefresh` passed to ChatView and NewMessage
- ~~`authenticate_caller` helper extracted (auth logic centralized, consistent tuple return on all paths)~~ → fixed in `fix/backend-minor-issues`, merged to main; later moved to `core/utils.py` with `HTTPException(401)` pattern
- ~~`GET /messages/{chat_id}` crashes on empty chat (no null guard)~~ → fixed, null check returns `{ auth: True, messages: [] }`
- ~~`email-validator` missing from requirements~~ → fixed, added to `requirements.txt`
- ~~`encryption.py:verify` redundant `if x else` pattern~~ → simplified to direct return
- ~~`database.py:create_table` misleading print message~~ → updated to reflect all 3 tables
- ~~Duplicate WebSocket messages from stale connections (React Strict Mode double-mount)~~ → fixed with generation counter (`genRef`) that guards all WS handlers, ignores stale connections
- ~~`print()` scattered across backend~~ → replaced with `logging` module (named loggers, `%(asctime)s [%(levelname)s] %(name)s` format)
- ~~Backend crashes silently on missing env vars~~ → `setup.py` validates `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` on import; warns if SECRET_KEY is still placeholder
- ~~All endpoints return 200 even on errors~~ → `authenticate_caller` raises `HTTPException(401)`; all routers return `JSONResponse(status_code=4xx/5xx)` with frontend-compatible body
- ~~`main.py` was 350+ lines~~ → split into `db/`, `security/`, `core/`, `routers/` directories; `main.py` is now 28 lines
- ~~Frontend swallowed server error messages~~ → `client.js` catch blocks check `error.response?.data` before falling back to generic message
- ~~Backend flat file structure~~ → reorganized into `db/`, `security/`, `core/`, `routers/` directories with updated imports
- ~~Self-request in friends (no from_id == to_id check)~~ → fixed with guard clause in `send_friend_request`
- ~~Duplicate friend requests in swapped directions (A→B and B→A both allowed)~~ → fixed with SELECT check before INSERT in `send_friend_request`
- ~~Sidebar timestamp mismatch with chat view (UTC vs localtime)~~ → fixed, messages table schema changed from `datetime('now')` to `datetime('now', 'localtime')` so both DB and WebSocket timestamps use local time
- ~~Any logged-in user could read/post to any chat by guessing `chat_id`~~ → fixed with `chat_belongs_to_user()` membership check on `GET`/`POST /messages` (403) and WebSocket `/ws/{chat_id}` (close 1008)
- ~~`GET /users/search` was unauthenticated (username enumeration)~~ → fixed, now requires JWT via `authenticate_caller`
- ~~Anyone could accept/reject any pending friend request by `request_id`~~ → fixed, accept/reject now verify `to_id == caller_id`, others get 404
- ~~`client.js` template literals mangled to single quotes (all API calls + WS broken)~~ → fixed, restored backticks
- ~~`POST /upload` was unauthenticated (anyone could fill the disk) and accepted any file type/size~~ → fixed, requires JWT, extension allowlist (jpg/jpeg/png/gif/webp), 5 MB chunked limit via `MAX_UPLOAD_SIZE_MB`, magic-byte check, empty-file reject
- ~~`GET /uploads/{filename}` was unauthenticated~~ → fixed, requires `token` query param (valid JWT), only serves allowlisted image extensions
- ~~`MAX_uPLOAD_SIZE_MB` typo in setup.py crashed backend on startup~~ → fixed to `MAX_UPLOAD_SIZE_MB`
- ~~"database is locked" errors under concurrent writes~~ → `create_connection` now enables WAL mode, `busy_timeout=5000`, and `foreign_keys=ON` (SQLite-only; migrated DB engine handles concurrency natively when we move off SQLite)
- ~~`insert_user` never returned the new id / swallowed errors~~ → returns `cursor.lastrowid`; returns `None` on `sqlite3.Error`; `POST /signup` checks the return and returns `409` on the signup race (pre-check via `get_user_hash` + post-INSERT confirmation)
- ~~`chats.created_at` / `friends.created_at` stored UTC while `messages.timestamp` was localtime~~ → both now `datetime('now', 'localtime')`
- ~~`POST /chats` with a nonexistent `user2_id` returned 200~~ → `get_user_by_id` guard, now returns `JSONResponse(status_code=404)`

**Not yet implemented (backend):**
- None. All planned backend features are done. (Concurrency rewrite — aiosqlite/threading.Lock — deliberately skipped; WAL + busy_timeout suffice for SQLite dev, DB migrates later.)

## VoIP status

**Backend** — implemented (merged to main):
- 5 new WebSocket message types: `call_offer`, `call_answer`, `ice_candidate`, `call_end`, `call_reject`
- Backend forwards `data` payload transparently — no inspection, no database storage
- Uses existing `ConnectionManager.broadcast()` with `exclude=websocket` so sender doesn't echo
- `call_end` and `call_reject` are notification-only (no `data` field)
- No new Python libraries required

**Not yet implemented (frontend — your friend's side):**
- Install `simple-peer` npm package
- Create `CallContext.jsx` managing call state (idle/calling/ringing/connected), microphone via `getUserMedia`, and simple-peer instance for signal exchange
- Create `IncomingCall.jsx` overlay (accept/reject buttons)
- Create `ActiveCall.jsx` bar (duration timer, end call, mute toggle)
- Wire phone icon in `ChatHeader.jsx` to initiate calls
- Wrap `App.jsx` with `CallProvider`

## Frontend TODO (in rough priority order)

1. ~~Wire `MessageInput` to actually call the "add message" function~~ → done, ChatView owns messages state + addMessage, MessageInput calls it on Enter/click
2. ~~Clicking a user card in `NewMessage` should call `setSelectedChat` (passed down from HomePage) to open `ChatView`~~ → done, NewMessage accepts `setSelectedChat` prop, user card onClick fires `setSelectedChat({ id, username })`
 3. ~~Back button in `ChatHeader` to reset `selectedChat` to `null` (return to WelcomeView)~~ → done, ChatHeader gets `handleBack` prop, calls `setSelectedChat(null)` in HomePage
 4. ~~Replace `NewMessage`'s console.log placeholders with real axios calls once backend search/suggestions endpoints exist~~ → done, search endpoint wired with 300ms debounce; shows "No Users found." on empty results
 5. ~~Update `.map()` keys in NewMessage from index-based to `user.id` once real user objects arrive~~ → done, uses `key={user.id}` and `{user.username}`
6. ~~Replace hardcoded "Test Username" in ChatHeader with real selected chat user (ChatHeader receives no props yet)~~ → done, ChatHeader accepts `username` prop, ChatView passes `selectedChat.username`
7. ~~Sidebar: replace empty-state with real conversation list via `GET /chats`~~ → done, Sidebar fetches on mount and re-fetches on `chatRefresh` change. Cards with `bg-[#2F3347]`, `overflow-y-auto` scrolling, timestamps displayed.
 8. ~~Wire `NewMessage` user card click → `POST /chats` then open `ChatView` with the new chat~~ → done, `handleUserClick` calls `createChat` then passes `chat_id` to `setSelectedChat`
 9. ~~Wire `ChatView` to fetch messages via `GET /messages/{chat_id}` and send via `POST /messages` (backend ready, frontend still using mock messages)~~ → done, ChatView fetches real messages via `getMessages` on mount/chat change and sends via `sendMessages` on send. Loading state shown while fetching.
10. ~~WebSocket integration for real-time messages~~ → done, ChatView sends/receives via WebSocket (no POST). Backend handles `message`, `typing`, `stop_typing` types with `exclude` support.
11. ~~Move `SendDataPython.jsx` to `src/services/api.js`~~ → done, renamed to `src/components/api/client.js`
12. Finish migrating leftover old-palette colors in Sidebar settings cards (`#40465d` → `#2F3347`, `#3a3f54` → `#363B52`)
13. ~~Login should eventually store/use JWT token once backend issues one~~ → done, JWT fully wired on both backend and frontend
14. ~~Add logout button via profile dropdown in NavBar~~ → done, profile icon toggles dropdown with Log Out, click-outside-to-close, removes token and navigates to /
15. ~~Typing indicator~~ → done, animated dots with custom `@keyframes typing-dot` in `index.css`, 1.5s idle timer, `exclude=websocket` on backend
16. ~~Auto-scroll on new messages~~ → done, `MessageList` uses `useRef` + `scrollIntoView`
17. ~~Timestamp visibility on own messages~~ → done, `text-white/65` on purple bubbles vs `text-gray-400` on dark
18. Add image upload UI (file picker icon in MessageInput, upload via POST /upload, send via WebSocket)
19. Display images in MessageBubble (render `<img>` when message has `image_url`)
20. ~~Build friends list UI (sidebar tabs or separate page, friend requests with accept/reject)~~ → done, Sidebar has Requests and Friends List sections, FriendsView for searching + sending requests, accept/reject wired with API calls. Searches friends only in NewMessage. Self-request prevented via frontend filter and backend guard. Duplicate friend requests prevented in both directions.
21. ~~Add `uploads/` to .gitignore~~ -> done

## Environment config

- `Backend/.env` — backend secrets (SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, P_IP, ENCRYPTION_KEY, MAX_UPLOAD_SIZE_MB). Ignored by git; copy from `.env.example`.
- `Backend/setup.py` — loads .env, configures logging, validates required vars on startup.
- Root `.env` — frontend Vite vars (VITE_PERSONAL_IP). Ignored by git; copy from `.env.example`.
- Set `VITE_PERSONAL_IP` and `P_IP` to your laptop's local network IP (e.g. `192.168.1.112`) to test the app from your phone on the same WiFi.

## Git conventions

- Conventional Commits style: `feat:`, `fix:`, `refactor:`, `style:`, `chore:`
- Feature branches: `feature/short-description` (created with `git checkout -b feature/...`)
- MIT license, repo is public and intentionally open source


