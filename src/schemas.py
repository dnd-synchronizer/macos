from dataclasses import dataclass


@dataclass
class Auth:
    room: str
    client_id: str


@dataclass
class Status:
    room: str
    client: str
    status: bool
