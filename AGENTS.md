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
- CORS configured for `http://localhost:5173` and `http://localhost:8000`
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
      NavBar.jsx          — logo + ENTEKA text, settings icon (toggles chat/settings mode via prop), profile icon
      Sidebar.jsx         — shows empty-chats state in chat mode, "Account Settings" entry in settings mode
    chat/
      WelcomeView.jsx     — "Hello, {userName}!" + "Start a new chat!" button (calls turnOffWelcomeMode prop)
      NewMessage.jsx      — "To:" recipient input + suggestions/search list. Accepts `setSelectedChat` prop; clicking a user card calls it with `{ id, username }` to open ChatView. Has searchText, users state. useEffect on [searchText] with 300ms debounce (calls `search` from client.js, sets users state, shows "No Users found." card when empty). Resets users on empty input via else branch.
      ChatView.jsx        — composes ChatHeader + MessageList + MessageInput. Accepts `selectedChat` prop, passes `username` to ChatHeader. Owns messages state, passes addMessage function to MessageInput.
      ChatHeader.jsx      — profile pic + username. Accepts `username` prop to display the selected chat user's name.
      MessageList.jsx     — renders MessageBubble list from mock messages, scrollable (flex-1 + overflow-y-auto + min-h-0 chain, overflow-hidden on parent)
      MessageBubble.jsx   — { text, timestamp, isMine } → right-aligned purple bubble if isMine, left-aligned dark bubble otherwise
      MessageInput.jsx    — text input + send icon, styled as pill; wired to add messages to ChatView's state via SendMessage prop on Enter/click
    settings/
      SettingsPanel.jsx   — big settings icon by default; account options list (username/password/email/profile picture) when activeSettings prop is true
    api/
      client.js           — axios calls to backend: loginDataPython(data), signUpDataPython(data), verifyToken(token), search(query). Returns { auth, message, token } or network-error fallback. search returns response.data (list of user dicts) or null on network error. (Moved from SendDataPython.jsx)
  pages/
    AuthPage.jsx          — toggles LoginForm/SignUpForm via showSignUp state + toggleSwitch (prevState => !prevState pattern)
    HomePage.jsx          — owns chatMode, welcome, activeSettings, selectedChat state. Renders NavBar + Sidebar + (ChatView | WelcomeView | NewMessage | SettingsPanel) depending on state combo
  App.jsx                 — React Router routes: "/" → AuthPage, "/home" → HomePage (guarded by isAuthenticated), "*" → redirect to "/". Owns isAuthenticated + userName + loading state, restores session via /verify on mount.
  main.jsx                 — wraps App in BrowserRouter
```

### Key state-lifting patterns already established
- Toggle-between-two-views pattern: `const [x, setX] = useState(bool); function toggle() { setX(prev => !prev) }` — used in AuthPage (showSignUp) and HomePage (chatMode).
- One-way state (no toggle needed): `welcome` in HomePage only ever goes true → false via `turnOffWelcomeMode`.
- Auth state (`isAuthenticated`, `userName`) lives in `App.jsx` and is passed down as props — not in context or a global store (no Redux/Zustand currently in use, despite earlier discussion of Zustand as an option).
- `selectedChat` in HomePage gates whether ChatView shows; must be initialized to `null` (not `{}`, which is truthy and broke conditional rendering early on).

## Backend status

**Implemented (`main.py`, `database.py`, `encryption.py`, `auth.py`):**
- `POST /signup` — { username, email, password } → checks username uniqueness via `get_user_hash`, hashes password with bcrypt, inserts user, returns JWT token → { auth, token, username }
- `POST /login` — { username, password } → looks up hash, verifies with bcrypt, returns JWT token → { auth, token, username }
- `POST /verify` — { token } → verifies JWT, returns username → { auth, username }
- `GET /` — health check
- `GET /users/search?query=username` — searches users by username prefix via `search_users(conn, query)` in `database.py`, returns `[{ id, username }]` or `null`
- `users` table: id, username (UNIQUE), email (UNIQUE), password (hashed)
- `database.py` functions: `create_connection`, `create_table`, `insert_user`, `get_user_hash`, `search_users`
- CORS enabled for localhost:5173 and localhost:8000

**Known issues fixed so far:**
- ~~Passwords stored in plain text~~ → fixed with bcrypt
- ~~No UNIQUE constraint on username~~ → fixed
- ~~Signup checked username+password together~~ → fixed, now checks username only via `get_user_hash`

**Not yet implemented (backend):**
- `GET /users/suggestions` — for NewMessage default suggestions
- Conversations endpoints (`GET /conversations`, `POST /conversations`)
- Messages endpoints (`GET /messages/:conversationId`)
- WebSocket endpoint for real-time messaging

## Frontend TODO (in rough priority order)

1. ~~Wire `MessageInput` to actually call the "add message" function~~ → done, ChatView owns messages state + addMessage, MessageInput calls it on Enter/click
2. ~~Clicking a user card in `NewMessage` should call `setSelectedChat` (passed down from HomePage) to open `ChatView`~~ → done, NewMessage accepts `setSelectedChat` prop, user card onClick fires `setSelectedChat({ id, username })`
3. Back button in `ChatHeader` to reset `selectedChat` to `null` (return to WelcomeView)
 4. ~~Replace `NewMessage`'s console.log placeholders with real axios calls once backend search/suggestions endpoints exist~~ → search endpoint exists (`GET /users/search?q=`), wired to call it with 300ms debounce; shows "No Users found." on empty results; suggestions endpoint still pending
 5. ~~Update `.map()` keys in NewMessage from index-based to `user.id` once real user objects arrive~~ → done, uses `key={user.id}` and `{user.username}`
6. ~~Replace hardcoded "Test Username" in ChatHeader with real selected chat user (ChatHeader receives no props yet)~~ → done, ChatHeader accepts `username` prop, ChatView passes `selectedChat.username`
7. Sidebar: replace empty-state with real conversation list once `/conversations` exists
8. WebSocket integration for real-time messages
9. ~~Move `SendDataPython.jsx` to `src/services/api.js`~~ → done, renamed to `src/components/api/client.js`
10. Finish migrating leftover old-palette colors in Sidebar settings cards (`#40465d` → `#2F3347`, `#3a3f54` → `#363B52`)
11. ~~Login should eventually store/use JWT token once backend issues one~~ → done, JWT fully wired on both backend and frontend

## Git conventions

- Conventional Commits style: `feat:`, `fix:`, `refactor:`, `style:`, `chore:`
- Feature branches: `feature/short-description` (created with `git checkout -b feature/...`)
- MIT license, repo is public and intentionally open source


