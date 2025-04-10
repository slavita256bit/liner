import json
import socket
from asyncio import CancelledError

import cv2
import base64
import asyncio
import redis
import websockets
from websockets import ConnectionClosedOK, ConnectionClosedError

from threaded_signs_processor import ThreadedSignsProcessor
from settings import PHONE_IP
from threaded_road_processor import ThreadedRoadProcessor
from threaded_camera import ThreadedCamera


stream_fps = 30
camera = ThreadedCamera()
road_processor = ThreadedRoadProcessor(camera)
# sign_processor = ThreadedSignsProcessor(camera)
r = redis.Redis(host='localhost', port=6379, db=0)

print('Lets go!')

async def stream(websocket):
    while True:
        if road_processor.frame is not None:
            # frame = cv2.cvtColor(processor.frame, cv2.COLOR_GRAY2BGR)

            curvature, delta, frame, time_used = road_processor.frame
            # sign_frame = sign_processor.result


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
        road_processor.stop()
        camera.stop()
        print("Bue!")

if __name__ == "__main__":
    asyncio.run(main())