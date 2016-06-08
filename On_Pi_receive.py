######## Imports #########

from threading import Thread
from serial import Serial
import socket
import imutils
from imutils.video import VideoStream
import cv2
import numpy
from time import sleep

###### Socket Parameters Set #######
UDP_IP = "0.0.0.0"
UDP_PORT = 2000
BUFFER_SIZE = 20
TCP_IP = '192.168.137.1'
TCP_PORT = 2222
my_socket = socket.socket()
my_socket.connect((TCP_IP, TCP_PORT))

########  Serial Port   ########
Serial_Port = Serial('/dev/ttyAMA0', 115200, timeout=1)

######  Pre_Needed for Start Video Processing ######

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
Video_Stream = VideoStream(usePiCamera=1 > 0).start()
sleep(2.0)
greenLower = (49, 75, 51)
greenUpper = (100, 255, 255)

####    flag of autonomous ####
autonomous_flag = 0

## PID Parameter ##
## refrence ##
## define variables ##
##### Set_Point #####
x_degree = 100
y_degree = 85

x0 = 200
y0 = 150
x = 0
y = 0
radius = 0
t = 0
#######
err_Y_sum = 10
err_X_sum = 10
err_x_past = 10
err_y_past = 10
#######
PX = 0.12
IX = 0.009
DX = 0.012
#
PY = 0.2
IY = 0.0035
DY = 0.001


#
###########################
def PID_Controller(H, V, R):
    global t
    global err_x_past
    global err_y_past
    global err_Y_sum
    global err_X_sum

    err_x = H - x0
    err_X_diff = err_x - err_x_past
    err_X_sum = + err_x
    err_x_past = err_x

    err_y = V - y0
    err_Y_sum = + err_y
    err_Y_diff = err_y - err_y_past
    err_y_past = err_y

    if err_X_sum > 150:
        err_X_sum = 150
    if err_X_sum < -150:
        err_X_sum = -150

    if err_Y_sum > 140:
        err_Y_sum = 140
    if err_Y_sum < -140:
        err_Y_sum = -140
    if err_X_diff > 100:
        err_X_diff = 100
    if err_X_diff < -80:
        err_X_diff = -80
    if err_Y_diff > 80:
        err_Y_diff = 80
    if err_Y_diff < -80:
        err_Y_diff = -80

    x_degree = int(100 - PX * err_x + IX * err_X_sum + DX * err_X_diff)
    if x_degree > 165:
        x_degree = 165
    if x_degree < 45:
        x_degree = 45

    y_degree = int(PY * err_y + IY * err_Y_sum + DY * err_Y_diff + 85)
    if y_degree < 25:
        y_degree = 25
    if y_degree > 130:
        y_degree = 130

    # serial.write(b'P,{}'.format).x_degree
    Serial_Port.write(('P,' + str(x_degree)).encode())
    Serial_Port.write(('T,' + str(y_degree)).encode())
    # t = t + 1
    # if t == 3:
    #     t = 0
    #     if R < 17:
    #         Serial_Port.write(('M,1').encode())  # Go Ahead
    #     elif R > 70:
    #         Serial_Port.write(('M,2').encode())  # Back
    #     else:
    #         Serial_Port.write(('M,5').encode())  # Stop

    #     ###

    # if H < 45:
    #     Serial_Port.write(('M,3').encode())  # Left
    # elif H > 360:
    #     Serial_Port.write(('M,4').encode())  # Right
    # else:
    #     Serial_Port.write(('M,5').encode())  # Stop


# 65<pos1<130   delay=25      for Tilt ref 91
#      30<pos2<175   delay=10-20   for Pan  105
#     Horiz = int((x/400)*145+30)
#     Vert  = int((y/300)*65+65)


#############   socket_send   ###################
def socket_send(frame_get):
    global IsRunning
    result, imgencode = cv2.imencode('.jpg', frame_get, encode_param)
    data = numpy.array(imgencode)
    stringdata = data.tostring()
    try:
        my_socket.send((str(len(stringdata)).encode()).ljust(16))
        my_socket.send(stringdata)
    except :
        print ("    OOPS!   \nConnection Terminated by HOST!\nThread one has been Killed!\n   :|  ")
        quit()

#### Thread Two ###
def Get_Setting():
    global autonomous_flag
    global x_degree
    global y_degree
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        sock.bind((UDP_IP, UDP_PORT))
        set, addr = sock.recvfrom(1024)
        if set == b'Up':
            Serial_Port.write(('M,1').encode())
        elif set == b'Down':
            Serial_Port.write(('M,2').encode())
        elif set == b'Left':
            Serial_Port.write(('M,3').encode())
        elif set == b'Right':
            Serial_Port.write(('M,4').encode())
        elif set == b'Stop':
            Serial_Port.write(('M,5').encode())
        elif set == b'Pan+':
            x_degree = x_degree - 5
            if x_degree < 150:
                Serial_Port.write(('P,' + str(x_degree)).encode())
            else:
                x_degree = 150
        elif set == b'Pan-':
            x_degree = x_degree + 5
            if x_degree > 50:
                Serial_Port.write(('P,' + str(x_degree)).encode())
            else:
                x_degree = 50
        elif set == b'Tilt-':
            y_degree = y_degree + 5
            if y_degree < 150:
                Serial_Port.write(('T,' + str(y_degree)).encode())
            else:
                y_degree = 150
        elif set == b'Tilt+':
            y_degree = y_degree - 5
            if y_degree > 10:
                Serial_Port.write(('T,' + str(y_degree)).encode())
            else:
                y_degree = 10
        elif set == b'Auto':
            autonomous_flag = 1

        elif set == b'Manual':
            autonomous_flag = 0


#### Thread one ###
def Ball_tarcking():
    global x
    global y
    global radius
    frame = Video_Stream.read()
    frame = imutils.resize(frame, width=400)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        if radius > 10:
            cv2.circle(frame, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            ##   |    ##
### ==>     ##   |    ##
            ##  \/    ##
            PID_Controller(x, y, radius)
    socket_send(frame)

###### choose wich mode ####
def Camera_Send():
    global autonomous_flag
    while True:
        if autonomous_flag == 1:
            Ball_tarcking()
        elif autonomous_flag == 0:
            frame = Video_Stream.read()
            frame = imutils.resize(frame, width=600)
            socket_send(frame)

######    Threads Start    #######
t1 = Thread(target=Camera_Send)
t2 = Thread(target=Get_Setting)
t2.start()
t1.start()
