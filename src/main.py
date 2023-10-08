import subprocess
from dataclasses import asdict
from json import dumps, loads
from threading import Thread
from time import sleep
from uuid import uuid4

import requests
from websockets.sync.client import connect

from schemas import Auth, Status

CLIENT_ID = str(uuid4())
ROOM = "some_room"


def switch_dnd(status: Status):
    if status.client == CLIENT_ID:
        return
    if status.status:
        subprocess.Popen(
            "macos-focus-mode enable",
            shell=True,
        )
    else:
        subprocess.Popen(
            "macos-focus-mode disable",
            shell=True,
        )


def get_dnd_status() -> bool:
    return (
        subprocess.Popen(
            'defaults read com.apple.controlcenter "NSStatusItem Visible FocusModes"',
            shell=True,
            stdout=subprocess.PIPE,
        )
        .communicate()[0]
        .decode("utf-8")
        .strip()
        == "1"
    )


def dnd_listener():
    current_status = get_dnd_status()
    while True:
        new_status = get_dnd_status()
        if new_status != current_status:
            current_status = new_status
            print("DND status changed to", current_status)
            response = requests.post(
                "http://127.0.0.1:8000/rooms/change_status/",
                json=asdict(Status(status=current_status, client=CLIENT_ID, room=ROOM)),
            )
            print(response.json())

        sleep(1)


def main():
    Thread(target=dnd_listener, daemon=True).start()
    with connect("ws://localhost:8000/ws/rooms/") as websocket:
        auth = Auth(room="some_room", client_id=CLIENT_ID)
        websocket.send(dumps(asdict(auth)))
        while True:
            response = websocket.recv()
            status = Status(**loads(response))
            switch_dnd(status)


if __name__ == "__main__":
    main()
