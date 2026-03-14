import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from jose import jwt
from sqlalchemy.orm import Session

from app import models
from app.core.config import settings
from app.db.database import get_db
from app.services.socket_manager import manager

ws_router = APIRouter()

@ws_router.websocket("/groups/{group_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    group_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    try:
        payload = payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        id = payload.get("sub")
        if id is None:
            await websocket.close(code=1008)
            return

        user = db.query(models.User).filter(models.User.id == id).first()
        if not user:
            await websocket.close(code=1008)
            return

        if user.role != models.UserRole.ADMIN:
            current_group_ids = [g.id for g in user.groups]
            if group_id not in current_group_ids:
                await websocket.close(code=1008)
                return

    except Exception:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, group_id)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                data_json = json.loads(data)
                content = data_json.get("content")
            except:
                continue

            if not content:
                continue

            new_message = models.Message(
                content=content,
                user_id=user.id,
                group_id=group_id,
                sent_at=datetime.now(timezone.utc)
            )
            db.add(new_message)
            db.commit()
            db.refresh(new_message)

            response_data = {
                "id": new_message.id,
                "content": new_message.content,
                "user_id": user.id,
                "author_name": f"{user.first_name} {user.last_name}",
                "sent_at": str(new_message.sent_at),
                "type": "message"
            }

            await manager.broadcast(response_data, group_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, group_id)
