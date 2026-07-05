# AGENTS.md — EntekaApp

## Project overview

EntekaApp is a real-time messaging app being migrated from vanilla JavaScript (Webpack) to React. The frontend is built by Joackim (learning React, currently knows `useState`, `useEffect`, props, and basic React Router). The backend is built by a friend using Python (FastAPI).

This file exists to give any AI coding agent the context needed to continue helping without re-discovering the same decisions.

## Tutoring style — IMPORTANT

Joackim is explicitly learning React. Unless told otherwise:
- **Do not write code unless explicitly asked.** Act as a tutor: explain concepts, ask guiding questions, let Joackim write the code himself.
- Confirm understanding before moving to the next component.
- Only step in with full code when Joackim asks directly for it (e.g. styling syntax, git commands, config files).
- Build order matters — one component at a time, reviewed before moving to the next.

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
      NewMessage.jsx      — "To:" recipient input + suggestions/search list. Has searchText, users, suggestions state. Two useEffects: one on mount (load suggestions, currently console.log placeholder), one on [searchText] (search backend, currently console.log placeholder, guarded by `searchText !== ""`)
      ChatView.jsx        — composes ChatHeader + MessageList + MessageInput. Composition component for the chat screen.
      ChatHeader.jsx      — profile pic + username (currently hardcoded "Test Username")
      MessageList.jsx     — renders MessageBubble list from mock messages, scrollable (flex-1 + overflow-y-auto + min-h-0 chain, overflow-hidden on parent)
      MessageBubble.jsx   — { text, timestamp, isMine } → right-aligned purple bubble if isMine, left-aligned dark bubble otherwise
      MessageInput.jsx    — text input + send icon, styled as pill; NOT yet wired to add messages to ChatView's state
    settings/
      SettingsPanel.jsx   — big settings icon by default; account options list (username/password/email/profile picture) when activeSettings prop is true
    api/
      client.js           — axios calls to backend: loginDataPython(data), signUpDataPython(data), verifyToken(token). Returns { auth, message, token } or network-error fallback. (Moved from SendDataPython.jsx)
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
- `users` table: id, username (UNIQUE), email (UNIQUE), password (hashed)
- CORS enabled for localhost:5173 and localhost:8000

**Known issues fixed so far:**
- ~~Passwords stored in plain text~~ → fixed with bcrypt
- ~~No UNIQUE constraint on username~~ → fixed
- ~~Signup checked username+password together~~ → fixed, now checks username only via `get_user_hash`

**Not yet implemented (backend):**
- `GET /users/search?q=username` — for NewMessage search
- `GET /users/suggestions` — for NewMessage default suggestions
- Conversations endpoints (`GET /conversations`, `POST /conversations`)
- Messages endpoints (`GET /messages/:conversationId`)
- WebSocket endpoint for real-time messaging

## Frontend TODO (in rough priority order)

1. Wire `MessageInput` to actually call the "add message" function passed down from `ChatView` (in progress — function not yet written)
2. Clicking a user card in `NewMessage` should call `setSelectedChat` (passed down from HomePage) to open `ChatView`
3. Back button in `ChatHeader` to reset `selectedChat` to `null` (return to WelcomeView)
4. Replace `NewMessage`'s console.log placeholders with real axios calls once backend search/suggestions endpoints exist
5. Update `.map()` keys in NewMessage from index-based to `user.id` once real user objects arrive (shape will be `{ id, username }`, not bare numbers)
6. Replace hardcoded "Test Username" in ChatHeader with real selected chat user
7. Sidebar: replace empty-state with real conversation list once `/conversations` exists
8. WebSocket integration for real-time messages
9. ~~Move `SendDataPython.jsx` to `src/services/api.js`~~ → done, renamed to `src/components/api/client.js`
10. Finish migrating leftover old-palette colors (see Color palette section) in Sidebar settings cards etc.
11. ~~Login should eventually store/use JWT token once backend issues one~~ → done, JWT fully wired on both backend and frontend

## Git conventions

- Conventional Commits style: `feat:`, `fix:`, `refactor:`, `style:`, `chore:`
- Feature branches: `feature/short-description` (created with `git checkout -b feature/...`)
- MIT license, repo is public and intentionally open source

## Known environment notes

- Joackim is on Windows for the frontend machine (SSH key path issues use `C:\Users\joack\.ssh\...`), and a friend's backend machine is Mac-based (zsh, `.venv` auto-activation issue previously resolved by removing the `source .venv/bin/activate` line from `.zshrc`).
- Dev servers: frontend on `localhost:5173` (Vite default), backend on `localhost:8000` (FastAPI default).
