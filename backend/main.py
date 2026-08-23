import secrets
import string

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db, engine, Base
import models
import schemas
import auth
from ws_manager import manager

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DevCollab API", version="3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _random_invite_code(length: int = 10) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "-".join(("".join(secrets.choice(alphabet) for _ in range(5)),
                     "".join(secrets.choice(alphabet) for _ in range(5))))


def _migrate_legacy_database():
    """Upgrade a v2 SQLite database in-place without requiring Alembic yet."""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("projects")}
    with engine.begin() as conn:
        if "invite_code" not in columns:
            conn.execute(text("ALTER TABLE projects ADD COLUMN invite_code VARCHAR"))
        if "password_hash" not in columns:
            conn.execute(text("ALTER TABLE projects ADD COLUMN password_hash VARCHAR"))
        membership_columns = {col["name"] for col in inspector.get_columns("room_memberships")}
        if "is_admin" not in membership_columns:
            conn.execute(text("ALTER TABLE room_memberships ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0"))
        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_projects_invite_code ON projects (invite_code)"))

    db = next(get_db())
    try:
        for project in db.query(models.Project).all():
            if not project.invite_code:
                project.invite_code = _random_invite_code()
            if not project.password_hash:
                project.password_hash = auth.hash_password(project.invite_code)
            owner_member = db.query(models.RoomMembership).filter(
                models.RoomMembership.project_id == project.id,
                models.RoomMembership.user_id == project.owner_id,
            ).first()
            if not owner_member:
                db.add(models.RoomMembership(project_id=project.id, user_id=project.owner_id, is_admin=1))
            elif not owner_member.is_admin:
                owner_member.is_admin = 1
        db.commit()
    finally:
        db.close()


_migrate_legacy_database()

def _ensure_invite_code(db: Session, project: models.Project) -> str:
    while True:
        code = _random_invite_code()
        if not db.query(models.Project).filter(models.Project.invite_code == code).first():
            project.invite_code = code
            return code


def _project_out(db: Session, project: models.Project, user: models.User | None = None) -> schemas.ProjectOut:
    count = db.query(models.RoomMembership).filter(models.RoomMembership.project_id == project.id).count()
    return schemas.ProjectOut(
        id=project.id,
        name=project.name,
        owner_id=project.owner_id,
        invite_code=project.invite_code,
        member_count=count,
        is_owner=(user.id == project.owner_id) if user else False,
    )


def _get_project_or_404(db: Session, room_id: int) -> models.Project:
    project = db.query(models.Project).filter(models.Project.id == room_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Room doesn't exist")
    return project


def _require_member(db: Session, project: models.Project, user: models.User) -> models.RoomMembership:
    membership = db.query(models.RoomMembership).filter(
        models.RoomMembership.project_id == project.id,
        models.RoomMembership.user_id == user.id,
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this room")
    return membership


def _get_task_or_404(db: Session, task_id: int) -> models.Task:
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def _get_comment_or_404(db: Session, comment_id: int) -> models.Comment:
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


def _require_task_member(db: Session, task: models.Task, user: models.User) -> models.Project:
    project = _get_project_or_404(db, task.project_id)
    _require_member(db, project, user)
    return project


def _require_comment_member(db: Session, comment: models.Comment, user: models.User) -> models.Project:
    task = _get_task_or_404(db, comment.task_id)
    return _require_task_member(db, task, user)


# ---------- Auth ----------

@app.post("/register", response_model=schemas.Token)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == payload.username.strip()).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"username '{payload.username}' already exists")
    user = models.User(username=payload.username.strip(), hashed_password=auth.hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return schemas.Token(access_token=auth.create_access_token(user.username), username=user.username)


@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username.strip()).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return schemas.Token(access_token=auth.create_access_token(user.username), username=user.username)


@app.get("/users/search", response_model=list[schemas.UserOut])
def search_users(q: str = "", db: Session = Depends(get_db),
                current_user: models.User = Depends(auth.get_current_user)):
    query = q.strip()
    if len(query) < 2:
        return []
    return (
        db.query(models.User)
        .filter(models.User.username.ilike(f"%{query}%"), models.User.id != current_user.id)
        .order_by(models.User.username.asc())
        .limit(20)
        .all()
    )


