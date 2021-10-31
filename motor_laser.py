import time
import RPi.GPIO as GPIO


class StepMotor:

    global pan_motor, tilt_motor 
    global PAN_LIMIT, TIL_LIMIT 
    global PAN_AOV, TILT_AOV 
    global teri_x, teri_y, teri_move
    global bird_detect_time, LASER_SET

    def __init__(self, pin1, pin2, pin3, pin4, speed = 0.01, gear_ratio = 1):
        
        """
        Date : 21.09.01
        Function : Set the pin number, speed, and gear ratio of the step motor
        """
        
        self.gear_ratio = gear_ratio
        self.speed = speed
        self.pins = [pin1, pin2, pin3, pin4]
        self.step_counter = 0
        self.step_count = 8
        self.pos = 0
        self.seq = [[1,0,0,0],[1,1,0,0],[0,1,0,0],[0,1,1,0],[0,0,1,0],[0,0,1,1],[0,0,0,1],[1,0,0,1]]
        GPIO.setmode(GPIO.BCM)
        for pin in self.pins:
            GPIO.setup(pin,GPIO.OUT)
            GPIO.output(pin,False)
        
    def reset(self):

        """
        Date : 21.09.03
        Function : Move the step motor to its initial position
        """

        for i in range(0,5000*self.gear_ratio):
            for pin in range(0,4):
                xpin = self.pins[pin]
                if self.seq[self.step_counter][pin]!=0:
                    GPIO.output(xpin, True)
                else:
                    GPIO.output(xpin, False)
                    
            self.step_counter -= 1           
            if(self.step_counter == self.step_count):
                self.step_counter = 0
            if(self.step_counter < 0):
                self.step_counter = self.step_count - 1
            time.sleep(self.speed)
        
        self.step_counter = 0
        self.pos = 0
 
    def set_angle(self, angle):

        """
        Date : 21.09.04
        Function : The absolute coordinates of the step motor are set
        """

        aim = int(self.gear_ratio*angle * 4096 / 360.0 + 0.5)
        while(self.pos != aim):            
            if(self.pos < aim):
                self.pos +=1
                self.step_counter += 1
                if(self.step_counter == self.step_count):
                    self.step_counter = 0
            
            if(self.pos > aim):
                self.pos -= 1
                self.step_counter -= 1
                if(self.step_counter < 0):
                    self.step_counter = self.step_count - 1
            
            for pin in range(0,4):
                xpin = self.pins[pin]
                if self.seq[self.step_counter][pin]!=0:
                    GPIO.output(xpin, True)
                else:
                    GPIO.output(xpin, False)
            time.sleep(self.speed)

 
    def angle_setting(self,pan,tilt):
        self.pan_motor.set_angle(pan)
        print("pan angle : %d" % (self.pan_motor.get_angle()))
        self.tilt_motor.set_angle(tilt)
        print("tilt angle : %d" % (self.tilt_motor.get_angle()))
            
    def get_angle(self):
        return self.pos * 360 / 4096.0 / self.gear_ratio
        
    def set_speed(self, s):
        self.speed = s
 
    def stepMotor_iniit():
        
        """
        Date : 21.09.14
        Function : Initialization of step motor variables.
        """
        
        global pan_motor,tilt_motor,PAN_LIMIT,TIL_LIMIT,PAN_AOV,TILT_AOV,teri_x,teri_y,teri_move
        pan_motor = StepMotor(2,3,4,17, 0.001, 3)
        tilt_motor = StepMotor(21,20,16,12, 0.001)
        pan_motor.reset()
        tilt_motor.reset()
        pan_motor.set_speed(0.002)
        tilt_motor.set_speed(0.002)
        PAN_LIMIT = 180
        TIL_LIMIT = 180
        PAN_AOV = 42
        TILT_AOV = 56
        teri_x = [126, 162, 198, 234]
        teri_y = [70,110]
        teri_move = [[teri_x[0],teri_y[0]], [teri_x[1],teri_y[0]], [teri_x[2],teri_y[0]], [teri_x[3],teri_y[0]],[teri_x[3],teri_y[1]], 
        [teri_x[2],teri_y[1]], [teri_x[1],teri_y[1]], [teri_x[0],teri_y[1]]]
        

class Laser:

    def __init__(self, pin):
        
        """
        Date : 21.09.12
        Function : Set the pin number, laser on & off
        """
        self.pin = pin
        self.state = False
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin, False)


    def on(self):
        GPIO.output(self.pin, True)
        self.state = True
        
    def off(self):
        GPIO.output(self.pin, False)
        self.state = False


    def laser_th(self):
        
        """
        Date : 21.09.15
        Function : The on/off of the laser is controller.
        """
        global LASER_SET,bird_detect_time
        LASER_SET = False
        bird_detect_time = 0
        
        while 1:
            if LASER_SET == True:
                Laser.on(self)
                bird_detect_time += 1
                time.sleep(1)
                if bird_detect_time == 10:
                    LASER_SET = False
                    bird_detect_time = 0
            else:
                Laser.off(self)