import requests
from session import session

BASE_URL = "http://127.0.0.1:8000"


class ApiError(Exception):
    pass


def _headers():
    if not session.token:
        return {}
    return {"Authorization": f"Bearer {session.token}"}


def _handle(resp: requests.Response):
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise ApiError(str(detail))
    return resp.json()


def _request(method: str, path: str, **kwargs):
    kwargs.setdefault("headers", _headers())
    kwargs.setdefault("timeout", 5)
    try:
        return _handle(requests.request(method, f"{BASE_URL}{path}", **kwargs))
    except requests.exceptions.RequestException:
        raise ApiError("Can't reach the server. Is the backend running?")


def register(username: str, password: str) -> dict:
    return _request("POST", "/register", json={"username": username, "password": password})


def login(username: str, password: str) -> dict:
    return _request("POST", "/login", data={"username": username, "password": password})


def list_rooms() -> list:
    return _request("GET", "/rooms")


def search_users(query: str) -> list:
    return _request("GET", "/users/search", params={"q": query})


def add_room_member(room_id: int, user_id: int) -> dict:
    return _request("POST", f"/rooms/{room_id}/members/{user_id}")


def list_room_members(room_id: int) -> list:
    return _request("GET", f"/rooms/{room_id}/members")


def create_room(name: str, password: str) -> dict:
    return _request("POST", "/rooms", json={"name": name, "password": password})


def join_room(invite_code: str, password: str) -> dict:
    return _request("POST", "/rooms/join", json={"invite_code": invite_code, "password": password})


def get_room(room_id: int) -> dict:
    return _request("GET", f"/rooms/{room_id}")


def delete_room(room_id: int):
    return _request("DELETE", f"/rooms/{room_id}")


def leave_room(room_id: int):
    return _request("DELETE", f"/rooms/{room_id}/membership")


def list_tasks(room_id: int) -> list:
    return _request("GET", f"/rooms/{room_id}/tasks")


def add_task(room_id: int, content: str) -> dict:
    return _request("POST", f"/rooms/{room_id}/tasks", json={"content": content})


def delete_task(task_id: int):
    return _request("DELETE", f"/tasks/{task_id}")


def like_task(task_id: int) -> dict:
    return _request("POST", f"/tasks/{task_id}/like")


def dislike_task(task_id: int) -> dict:
    return _request("POST", f"/tasks/{task_id}/dislike")


def set_status(task_id: int, new_status: str) -> dict:
    return _request("POST", f"/tasks/{task_id}/status/{new_status}")


def list_comments(task_id: int) -> list:
    return _request("GET", f"/tasks/{task_id}/comments")


def add_comment(task_id: int, content: str) -> dict:
    return _request("POST", f"/tasks/{task_id}/comments", json={"content": content})


def delete_comment(comment_id: int):
    return _request("DELETE", f"/comments/{comment_id}")


def like_comment(comment_id: int) -> dict:
    return _request("POST", f"/comments/{comment_id}/like")


def dislike_comment(comment_id: int) -> dict:
    return _request("POST", f"/comments/{comment_id}/dislike")
