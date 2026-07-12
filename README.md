# AetherArcade: Real-Time Chat & In-Chat Gaming Integration Platform

AetherArcade is a full-stack real-time messaging platform featuring interactive, instant-play mini-games integrated directly into chat threads. Built with a robust Python/Django backend and a responsive Vite/React frontend, the platform allows users to discover contacts, initiate 1:1 chat sessions, and launch games (Chess, Tic-Tac-Toe, and Connect Four) directly in a split-screen layout.

---

## 🚀 Key Features

*   **Secure Session Authentication**: Custom-built, lightweight session authentication bypassing heavy standard Django schema pollution.
*   **User Discovery**: Dynamic username lookup allowing users to discover other registered members and start new chats.
*   **1:1 Messaging**: Smooth chronological message threads with updates.
*   **Seeded Game Catalog**: Natively seeded game database containing description and relative loading endpoints.
*   **Interactive Split-Screen Iframe Panel**: Selecting a game sends a special game invite bubble. Clicking "Launch & Play" loads the game inside a side-by-side split screen so players can chat and play simultaneously.
*   **Three Playable HTML5 Games**:
    *   **Tic-Tac-Toe**: Supports Local 2-Player (Pass & Play) and vs. AI modes.
    *   **Connect Four**: Turn-based grid drop physics with AI & Local PvP support.
    *   **Chess**: Fully verified move validation (powered by `chess.js`) with turn tracking, check/checkmate alerts, and unicode chess pieces.

---

## 🛠️ Technology Stack

### Backend
*   **Framework**: Python (Django 6.0+)
*   **Database**: SQLite / PostgreSQL (Configured dynamically via environment variables)
*   **Architecture**: REST API with session-based cookies and custom CORS middleware.

### Frontend
*   **Framework**: React (Vite-based Single Page Application)
*   **State Management**: Zustand
*   **Styling**: Tailwind CSS v4.0 (Latest CSS-first styling engine)
*   **Icons**: Lucide React

---

## 📁 Project Structure

```text
├── backend_project/           # Django configuration folder
│   ├── settings.py            # Registered apps, middleware lists, DB configs
│   ├── urls.py                # Router loading the api/ prefix
│   └── ...
├── api/                       # Django API Application
│   ├── migrations/            # Data & schema migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_seed_games.py # Seeds default Chess, Tic-Tac-Toe, Connect Four catalog
│   │   └── 0003_update_game_urls.py # Updates URLs to relative React endpoints
│   ├── middleware.py          # CORS & Session-auth middlewares
│   ├── models.py              # User, Conversation, Message, Games models (with clean() constraints)
│   ├── urls.py                # REST endpoints routing
│   ├── views.py               # API Views
│   └── tests.py               # 9 database & API unit tests (100% passing)
├── frontend/                  # React Single Page Application (SPA)
│   ├── public/                # Static public assets
│   │   └── games/             # Natively served HTML5 games
│   │       ├── chess.html
│   │       ├── tictactoe.html
│   │       └── connectfour.html
│   ├── src/
│   │   ├── store/
│   │   │   └── useChatStore.js # Zustand store managing state transitions
│   │   ├── utils/
│   │   │   └── api.js          # Fetch API client configured with credentials
│   │   ├── App.jsx             # SPA Interface (Auth, Sidebar, Chat thread, Game split screen)
│   │   ├── index.css           # Tailwind v4.0 configurations
│   │   └── main.jsx            # React mount point
│   ├── vite.config.js          # Vite configuration with @tailwindcss/vite plugin
│   └── package.json
├── api_test_client.py         # Python command-line integration test client
├── venv/                      # Python virtual environment (ignored in git)
├── db.sqlite3                 # Local SQLite database file (ignored in git)
├── .gitignore                 # Excludes system, venv, node_modules, and database files
└── spec.md                    # Project specification file
```

---

## ⚙️ Setup and Execution

### Prerequisites
*   Python 3.12+
*   Node.js (v18+) & npm

### 1. Run the Django Backend
Navigate to the root directory, activate the virtual environment, and launch the server:
```bash
# Activate virtual environment
source venv/bin/activate

# Apply migrations and seed games
python manage.py migrate

# Run unit tests to verify database integrity
python manage.py test

# Start the Django development server (default port 8000)
python manage.py runserver
```

### 2. Run the Vite React Frontend
Navigate to the `frontend/` folder, install npm packages, and run the developer server:
```bash
# Navigate to frontend
cd frontend

# Install package dependencies
npm install

# Start Vite React server (default port 5173)
npm run dev
```
Visit **`http://localhost:5173`** in your browser to interact with the platform.

### 3. Run API Integration Tests
While the backend server is running on `http://127.0.0.1:8000`, you can run the integration test client to verify all API endpoints step-by-step:
```bash
# In the root directory, run the Python integration test client
python api_test_client.py
```

---

## 🌐 REST API Specifications

The backend exposes the following REST paths under the `/api/` prefix:

| Endpoint | Method | Authentication | Description |
| :--- | :--- | :---: | :--- |
| `/api/register` | `POST` | Public | Create a new user account with hashed password |
| `/api/login/` | `POST` | Public | Authenticate user credentials and establish session |
| `/api/users/?search=<query>` | `GET` | Session | Search other users by username |
| `/api/conversations/` | `GET` | Session | List active conversations for the logged-in user |
| `/api/conversations/` | `POST` | Session | Start a new 1:1 conversation with a recipient |
| `/api/conversation/<id>/messages/?after=<cursor>` | `GET` | Session | Fetch chronological message history (paginated with cursor) |
| `/api/messages/` | `POST` | Session | Send a text message or a special game invite message |
| `/api/games` | `GET` | Session | Retrieve the seeded catalog of shareable instant games |

---

## 🔒 Data Integrity & Validation

To ensure absolute schema safety, validations are strictly enforced at the model level via `clean()` and called automatically inside overridden `save()` methods:
1.  **User uniqueness**: Usernames must be unique and non-empty. Passwords are securely hashed.
2.  **Self-conversations block**: Prevents a user from starting a conversation with themselves.
3.  **Conversation uniqueness**: Only one active conversation record can exist between any two users (validated bidirectionally: `part_1` to `part_2` or `part_2` to `part_1`).
4.  **Message membership**: The message sender must be one of the registered participants in the referenced conversation.
5.  **Empty contents block**: Message text/content cannot be empty.
