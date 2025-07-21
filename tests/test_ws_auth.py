from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect
from fastapi.testclient import TestClient
class DummyAuth:
    def verify_id_token(self, token, check_revoked=True):
        return
fb_auth = DummyAuth()

router = APIRouter()

@router.websocket("/caption")
async def caption_ws(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return
    try:
        fb_auth.verify_id_token(token, check_revoked=True)
    except Exception:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    try:
        await websocket.receive_bytes()
    except WebSocketDisconnect:
        pass
import pytest

app = FastAPI()
app.include_router(router, prefix="/ws")
client = TestClient(app)


def test_ws_rejects_bad_token(monkeypatch):
    monkeypatch.setattr(fb_auth, "verify_id_token", lambda *a, **k: (_ for _ in ()).throw(Exception()))
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/caption?token=bad") as ws:
            ws.send_bytes(b"hi")

