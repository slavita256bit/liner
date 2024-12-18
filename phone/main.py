import json
import socket

import cv2
import base64
import asyncio
import websockets

import signs_processor
from settings import PHONE_IP
from threaded_communicator import ThreadedRobotCommunicator
from threaded_processor import ThreadedProcessor
from threaded_camera import ThreadedCamera


stream_fps = 30
camera = ThreadedCamera()
processor = ThreadedProcessor(camera)
# robot_communicator = ThreadedRobotCommunicator()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('localhost', 8765))
s.listen()
print('Waiting for robot...')
conn, addr = s.accept()
print('Lets go!')

async def stream(websocket):
    while True:
        if processor.frame is not None:
            curvature, delta, frame, time_used = processor.frame
            # frame = cv2.cvtColor(processor.frame, cv2.COLOR_GRAY2BGR)
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            # robot_communicator.send(curvature)
            new_data = str(curvature)
            print(new_data)
            conn.sendall(str.encode(new_data))

            if websocket.open:
                json_string = json.dumps({
                    'img': jpg_as_text,
                    'time': str(time_used),
                    'curvature': curvature,
                    'delta': delta,
                })
                await websocket.send(json_string)

        await asyncio.sleep(1 / stream_fps)

start_server = websockets.serve(stream, PHONE_IP, 8000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
