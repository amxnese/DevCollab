class Session:
    def __init__(self):
        self.token: str | None = None
        self.username: str | None = None
        self.current_room_id: int | None = None
        self.current_room_name: str | None = None
        self.current_room_owner_id: int | None = None
        self.current_room_invite_code: str | None = None
        self.current_room_is_owner: bool = False

    @property
    def is_logged_in(self) -> bool:
        return self.token is not None

    def login(self, token: str, username: str):
        self.token = token
        self.username = username

    def logout(self):
        self.token = None
        self.username = None
        self.current_room_id = None
        self.current_room_name = None
        self.current_room_owner_id = None
        self.current_room_invite_code = None
        self.current_room_is_owner = False

    def set_room(self, room: dict):
        self.current_room_id = room["id"]
        self.current_room_name = room["name"]
        self.current_room_owner_id = room["owner_id"]
        self.current_room_invite_code = room.get("invite_code")
        self.current_room_is_owner = bool(room.get("is_owner"))


session = Session()
