from threading import Thread
import threading
import socket
import serial
import imutils
from imutils.video import VideoStream
import cv2
import numpy
import time

x_degree = 105
y_degree = 91
UDP_IP = "0.0.0.0"
UDP_PORT = 2000
BUFFER_SIZE = 20
TCP_IP = '192.168.1.6'
TCP_PORT = 2222
my_socket = socket.socket()
my_socket.connect((TCP_IP, TCP_PORT))

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
Video_Stream = VideoStream(usePiCamera=1 > 0).start()
time.sleep(2.0)
Serial_Port = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)


#############   socket_send   ###################

def socket_send(frame_get):
    result, imgencode = cv2.imencode('.jpg', frame_get, encode_param)
    data = numpy.array(imgencode)
    stringdata = data.tostring()
    my_socket.send((str(len(stringdata)).encode()).ljust(16))
    my_socket.send(stringdata)


def PID_Ball_tracking():
    print("mode autonamus")


def Get_Setting():
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
            print("yy")
            y_degree = y_degree + 5
            if y_degree < 150:
                Serial_Port.write(('T,' + str(y_degree)).encode())
            else:
                y_degree = 150
        elif set == b'Tilt+':
            print("tt")
            y_degree = y_degree - 5
            if y_degree > 10:
                Serial_Port.write(('T,' + str(y_degree)).encode())
            else:
                y_degree = 10
        elif set == b'C_M_B':
            PID_Ball_tracking()


###
def Camera_Send():
    while True:
        frame = Video_Stream.read()
        frame = imutils.resize(frame, width=600)
        #cv2.imshow("Image", frame)
        socket_send(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break  #


t1 = Thread(target=Camera_Send)
t2 = Thread(target=Get_Setting)
t2.start()
t1.start()

