from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..firebase_client import auth as fb_auth
from firebase_admin import exceptions as fb_exc

router = APIRouter()

@router.websocket("/caption")
async def caption_ws(websocket: WebSocket):
    token = None
    auth_header = websocket.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
    if not token:
        token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return
    try:
        fb_auth.verify_id_token(token, check_revoked=True)
    except fb_exc.FirebaseError:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            await websocket.send_text(f"received:{len(data)}")
    except WebSocketDisconnect:
        pass
