import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect

from main import app

TARGET = "127.0.0.1"

def test_websocket():
    client = TestClient(app)
    with client.websocket_connect(f"/ws?target={TARGET}") as websocket:
        data = websocket.receive_text()
        assert "Reply from" in data


def test_websocket_with_interval():
    client = TestClient(app)
    with client.websocket_connect(f"/ws?target={TARGET}&interval=1") as websocket:
        data = websocket.receive_text()
        assert "Reply from" in data


def test_websocket_without_target():
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect, match=r"Target required"):
        with client.websocket_connect("/ws"):
            pass  # pragma: no cover


def test_websocket_with_bad_target():
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws?target=goo&timeout=1") as ws:
            ws.receive_text()  # pragma: no cover
