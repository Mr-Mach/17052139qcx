import socket
from MotorModule.Motor import Motor
import traceback
import time
from SteeringModule.Steering import Steering
import cv2
import numpy
# from OledModule.OLED import OLED

def getLocalIp():
#获取树莓派本身IP地址
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',80))
        ip=s.getsockname()[0]
    finally:
        s.close()
    return ip
#摄像头舵机控制
def cameraAction(steer,command):
    if command=='CamUp':
        steer.Up()
    elif command=='CamDown':
        steer.Down()
    elif command=='CamLeft':
        steer.Left()
    elif command=='CamRight':
        steer.Right()


def motorAction(motor,command):
#电机驱动设置
    if command=='DirForward':
        motor.ahead()
    elif command=='DirBack':
        motor.rear()
    elif command=='DirLeft':
        motor.left()
    elif command=='DirRight':
        motor.right()
    elif command=='DirStop':
        motor.stop()

def setCameraAction(command):
#防止摄像头出现单次点击持续转动的情况
    if command=='CamUp' or command=='CamDown' or command=='CamLeft' or command=='CamRight':
        return command
    else:
        return 'CamStop'

            

def main():
#打印IP地址，给OLED屏幕显示变量赋值
    host=getLocalIp()
    print('localhost ip :'+host)
    port=5050

#初始化TCP
    tcpServer=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    tcpServer.bind((host,port))
    tcpServer.setblocking(0) #Set unblock mode
    tcpServer.listen(5)

#初始化电机模块
    motor=Motor(5,21,22,23,24,13)#5,21,22,23,24,13为树莓派与驱动模块连接的GPIO接口
    motor.setup()

#初始摄像头舵机转向模块
    steer=Steering(14,0,180,15,90,180,36,160)
    steer.setup()
    global cameraActionState #设置转向模块的状态变量
    cameraActionState='CamStop'

    #初始化OLED屏幕模块
    # oled=OLED(16,20,0,0)
    # oled.setup()
    #
    # oled.writeArea1(host)
    # oled.writeArea3('State:')
    # oled.writeArea4(' Disconnect')
    while True:
        try:
            time.sleep(0.001)
            (client,addr)=tcpServer.accept()
            print('accept the client!')
            # oled.writeArea4(' Connect')
            client.setblocking(0)
            while True:
                time.sleep(0.001)
                cameraAction(steer,cameraActionState)
                try:
                    data=client.recv(1024)
                    data=bytes.decode(data)
                    if(len(data)==0):
                        print('client is closed')
                        # oled.writeArea4(' Disconnect')
                        break
                    motorAction(motor,data)
                    cameraActionState=setCameraAction(data)
                except socket.error:
                    continue
                except KeyboardInterrupt as e:
                    raise e
        except socket.error:
            pass
        except KeyboardInterrupt:
            motor.clear()
            steer.cleanup()
            tcpServer.close()
            # oled.clear()
        except Exception as e1:
            traceback.print_exc()
            motor.clear()
            steer.cleanup()
            tcpServer.close()
            # oled.clear()
main()
