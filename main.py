import os
import cv2
import threading
import time
from motor_laser import StepMotor as mls
from motor_laser import Laser as mll
from user_tensor import UT as ut
from select import select
from collections import deque
import conn_img as ci
import motor_laser as ml
from flask import Flask, render_template, Response
from tflite_runtime.interpreter import Interpreter

app = Flask(__name__)

global CAMERA_WIDTH,CAMERA_HEIGHT,font,cycle_time,bird_detect_time,bird_find,body_find
global labels,interpreter,LASER_SET,cap, laser

# Initializing Step motor & camera angle
mls.stepMotor_iniit()


# laser settings. 
laser = mll(5)
ml.LASER_SET = False
laser_thr = threading.Thread(target=laser.laser_th)
laser_thr.start()

# Set learning model variables
labels = ut.load_labels()
interpreter = Interpreter('greeneyedboys_pic.tflite')
interpreter.allocate_tensors()
_, input_height, input_width, _ = interpreter.get_input_details()[0]['shape']

# Variables for flag 
CAMERA_WIDTH = 480
CAMERA_HEIGHT = 640
cycle_time = 0 # system cycle time
bird_detect_time = 0 # Time for bird recognition
bird_find = False
body_find = False
font = cv2.FONT_HERSHEY_COMPLEX

