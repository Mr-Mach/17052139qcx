# -*- coding: UTF-8 -*-
import RPi.GPIO as GPIO
import time

class Rotation:
#此类表示SG90模块
	frequency=50 #脉冲频率
	delta_theta=0.2 #旋转角度
	min_delay=0.0006 #旋转动作完成时间
	max_delay=0.4 #0~180°旋转理论所需时间
	
	def __init__(self,channel,min_theta,max_theta,init_theta=0):
		self.channel=channel #控制管脚
		if(min_theta<0 or min_theta>180):
			self.min_theta=0
		else:
			self.min_theta=min_theta
		if(max_theta<0 or max_theta>180):
			self.max_theta=180
		else:
			self.max_theta=max_theta
			if(init_theta<min_theta or init_theta>max_theta):
				self.init_theta=(self.min_theta+self.max_theta)/2
			else:
				self.init_theta=init_theta #初始化角度
				self.min_dutycycle=2.5+self.min_theta*10/180
				self.max_dutycycle=2.5+self.max_theta*10/180
		
		
	def setup(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(self.channel,GPIO.OUT)
		self.pwm=GPIO.PWM(self.channel,Rotation.frequency) #PWM
		self.dutycycle=2.5+self.init_theta*10/180 #初始角度
		self.pwm.start(self.dutycycle)
		time.sleep(Rotation.max_delay)
	
	def positiveRotation(self):
#顺时针旋转
		self.dutycycle=self.dutycycle+Rotation.delta_theta*10/180
		if self.dutycycle>self.max_dutycycle:
			self.dutycycle=self.max_dutycycle
		self.pwm.ChangeDutyCycle(self.dutycycle)
		time.sleep(Rotation.min_delay)
		
	def reverseRotation(self):
#逆时针旋转
		self.dutycycle=self.dutycycle-Rotation.delta_theta*10/180
		if self.dutycycle<self.min_dutycycle:
			self.dutycycle=self.min_dutycycle
		self.pwm.ChangeDutyCycle(self.dutycycle)
		time.sleep(Rotation.min_delay)
		
	def specifyRotation(self,theta): 
#旋转角度限定
		if(theta<0 or theta>180):
			return
		self.dutycycle=2.5+theta*10/180
		self.pwm.ChangeDutyCycle(self.dutycycle)
		time.sleep(Rotation.max_delay)
		
	def cleanup(self):
		self.pwm.stop()
		time.sleep(Rotation.min_delay)
		GPIO.cleanup()
