import cv2
import numpy as np
import socket
import traceback
import Motor1
import time

WIDTH=640 #视频宽、高
HIGHT=480
center_x=WIDTH/2
center_y=HIGHT/2

def getCenter(points):
#计算目标窗口的中心
    return ((points[0][0]+points[2][0])/2,(points[0][1]+points[2][1])/2)

def getOffset(point):
#计算目标窗口中心在水平位置上与屏幕中心的偏差大小
    return point[0]-center_x

def getSize(point):
#计算目标窗口的对角线长度，作为度量尺度
    return np.sqrt(np.sum(np.square(point[0]-point[2])))

#初始化socket，用于发送实时视频帧
#PC端IP地址
HOST='192.168.1.104'
PORT=5050
server=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server.connect((HOST,PORT))
cap=cv2.VideoCapture(0)

#初始化电机控制模块
motor=Motor1.Motor_Module()
motor.setup()
interval=0.01 #小车单次运动时间
limit_offset=40 #目标窗口的水平偏差（绝对值）超过设定值就控制小车左右转
limit_size_down=200 #目标窗口的尺寸小于设定值则控制小车前进
limit_size_up=250 #目标窗口的尺寸大于设定值则控制小车后退

#先使用Haar级联器检测是否有网球
print('load the cascade...')
ball_cascade=cv2.CascadeClassifier('haarcascade.xml')
ball_x=0
ball_y=0
ball_width=0
ball_height=0
try:
    print('寻找目标')
    while True:
        ret,frame=cap.read() #读取视频帧
        if ret is False:
            continue
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        balls=ball_cascade.detectMultiScale(gray,1.3,25)
        if balls is not None and len(balls)>0:
            #选取尺寸最大的那个窗口作为目标窗口，因为系统只能跟踪一个目标，
            width=balls[:,2]
            index=np.argsort(width)[-1]
            (x,y,w,h)=balls[index]
            ball_x=x
            ball_y=y
            ball_width=w
            ball_height=h
            img=cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2) #绘制目标窗口
            break #一旦检测到目标的存在，就可以退出haar检测了
        ret,imgencode=cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,50]) #编码图像并通过UDP发送出去
        server.sendall(imgencode)
    ret,imgencode=cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,50])
    server.sendall(imgencode)

    #进行CAMShift跟踪
    print('prepare for camshift...')
    track_window=(ball_x,ball_y,ball_width,ball_height) #目标窗口
    roi=frame[ball_y:ball_y+ball_height,ball_x:ball_x+ball_width]
    hsv_roi=cv2.cvtColor(roi,cv2.COLOR_BGR2HSV) #转换成HSV图像
    mask=cv2.inRange(hsv_roi,np.array((30.,0.,0.)),np.array((70.,180.,180.))) #根据网球的颜色（H值）范围，生成目标窗口的掩模，使CAMShift的跟踪目标更精确
    roi_hist=cv2.calcHist([hsv_roi],[0],mask,[180],[0,180]) #生成目标窗口的色彩直方图（根据H值）
    cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX) #直方图归一化
    term_crit=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,10,1) #CAMShift方法的参数

    print('开始追踪目标')
    while True:
        ret,frame=cap.read()
        if ret is False:
            continue
        hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        dst=cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1) #使用上面的色彩直方图对图像进行直方图反向投影
        ret,track_window=cv2.CamShift(dst,track_window,term_crit) #使用CAMShift算法定位目标
        pts=cv2.boxPoints(ret) #得到目标窗口矩形
        pts=np.int0(pts)
        img=cv2.polylines(frame,[pts],True,(255,0,0),2) #绘制目标窗口矩形
        img=cv2.circle(img,(center_x,center_y),8,(0,0,255),-1) #绘制屏幕中心
        (point_ball_x,point_ball_y)=getCenter(pts) #计算目标窗口中心
        img=cv2.circle(img,(point_ball_x,point_ball_y),8,(0,255,0),-1) #绘制目标窗口中心
        offset=getOffset((point_ball_x,point_ball_y)) #计算水平偏差
        img=cv2.putText(img,'offset: %d' % offset,(point_ball_x,point_ball_y-10),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,0),1,cv2.LINE_AA) #把偏差值显示在图像上
        size=getSize(pts) #计算尺寸
        img=cv2.putText(img,'size: %f' % size,(point_ball_x,point_ball_y+10),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,0),1,cv2.LINE_AA)
        ret,imgencode=cv2.imencode('.jpg',img,[cv2.IMWRITE_JPEG_QUALITY,50])
        server.sendall(imgencode)
        # 控制系统运动
        if offset>limit_offset:
            motor.right(interval) #驱动右转interval秒
        elif offset<(-limit_offset):
            motor.left(interval)
        else:
            if size<limit_size_down:
                motor.ahead(interval)
            elif size>limit_size_up:
                motor.rear(interval)

except Exception as e:
    print(traceback.print_exc())
    cap.release()
    motor.stop()