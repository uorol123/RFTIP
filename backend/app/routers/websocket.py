"""
WebSocket 路由 - 实时推送文件处理进度、轨迹处理状态等
"""
import json
import asyncio
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from core.database import get_db

router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # file_id -> list of WebSocket connections
        self.file_connections: Dict[int, Set[WebSocket]] = {}
        # track_task_id -> list of WebSocket connections
        self.track_connections: Dict[str, Set[WebSocket]] = {}
        # 通用连接（intrusions, statistics等）
        self.general_connections: Dict[str, Set[WebSocket]] = {
            "intrusions": set(),
            "statistics": set(),
        }

    async def connect_file(self, websocket: WebSocket, file_id: int):
        """连接到文件处理频道"""
        if file_id not in self.file_connections:
            self.file_connections[file_id] = set()
        self.file_connections[file_id].add(websocket)
        print(f"[WS] Client connected to file:{file_id}, total connections: {len(self.file_connections[file_id])}")

    def disconnect_file(self, websocket: WebSocket, file_id: int):
        """断开文件处理频道连接"""
        if file_id in self.file_connections:
            self.file_connections[file_id].discard(websocket)
            if not self.file_connections[file_id]:
                del self.file_connections[file_id]
            print(f"[WS] Client disconnected from file:{file_id}")

    async def connect_track(self, websocket: WebSocket, task_id: str):
        """连接到轨迹处理频道"""
        if task_id not in self.track_connections:
            self.track_connections[task_id] = set()
        self.track_connections[task_id].add(websocket)
        print(f"[WS] Client connected to track:{task_id}")

    def disconnect_track(self, websocket: WebSocket, task_id: str):
        """断开轨迹处理频道连接"""
        if task_id in self.track_connections:
            self.track_connections[task_id].discard(websocket)
            if not self.track_connections[task_id]:
                del self.track_connections[task_id]

    async def connect_general(self, websocket: WebSocket, channel: str):
        """连接到通用频道"""
        if channel not in self.general_connections:
            self.general_connections[channel] = set()
        self.general_connections[channel].add(websocket)
        print(f"[WS] Client connected to general channel:{channel}")

    def disconnect_general(self, websocket: WebSocket, channel: str):
        """断开通用频道连接"""
        if channel in self.general_connections:
            self.general_connections[channel].discard(websocket)
            if not self.general_connections[channel]:
                del self.general_connections[channel]

    async def broadcast_to_file(self, file_id: int, message: dict):
        """向文件处理频道广播消息"""
        if file_id in self.file_connections:
            disconnected = []
            for connection in self.file_connections[file_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    print(f"[WS] Error sending to file:{file_id}: {e}")
                    disconnected.append(connection)

            # 清理断开的连接
            for conn in disconnected:
                self.disconnect_file(conn, file_id)

    async def broadcast_to_track(self, task_id: str, message: dict):
        """向轨迹处理频道广播消息"""
        if task_id in self.track_connections:
            disconnected = []
            for connection in self.track_connections[task_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    print(f"[WS] Error sending to track:{task_id}: {e}")
                    disconnected.append(connection)

            for conn in disconnected:
                self.disconnect_track(conn, task_id)

    async def broadcast_to_general(self, channel: str, message: dict):
        """向通用频道广播消息"""
        if channel in self.general_connections:
            disconnected = []
            for connection in self.general_connections[channel]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    print(f"[WS] Error sending to {channel}: {e}")
                    disconnected.append(connection)

            for conn in disconnected:
                self.disconnect_general(conn, channel)


manager = ConnectionManager()


@router.websocket("/files/{file_id}")
async def file_processing_websocket(
    websocket: WebSocket,
    file_id: int,
    token: str = Query(...)
):
    """
    文件处理进度 WebSocket

    连接URL: ws://localhost:8000/api/ws/files/{file_id}?token={access_token}
    """
    await websocket.accept()

    # 验证token
    from app.routers.auth import get_current_user_from_token
    try:
        user = get_current_user_from_token(token)
    except Exception:
        await websocket.close(code=1008, reason="Invalid token")
        return

    await manager.connect_file(websocket, file_id)

    try:
        while True:
            # 保持连接，接收心跳
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect_file(websocket, file_id)
    except Exception as e:
        print(f"[WS] Error in file websocket: {e}")
        manager.disconnect_file(websocket, file_id)


@router.websocket("/tracks/{task_id}")
async def track_processing_websocket(
    websocket: WebSocket,
    task_id: str,
    token: str = Query(...)
):
    """
    轨迹处理任务 WebSocket

    连接URL: ws://localhost:8000/api/ws/tracks/{task_id}?token={access_token}
    """
    await websocket.accept()

    # 验证token
    from app.routers.auth import get_current_user_from_token
    try:
        user = get_current_user_from_token(token)
    except Exception:
        await websocket.close(code=1008, reason="Invalid token")
        return

    await manager.connect_track(websocket, task_id)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect_track(websocket, task_id)
    except Exception as e:
        print(f"[WS] Error in track websocket: {e}")
        manager.disconnect_track(websocket, task_id)


@router.websocket("/intrusions")
async def intrusions_websocket(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    实时入侵告警 WebSocket

    连接URL: ws://localhost:8000/api/ws/intrusions?token={access_token}
    """
    await websocket.accept()

    # 验证token
    from app.routers.auth import get_current_user_from_token
    try:
        user = get_current_user_from_token(token)
    except Exception:
        await websocket.close(code=1008, reason="Invalid token")
        return

    await manager.connect_general(websocket, "intrusions")

    # 发送连接成功消息
    await websocket.send_text(json.dumps({
        "type": "connected",
        "channel": "intrusions",
        "message": "已连接到入侵告警频道"
    }))

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect_general(websocket, "intrusions")
    except Exception as e:
        print(f"[WS] Error in intrusions websocket: {e}")
        manager.disconnect_general(websocket, "intrusions")


@router.websocket("/statistics")
async def statistics_websocket(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    系统统计更新 WebSocket

    连接URL: ws://localhost:8000/api/ws/statistics?token={access_token}
    """
    await websocket.accept()

    # 验证token
    from app.routers.auth import get_current_user_from_token
    try:
        user = get_current_user_from_token(token)
    except Exception:
        await websocket.close(code=1008, reason="Invalid token")
        return

    await manager.connect_general(websocket, "statistics")

    # 发送连接成功消息
    await websocket.send_text(json.dumps({
        "type": "connected",
        "channel": "statistics",
        "message": "已连接到统计更新频道"
    }))

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect_general(websocket, "statistics")
    except Exception as e:
        print(f"[WS] Error in statistics websocket: {e}")
        manager.disconnect_general(websocket, "statistics")


# 导出管理器，供其他模块使用
__all__ = ["manager", "router"]
