# DevCollab v2

DevCollab is a FastAPI + PyQt6 collaborative workspace for small teams. The backend owns authentication, permissions, room membership and real-time events; the desktop client is a focused collaboration UI.

## What's new

### Private rooms
- Numeric database IDs are no longer a join credential.
- Every room gets a cryptographically generated invite code such as `AB12C-9XZ8Q`.
- Joining requires **both** the invite code and the room password.
- Room passwords are bcrypt-hashed; plaintext room passwords are never stored.
- Users have persistent room membership after joining, so guessing a numeric ID does not grant access.
- Room creators can delete their entire room. Joined members appear in **Joined rooms** automatically and can open the room without entering the invite code again.
- Room owners can search the user database and add existing users directly to a room.
- Owners can leave a room too; ownership transfers to the longest-standing remaining member. A solo owner must delete the room instead.

### Task permissions
- The **task creator or a room admin** can delete that task.
- The backend enforces the rule; changing the desktop client cannot bypass it.
- The room owner is the default admin. If ownership is transferred, the new owner becomes the admin.
- Like/dislike and status changes still work for room members.

### Discussion
- Every task now has a discussion area.
- Any room member can add an opinion/comment.
- Comments support independent likes and dislikes per user.
- Comment creators can delete their own comments.
- Comment activity is synchronized live over WebSockets.

### UI overhaul
- Dark visual system with reusable cards, typography and accent styles.
- Home dashboard split into **Your rooms** and **Joined rooms**.
- Room-owner user search with one-click member invitations from the existing user database.
- Generated invite code shown clearly in a room.
- Two-pane room layout: tasks on the left, selected task + discussion on the right.
- Cleaner task cards with creator, timestamp, reactions and status.
- Simple DevCollab `DC` brand mark integrated into the interface.

## Running locally

You need two terminals.

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

The backend creates `devcollab.db` automatically.


### Client

In another terminal:

```bash
cd client
pip install -r requirements.txt
python main.py
```

## Architecture

```text
PyQt6 client
   │
   ├── HTTP/JSON ───────────────► FastAPI
   │                              │
   └── WebSocket ───────────────►│
                                  ├── JWT auth
                                  ├── room membership
                                  ├── permission checks
                                  └── SQLAlchemy / SQLite
```