@app.post("/rooms/{room_id}/members/{user_id}")
def add_room_member(room_id: int, user_id: int, db: Session = Depends(get_db),
                    current_user: models.User = Depends(auth.get_current_user)):
    project = _get_project_or_404(db, room_id)
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the room owner can add members")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    existing = db.query(models.RoomMembership).filter(
        models.RoomMembership.project_id == room_id, models.RoomMembership.user_id == user_id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="That user is already a member")
    db.add(models.RoomMembership(project_id=room_id, user_id=user_id, is_admin=0))
    db.commit()
    return {"ok": True, "username": user.username}


@app.get("/rooms/{room_id}/members", response_model=list[schemas.UserOut])
def list_room_members(room_id: int, db: Session = Depends(get_db),
                      current_user: models.User = Depends(auth.get_current_user)):
    project = _get_project_or_404(db, room_id)
    _require_member(db, project, current_user)
    return (
        db.query(models.User)
        .join(models.RoomMembership, models.RoomMembership.user_id == models.User.id)
        .filter(models.RoomMembership.project_id == room_id)
        .order_by(models.User.username.asc())
        .all()
    )


# ---------- Rooms ----------

@app.get("/rooms", response_model=list[schemas.ProjectOut])
def list_rooms(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    projects = (
        db.query(models.Project)
        .join(models.RoomMembership, models.RoomMembership.project_id == models.Project.id)
        .filter(models.RoomMembership.user_id == current_user.id)
        .order_by(models.Project.created_at.desc())
        .all()
    )
    return [_project_out(db, project, current_user) for project in projects]


@app.post("/rooms", response_model=schemas.ProjectOut)
def create_room(payload: schemas.ProjectCreate, db: Session = Depends(get_db),
                current_user: models.User = Depends(auth.get_current_user)):
    project = models.Project(
        name=payload.name.strip(),
        owner_id=current_user.id,
        password_hash=auth.hash_password(payload.password),
    )
    db.add(project)
    db.flush()
    _ensure_invite_code(db, project)
    db.add(models.RoomMembership(project_id=project.id, user_id=current_user.id, is_admin=1))
    db.commit()
    db.refresh(project)
    return _project_out(db, project, current_user)


@app.post("/rooms/join", response_model=schemas.ProjectOut)
def join_room(payload: schemas.ProjectJoin, db: Session = Depends(get_db),
              current_user: models.User = Depends(auth.get_current_user)):
    project = db.query(models.Project).filter(models.Project.invite_code == payload.invite_code.strip().upper()).first()
    if not project:
        raise HTTPException(status_code=404, detail="Invalid invite code")
    if not project.password_hash or not auth.verify_password(payload.password, project.password_hash):
        raise HTTPException(status_code=403, detail="Incorrect room password")

    existing = db.query(models.RoomMembership).filter(
        models.RoomMembership.project_id == project.id,
        models.RoomMembership.user_id == current_user.id,
    ).first()
    if not existing:
        db.add(models.RoomMembership(project_id=project.id, user_id=current_user.id, is_admin=0))
        db.commit()
    return _project_out(db, project, current_user)


@app.get("/rooms/{room_id}", response_model=schemas.ProjectOut)
def get_room(room_id: int, db: Session = Depends(get_db),
             current_user: models.User = Depends(auth.get_current_user)):
    project = _get_project_or_404(db, room_id)
    _require_member(db, project, current_user)
    return _project_out(db, project, current_user)


@app.delete("/rooms/{room_id}")
async def delete_room(room_id: int, db: Session = Depends(get_db),
                      current_user: models.User = Depends(auth.get_current_user)):
    project = _get_project_or_404(db, room_id)
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the room creator can delete the room")
    await manager.broadcast(room_id, "room_deleted", {"id": room_id})
    db.delete(project)
    db.commit()
    return {"ok": True}


@app.delete("/rooms/{room_id}/membership")
def leave_room(room_id: int, db: Session = Depends(get_db),
               current_user: models.User = Depends(auth.get_current_user)):
    project = _get_project_or_404(db, room_id)
    membership = db.query(models.RoomMembership).filter(
        models.RoomMembership.project_id == room_id,
        models.RoomMembership.user_id == current_user.id,
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this room")

    if project.owner_id == current_user.id:
        replacement = (
            db.query(models.RoomMembership)
            .filter(models.RoomMembership.project_id == room_id, models.RoomMembership.user_id != current_user.id)
            .order_by(models.RoomMembership.joined_at.asc())
            .first()
        )
        if not replacement:
            raise HTTPException(status_code=400, detail="You are the only member. Delete the room instead of leaving it.")
        project.owner_id = replacement.user_id
        replacement.is_admin = 1

    db.delete(membership)
    db.commit()
    return {"ok": True, "new_owner_id": project.owner_id}


@app.get("/rooms/{room_id}/tasks", response_model=list[schemas.TaskOut])
def list_tasks(room_id: int, db: Session = Depends(get_db),
               current_user: models.User = Depends(auth.get_current_user)):
    project = _get_project_or_404(db, room_id)
    _require_member(db, project, current_user)
    return db.query(models.Task).filter(models.Task.project_id == room_id).order_by(models.Task.created_at.desc()).all()


# ---------- Tasks ----------

async def _broadcast_task(room_id: int, event: str, task: models.Task):
    await manager.broadcast(room_id, event, schemas.TaskOut.model_validate(task).model_dump(mode="json"))


@app.post("/rooms/{room_id}/tasks", response_model=schemas.TaskOut)
async def add_task(room_id: int, payload: schemas.TaskCreate, db: Session = Depends(get_db),
                   current_user: models.User = Depends(auth.get_current_user)):
    project = _get_project_or_404(db, room_id)
    _require_member(db, project, current_user)
    task = models.Task(project_id=room_id, username=current_user.username, content=payload.content.strip())
    db.add(task)
    db.commit()
    db.refresh(task)
    await _broadcast_task(room_id, "task_created", task)
    return task


@app.delete("/tasks/{task_id}")
async def remove_task(task_id: int, db: Session = Depends(get_db),
                      current_user: models.User = Depends(auth.get_current_user)):
    task = _get_task_or_404(db, task_id)
    project = _require_task_member(db, task, current_user)
    membership = db.query(models.RoomMembership).filter(
        models.RoomMembership.project_id == project.id,
        models.RoomMembership.user_id == current_user.id,
    ).first()
    is_creator = task.username == current_user.username
    is_admin = bool(membership and membership.is_admin)
    if not (is_creator or is_admin):
        raise HTTPException(status_code=403, detail="Only the task creator or a room admin can delete this task")
    room_id = task.project_id
    db.delete(task)
    db.commit()
    await manager.broadcast(room_id, "task_deleted", {"id": task_id})
    return {"ok": True}


@app.post("/tasks/{task_id}/like", response_model=schemas.TaskOut)
async def like_task(task_id: int, db: Session = Depends(get_db),
                    current_user: models.User = Depends(auth.get_current_user)):
    task = _get_task_or_404(db, task_id)
    _require_task_member(db, task, current_user)
    interaction = db.query(models.Interaction).filter(
        models.Interaction.task_id == task_id, models.Interaction.username == current_user.username
    ).first()
    if not interaction:
        db.add(models.Interaction(task_id=task_id, username=current_user.username, type="like"))
        task.likes += 1
    elif interaction.type == "dislike":
        interaction.type = "like"
        task.likes += 1
        task.dislikes -= 1
    else:
        db.delete(interaction)
        task.likes -= 1
    db.commit()
    db.refresh(task)
    await _broadcast_task(task.project_id, "task_updated", task)
    return task


@app.post("/tasks/{task_id}/dislike", response_model=schemas.TaskOut)
async def dislike_task(task_id: int, db: Session = Depends(get_db),
                       current_user: models.User = Depends(auth.get_current_user)):
    task = _get_task_or_404(db, task_id)
    _require_task_member(db, task, current_user)
    interaction = db.query(models.Interaction).filter(
        models.Interaction.task_id == task_id, models.Interaction.username == current_user.username
    ).first()
    if not interaction:
        db.add(models.Interaction(task_id=task_id, username=current_user.username, type="dislike"))
        task.dislikes += 1
    elif interaction.type == "like":
        interaction.type = "dislike"
        task.dislikes += 1
        task.likes -= 1
    else:
        db.delete(interaction)
        task.dislikes -= 1
    db.commit()
    db.refresh(task)
    await _broadcast_task(task.project_id, "task_updated", task)
    return task


@app.post("/tasks/{task_id}/status/{new_status}", response_model=schemas.TaskOut)
async def set_status(task_id: int, new_status: str, db: Session = Depends(get_db),
                     current_user: models.User = Depends(auth.get_current_user)):
    if new_status not in ("woi", "completed"):
        raise HTTPException(status_code=400, detail="invalid status")
    task = _get_task_or_404(db, task_id)
    _require_task_member(db, task, current_user)
    if task.status == new_status:
        if task.statusby != current_user.username:
            raise HTTPException(status_code=403, detail=f"this task's status is set by {task.statusby}")
        task.status = None
        task.statusby = None
    elif task.status and task.statusby != current_user.username:
        raise HTTPException(status_code=403, detail=f"task is currently '{task.status}' set by {task.statusby}")
    else:
        task.status = new_status
        task.statusby = current_user.username
    db.commit()
    db.refresh(task)
    await _broadcast_task(task.project_id, "task_updated", task)
    return task


# ---------- Comments ----------

@app.get("/tasks/{task_id}/comments", response_model=list[schemas.CommentOut])
def list_comments(task_id: int, db: Session = Depends(get_db),
                  current_user: models.User = Depends(auth.get_current_user)):
    task = _get_task_or_404(db, task_id)
    _require_task_member(db, task, current_user)
    return db.query(models.Comment).filter(models.Comment.task_id == task_id).order_by(models.Comment.created_at.asc()).all()


@app.post("/tasks/{task_id}/comments", response_model=schemas.CommentOut)
async def add_comment(task_id: int, payload: schemas.CommentCreate, db: Session = Depends(get_db),
                      current_user: models.User = Depends(auth.get_current_user)):
    task = _get_task_or_404(db, task_id)
    _require_task_member(db, task, current_user)
    comment = models.Comment(task_id=task_id, username=current_user.username, content=payload.content.strip())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    await manager.broadcast(task.project_id, "comment_created", schemas.CommentOut.model_validate(comment).model_dump(mode="json"))
    return comment


@app.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int, db: Session = Depends(get_db),
                         current_user: models.User = Depends(auth.get_current_user)):
    comment = _get_comment_or_404(db, comment_id)
    project = _require_comment_member(db, comment, current_user)
    if comment.username != current_user.username:
        raise HTTPException(status_code=403, detail="Only the comment creator can delete this comment")
    task_id = comment.task_id
    db.delete(comment)
    db.commit()
    await manager.broadcast(project.id, "comment_deleted", {"id": comment_id, "task_id": task_id})
    return {"ok": True}


def _comment_reaction(comment_id: int, reaction: str, db: Session, current_user: models.User):
    comment = _get_comment_or_404(db, comment_id)
    _require_comment_member(db, comment, current_user)
    interaction = db.query(models.CommentInteraction).filter(
        models.CommentInteraction.comment_id == comment_id,
        models.CommentInteraction.username == current_user.username,
    ).first()
    if not interaction:
        db.add(models.CommentInteraction(comment_id=comment_id, username=current_user.username, type=reaction))
        if reaction == "like": comment.likes += 1
        else: comment.dislikes += 1
    elif interaction.type == reaction:
        db.delete(interaction)
        if reaction == "like": comment.likes -= 1
        else: comment.dislikes -= 1
    else:
        interaction.type = reaction
        if reaction == "like":
            comment.likes += 1
            comment.dislikes -= 1
        else:
            comment.dislikes += 1
            comment.likes -= 1
    db.commit()
    db.refresh(comment)
    return comment


async def _broadcast_comment(comment: models.Comment, event: str):
    await manager.broadcast(comment.task.project_id, event, schemas.CommentOut.model_validate(comment).model_dump(mode="json"))


@app.post("/comments/{comment_id}/like", response_model=schemas.CommentOut)
async def like_comment(comment_id: int, db: Session = Depends(get_db),
                       current_user: models.User = Depends(auth.get_current_user)):
    comment = _comment_reaction(comment_id, "like", db, current_user)
    await _broadcast_comment(comment, "comment_updated")
    return comment


@app.post("/comments/{comment_id}/dislike", response_model=schemas.CommentOut)
async def dislike_comment(comment_id: int, db: Session = Depends(get_db),
                          current_user: models.User = Depends(auth.get_current_user)):
    comment = _comment_reaction(comment_id, "dislike", db, current_user)
    await _broadcast_comment(comment, "comment_updated")
    return comment


# ---------- WebSocket ----------

@app.websocket("/ws/rooms/{room_id}")
async def room_websocket(websocket: WebSocket, room_id: int, token: str):
    try:
        username = auth.decode_token(token)
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    db = next(get_db())
    try:
        user = db.query(models.User).filter(models.User.username == username).first()
        project = db.query(models.Project).filter(models.Project.id == room_id).first()
        if not user or not project:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        membership = db.query(models.RoomMembership).filter(
            models.RoomMembership.project_id == room_id,
            models.RoomMembership.user_id == user.id,
        ).first()
        if not membership:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    finally:
        db.close()

    await manager.connect(room_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