def gen_frames():
    global cycle_time,bird_detect_time,bird_find,body_find, LASER_SET
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    
    while 1:   
        while True:
            """
            Data : 21.09.10
            Function : Bring the current area and the number of photos.
            """
            get_index = open('index.txt','r')
            get_control = get_index.read().split(",")
            q = deque(list(get_control[0]))
            now = int(q[0])
            pic_num = int(get_control[1])
            get_index.close()

            """
            Data : 21.08.27
            Function : Current zone time starts.
            """
        
            start_time = time.time()
            ret, img = cap.read()
            img = cv2.rotate(img,cv2.ROTATE_90_CLOCKWISE)    # Video 90 degree rotation toward right
            re_img = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), (320,320))
            res = ut.detect_objects(interpreter, re_img, 0.7)
            k = cv2.waitKey(30) & 0xff

            #currentX, currentY
            cx = ml.teri_move[now][0]
            cy = ml.teri_move[now][1]
            
            # Now description
            if int(cycle_time % 3) == 0:
                print("here is %d section" % (now+1))
                print("Lazer is : ",ml.LASER_SET)
                print("time : ",cycle_time)
                print("pic_num : ", pic_num)
                print("bird : ", bird_find)
                print("body : ", body_find)
                print("bird_detect_time : ",ml.bird_detect_time)
                print("\n")
            
            """
            Data : 21.09.18
            Function : When nothing was discovered
            """
            
            if  ml.LASER_SET == False and bird_find == False: 
                # move now district
                ml.pan_motor.set_angle(cx)
                ml.tilt_motor.set_angle(cy)
                ml.bird_detect_time = 0

            """
            Data : 21.09.25
            Function : When the number of pictures is a multiple of 10, the capacity is checked.
            """
            if pic_num % 10 == 0: 
                stream = os.popen('df -k sendimage')
                output=stream.read()
                used = int(output[-25:-18])
                print("now_used : ",used)
                
                # Send pictures to the Server & Erase pictures of raspberry pi
                if used > 91700000:
                    ci.Connect.send_img()
                    ci.Connect.remove_img()

            """
            Data : 21.09.20
            Function : After 30 seconds, move to the next area.
            """    
            if cycle_time > 30: 
                cycle_time = 0
                i = q.popleft()
                q.append(i)
                s = "".join(q) + "," + str(pic_num)
                out_index = open("index.txt","w")
                out_index.write(s)
                out_index.close()
                break
            
            """
            Data : 21.09.21
            Function : Gets the index of the found object.
            """            
            if res: 
                people_index = next((index for (index,item) in enumerate(res) if item['class_id'] == 1),None)
                bird_index = next((index for (index,item) in enumerate(res) if item['class_id'] == 0),None)
                for result in res:
                    # Square the found object.
                    ymin, xmin, ymax, xmax = result['bounding_box']    
                    xmin = int(max(1,xmin * CAMERA_WIDTH))
                    xmax = int(min(CAMERA_WIDTH, xmax * CAMERA_WIDTH))
                    ymin = int(max(1, ymin * CAMERA_HEIGHT))
                    ymax = int(min(CAMERA_HEIGHT, ymax * CAMERA_HEIGHT))
                    print("box : ", xmin,ymin,xmax, ymax)
                    pic_num += 1 
                    cv2.rectangle(img,(xmin, ymin),(xmax, ymax),(0,255,0),3)
                    cv2.putText(img,labels[int(result['class_id'])],(xmin, min(ymax, CAMERA_HEIGHT-20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),2,cv2.LINE_AA) 
                 
                """
                Data : 21.09.23
                Function : When a bird is found,
                           1. object recognition
                           2. object frame setting,
                           3. X,Y focus coordinates
                """

                if people_index is None:
                    # Finding the vertex of the frame
                    result = res[bird_index]
                    ymin, xmin, ymax, xmax = result['bounding_box']    
                    xmin = int(max(1,xmin * CAMERA_WIDTH))
                    xmax = int(min(CAMERA_WIDTH, xmax * CAMERA_WIDTH))
                    ymin = int(max(1, ymin * CAMERA_HEIGHT))
                    ymax = int(min(CAMERA_HEIGHT, ymax * CAMERA_HEIGHT))
                    # Finding the focus of the frame
                    X_focus = int((xmin+xmax)/2) # The X where the person was found
                    Y_focus = int((ymax+ymin)/2) # The Y where the person was found
                    print("Bird middle point : " ,X_focus,Y_focus)
                    cv2.putText(img, "+", (X_focus,Y_focus), font, 1, (0, 255, 255))
                    # Move the motor from the current position to the focus of the frame
                    pan_angle = cx + ml.PAN_AOV * (X_focus - CAMERA_WIDTH/2.0) / CAMERA_HEIGHT
                    tilt_angle = cy + ml.TILT_AOV * (Y_focus - CAMERA_WIDTH/2.0) / CAMERA_HEIGHT
                    ml.LASER_SET = True

                    # Save the object picture.                                     
                    cv2.imwrite("sendimage/%d" % (pic_num) + ".jpg", img)
                    s = "".join(q) + "," + str(pic_num)
                    out_index = open("index.txt","w")
                    out_index.write(s)
                    out_index.close()
                    ml.pan_motor.set_angle(pan_angle)
                    ml.tilt_motor.set_angle(tilt_angle-8)         
                    bird_find = True
                else:
                    # When a person is discovered
                    print("people detected !!")
                    ml.LASER_SET = False
                    body_find = True
            else:
                # When nothing was discovered
                print("Nothing detected !!!")
                bird_find = False
                body_find = False
            
            # When the camera can't bring the video
            if not ret:
                break
                  
            # concat frame one by one and show result
            else:
                ret, buffer = cv2.imencode('.jpg', img)
                img = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')
                
            end_time = time.time()
            cycle_time = cycle_time + (end_time - start_time)
            if bird_find == True:
                cycle_time = 0

"""
Date : 21.10.25
Function : Monitoring page implementation.
"""
@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/main.html')
def main_page(): 
    return render_template('main.html')

@app.route('/laser1.html')
def laser1_page():
    return render_template('laser1.html')

@app.route('/laserCon1.html')
def laserCon1_page():
    return render_template('laserCon1.html')

@app.route('/login.html')
@app.route('/') 
def login_page():
    return render_template('login.html')
    
@app.route('/password.html') 
def password_page():
    return render_template('password.html')
    
@app.route('/register.html') 
def register_page():
    return render_template('register.html')

@app.route('/inform.html')
def inform_page():
    return render_template('inform.html')

if __name__ == "__main__":
    app.run(host='192.168.1.5')
    #app.run(host='greeneyedboys.com')

