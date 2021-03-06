import cv2
import numpy
import socket
import time
import struct

#HOST为用户端IP地址
HOST='192.168.1.102'
PORT=5050
WIDTH=320
HEIGHT=240

server=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1) #启用广播
server.connect((HOST,PORT))
capture=cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH,WIDTH)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT,HEIGHT)
print('now starting to send frames...')
try:
    while True:
        time.sleep(0.01)
        success,frame=capture.read()
        if success and frame is not None:
            result,imgencode=cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,90])
            server.sendall(imgencode)
except Exception as e:
    server.sendall(struct.pack('b',1))
    print(e)
    capture.release()
    server.close()
    
