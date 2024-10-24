import cv2
import base64
import asyncio
import websockets

from threaded_processor import ThreadedProcessor
from threaded_camera import ThreadedCamera


stream_fps = 30
camera = ThreadedCamera()
processor = ThreadedProcessor(camera)
print('Lets go!')

async def stream(websocket):
    while True:
        if processor.frame is not None:
            frame = processor.frame
            # frame = cv2.cvtColor(processor.frame, cv2.COLOR_GRAY2BGR)
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')

            if websocket.open:
                await websocket.send(jpg_as_text)

        await asyncio.sleep(1 / stream_fps)

start_server = websockets.serve(stream, "192.168.1.151", 8000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
