import socket
import cv2
import numpy as np
import requests
from flask import send_file, Flask
from flask import request
from PIL import Image
from io import StringIO


# print(f'ogo')
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.bind(('localhost', 8765))
#     s.listen()
#     conn, addr = s.accept()
#     with conn:
#         print(f'Connected by {addr}')
#         while True:
#             data = conn.recv(1024)
#             if not data:
#                 break
#             conn.sendall(data)
#


def frame_processor(image):
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return grayscale

app = Flask(__name__)

@app.route('/get_image')
def get_image():
    url = 'http://localhost:8080/photo.png'
    resp = requests.get(url, stream=True).raw
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return send_file(image, mimetype='image/gif')

if __name__ == '__main__':
    app.run(port=7000, debug=True)
