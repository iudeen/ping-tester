from typing import Annotated

from asyncer import asyncify
from fastapi import FastAPI, WebSocket, WebSocketException, Query, Depends
from fastapi import status

from ping_test import ping_tester
from ping_test.loggers import logger

app = FastAPI(title="Ping Tester")


async def get_configuration(
        target: Annotated[str | None, Query()] = None,
        interval: Annotated[int, Query(lt=5)] = 0,
        timeout: Annotated[int, Query(le=30)] = 2,
        count: Annotated[int, Query(lt=25)] = 4,
):
    if not target:
        raise WebSocketException(status.WS_1007_INVALID_FRAME_PAYLOAD_DATA, reason="Target required")
    return {
        "target": target, "interval": interval, "timeout": timeout, "count": count
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, config: dict = Depends(get_configuration)):
    try:
        await websocket.accept()
        message = await asyncify(ping_tester)(**config)
        for i in message:
            await websocket.send_text(i.__repr__())
        await websocket.close()
    except Exception as e:
        logger.exception(e)
        await websocket.close(status.WS_1003_UNSUPPORTED_DATA, reason=e.__repr__())
