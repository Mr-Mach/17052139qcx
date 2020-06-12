import RPi.GPIO as GPIO
import time
import sys

class Motor_Module(object):
    '''电机控制模块'''
    def __init__(self):
        self.enab_pin=[5,6,13,19] #使能脚编号
        self.inx_pin=[21,22,23,24] #控制脚编号

        self.RightAhead_pin=self.inx_pin[3]
        self.RightBack_pin=self.inx_pin[2]
        self.LeftAhead_pin=self.inx_pin[1]
        self.LeftBack_pin=self.inx_pin[0]

        self.setup()

    def setup(self):
        '''引脚初始化'''
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for pin in self.inx_pin:
            GPIO.setup(pin,GPIO.OUT)
            GPIO.output(pin,GPIO.LOW)
        for pin in self.enab_pin:
            GPIO.setup(pin,GPIO.OUT)
            GPIO.output(pin,GPIO.HIGH)

    def ahead(self,secondvalue=0):
        self.setup()
        GPIO.output(self.RightAhead_pin,GPIO.HIGH)
        GPIO.output(self.LeftAhead_pin,GPIO.HIGH)
        if secondvalue!=0:
           time.sleep(secondvalue)
           self.stop()

    def left(self,secondvalue=0):
        self.setup()
        GPIO.output(self.RightAhead_pin,GPIO.HIGH)
        if secondvalue!=0:
           time.sleep(secondvalue)
           self.stop()

    def right(self,secondvalue=0):
        self.setup()
        GPIO.output(self.LeftAhead_pin,GPIO.HIGH)
        if secondvalue!=0:
           time.sleep(secondvalue)
           self.stop()

    def rear(self,secondvalue=0):
        self.setup()
        GPIO.output(self.RightBack_pin,GPIO.HIGH)
        GPIO.output(self.LeftBack_pin,GPIO.HIGH)
        if secondvalue!=0:
           time.sleep(secondvalue)
           self.stop()

    def stop(self):
        for pin in self.inx_pin:
            GPIO.output(pin,GPIO.LOW)