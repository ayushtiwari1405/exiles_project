# Project Specification: Real-Time Chat & Gaming Hub

## 1. Project Overview
Build a full-stack application featuring a frontend chat interface and a backend API. The platform will support user discovery, 1:1 messaging, and the ability to share interactive mini-games directly within conversation threads.

---

## 2. Technical Stack & Infrastructure

### Backend
* **Framework:** Python 
* **Database:** PostgreSQL  + Redis (for WebSocket)..
* **Authentication:** Basic username/password sessions or JWT 

### Frontend
* **Framework:** React.
* **Styling:** Tailwind CSS
* **State Management:** Zustand, Redux, Context API, or Vuex

---

## 3. Functional Requirements

### A. Authentication & User Management
* Users can create an account with a unique username and password.
* Secure password hashing (e.g., bcrypt).
* Users can search for other registered users via a search bar.

### B. Messaging (1:1)
* Users can initiate new 1:1 conversations.
* Infinite scrolling or cursor-based pagination for loading message history.

### C. In-Chat Gaming Integration
* Users can browse a seeded catalog of available mini-games.
* Users can send a "Game Invite" as a special message type within the chat.
* Clicking the game invite opens a modal or inline frame to display the game interface *(Note: Per scope exclusions, games do not need to be actually playable; simulating the UI/launch state is sufficient).*

---

## 4. Frontend Interface Requirements

The frontend must be fully responsive (mobile and desktop) and deliver a seamless Single Page Application (SPA) experience.

### A. Authentication Views
* **Login/Register Pages:** Simple, clean forms for user onboarding.
* **Error Handling:** Clear UI feedback for invalid credentials or taken usernames.

### B. Main Dashboard / Layout
* **Sidebar (Desktop) / Drawer (Mobile):** * Displays the currently logged-in user.
  * Contains a search bar to find new users (`GET /api/users/?search=<query>`).
  * Lists all active conversations, sorted by recent activity.
* **Main Content Area:** Displays the active chat window or an empty state if none is selected.

### C. Active Chat Interface
* **Header:** Shows the name of the user you are chatting with.
* **Message History Panel:** * Auto-scrolls to the bottom on new messages.
  * Distinct styling for sent vs. received messages (e.g., chat bubbles on left vs. right).
  * Smooth loading of older messages when scrolling to the top (`/?after=<cursor>`).
* **Message Input Area:**
  * Text input field with a send button.
  * A dedicated "Share Game" button (e.g., a gamepad icon).

### D. Game Integration UI
* **Game Catalog Modal:** Triggered by the "Share Game" button. Displays a grid or list of available games fetched from `GET /api/games/`.
* **Game Message Bubble:** A visually distinct message block indicating a game invite (e.g., showing the game thumbnail, title, and a "Play" button).
* **Mock Game Player:** When a game is launched, it should open in a focused state (e.g., a modal or overlaid iframe) to demonstrate where the game would run, even if the game itself is unplayable.

---

## 5. API Endpoints Specification

### REST API (HTTP)

**Auth & Users**
* `POST /api/register/` - Create a new user account.
* `POST /api/login/` - Authenticate and establish session/token.
* `GET /api/users/?search=<query>` - Search users by username.

**Conversations & Messages**
* `GET /api/conversations/` - List all active conversations for the logged-in user.
* `GET /api/conversations/<id>/messages/?after=<cursor>` - Fetch paginated message history.
* `POST /api/messages/` - Send a message. Payload must support distinguishing between standard text and game types.

**Games**
* `GET /api/games/` - Retrieve the seeded catalog of shareable games.

---

## 6. High-Level Data Models

**User**
* `id` (Primary Key)
* `username` (Unique)
* `password_hash`

**Conversation**
* `id` (Primary Key)
* `participant_1_id` (FK -> User)
* `participant_2_id` (FK -> User)
* `last_updated` (Timestamp)

**Message**
* `id` (Primary Key)
* `conversation_id` (FK -> Conversation)
* `sender_id` (FK -> User)
* `message_type` (Enum/String: `text`, `game`)
* `content` (Text payload or Game ID reference)
* `created_at` (Timestamp)

**Game (Seeded)**
* `id` (Primary Key)
* `title`
* `description`
* `thumbnail_url`
* `asset_url` 

---
## 7. Quality Assurance & Test Strategy

### Category 1: Authentication & Identity

- **TC-01 (Registration & Password Hashing):** Verify `POST /api/auth/register` creates a new user and stores the password as a bcrypt hash, not plain text.
- **TC-02 (Duplicate Username):** Verify `POST /api/auth/register` returns HTTP `409 Conflict` when a username already exists (case-insensitive).
- **TC-03 (Search Debounce):** Verify typing in the user search bar sends only one API request after a **300 ms** delay and returns matching users.

### Category 2: 1:1 Messaging & Pagination

- **TC-04 (Single Conversation Creation):** Verify sending the first message to a new user creates only one conversation, even if the request is sent multiple times.
- **TC-05 (Loading Older Messages):** Verify scrolling to the top loads older messages without missing or duplicating any, even if new messages arrive at the same time.
- **TC-06 (Message Display):** Verify sent messages appear on the right, received messages appear on the left, and screen readers announce the sender correctly.
- **TC-07 (Sending State & Retry):** Verify a sent message appears immediately with a **"Sending"** status and changes to a retry option if the request fails.
- **TC-08 (Prevent Self-Messaging):** Verify users cannot start a chat or send messages to themselves, returning HTTP `400 Bad Request`.

### Category 3: Real-Time WebSockets & Concurrency

- **TC-09 (Real-Time Message Delivery):** Verify a message sent by User A appears in User B's chat within **100 ms** without refreshing the page.
- **TC-10 (Reconnect & Sync):** Verify the app reconnects automatically after a WebSocket disconnect and fetches any missed messages.
- **TC-11 (Rate Limiting):** Verify sending **50 messages in 2 seconds** triggers rate limiting (`429` or WebSocket error) without affecting server stability.
- **TC-12 (Duplicate Message Prevention):** Verify duplicate requests with the same `client_tx_id` save only one message and show only one chat bubble.
- **TC-13 (Read Receipts):** Verify message status changes from **Delivered** to **Read** in real time when the recipient opens the chat.

### Category 4: In-Chat Gaming Integration & Security

- **TC-14 (Game List):** Verify clicking **Share Game** opens a modal within **200 ms** showing available games with images, titles, and descriptions.
- **TC-15 (Game Invite Storage):** Verify sending a game invite stores it as a game message using the correct game ID, without displaying the raw ID in the chat.
- **TC-16 (Game Card Display):** Verify valid game invites appear as interactive cards with a **Play** button, while invalid game IDs show a **"Game no longer available"** message.
- **TC-17 (Game Modal):** Verify clicking **Play** opens the game in a modal, keeps keyboard focus inside it, and closes with the **Escape** key.
- **TC-18 (Access Control):** Verify users cannot access conversations they are not part of and receive HTTP `403 Forbidden` (or an unauthorized WebSocket response).
