import json
import socket
from asyncio import CancelledError

import cv2
import base64
import asyncio
import redis
import websockets
from websockets import ConnectionClosedOK, ConnectionClosedError

import signs_processor
from settings import PHONE_IP
from threaded_processor import ThreadedProcessor
from threaded_camera import ThreadedCamera


stream_fps = 30
camera = ThreadedCamera()
processor = ThreadedProcessor(camera)
r = redis.Redis(host='localhost', port=6379, db=0)

print('Lets go!')

async def stream(websocket):
    while True:
        if processor.frame is not None:
            curvature, delta, frame, time_used = processor.frame
            # frame = cv2.cvtColor(processor.frame, cv2.COLOR_GRAY2BGR)
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            if isinstance(delta, int):
                r.set('delta', float(delta))
            else:
                r.set('delta', delta.item())

            json_string = json.dumps({
                'img': jpg_as_text,
                'time': float(time_used),
                'curvature': curvature,
                'delta': delta,
            })

            try:
                await websocket.send(json_string)
            except (ConnectionClosedOK, ConnectionClosedError):
                print("WebSocket connection closed.")
                break

        await asyncio.sleep(1 / stream_fps)


async def main():
    try:
        async with websockets.serve(stream, PHONE_IP, 8000):
            print("WebSocket server started.")
            await asyncio.Future()
    except CancelledError:
        print("Stopping...")
        processor.stop()
        camera.stop()
        print("Bue!")

if __name__ == "__main__":
    asyncio.run(main())