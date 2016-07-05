# -*- coding: utf-8 -*-
'''
Import Necessary Library

.
'''
from threading import Thread
from serial import Serial
import socket
from imutils.video import VideoStream
import cv2
from numpy import array
from time import sleep
from math import sin
from math import radians
from math import floor

'''
Socket => Set Parameters

TCP & UDP Address set
for use on one pc : UDP_IP = 'localhost'
Port must be above 1000 so don't need Permission
'''
UDP_IP = "192.168.1.103"
UDP_PORT = 2000
TCP_IP = '192.168.1.6'
TCP_PORT = 2222
TCP_Socket = socket.socket()
TCP_Socket.connect((TCP_IP, TCP_PORT))

# <editor-fold desc="Serial Port in Pi3↓">
'''
On Pi3 Serial Port changed to ttyAMA0
Note!!! for correct serial in jessi version if DeviceTree Not changed =>
    http://www.briandorey.com/post/Raspberry-Pi-3-UART-Overlay-Workaround
    http://www.briandorey.com/post/Raspberry-Pi-3-UART-Boot-Overlay-Part-Two
https://pythonhosted.org/pyserial/shortintro.html
'''
# </editor-fold>
Serial_Port = Serial('/dev/ttyAMA0', 115200, timeout=1)

# <editor-fold desc="Pre_Needed for Start Video Processing ↓">
'''
For JPEG, it can be a quality ( CV_IMWRITE_JPEG_QUALITY )
from 0 to 100 (the higher is the better). Default value is 95.
http://docs.opencv.org/3.0-beta/modules/imgcodecs/doc/reading_and_writing_images.html

for green L/H use range detector =>
https://github.com/jrosebr1/imutils/blob/master/bin/range-detector
'''
# </editor-fold>
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
Video_Stream = VideoStream(usePiCamera=1 > 0).start()  # => VideoStream(usePiCamera=1 > 0,resolution=(640,480)).start()
sleep(2.0)
greenLower = (49, 75, 51)
greenUpper = (100, 255, 255)

# <editor-fold desc="flag of autonomous ↓">
'''
initial with Manual Mode
'''
# </editor-fold>
autonomous_flag = 0

# <editor-fold desc="Controller Paramteter Set ↓">
'''
PID Parameter
Reference
Define Variables
Set_Points
'''
# </editor-fold>
x_degree = 105
y_degree = 90

x0 = 160
y0 = 120
x = 0
y = 0
radius = 0
t = 0
#######
err_y_sum = 10
err_x_sum = 10
err_x_past = 10
err_y_past = 10
#######
PX = 0.21
IX = 0.045
DX = 0.02
#
PY = 0.21
IY = 0.025
DY = 0.02
#

# <editor-fold desc="PID Controller ↓">
'''
1.find error :
    err_x = H - x0 (H as input from img_proc and x0 as half of width img
    err_y = V - y0 (So on..)
2.calculate PID result :
    PX * err_x + IX * err_x_sum + DX * err_x_diff
    PY * err_y + IY * err_y_sum + DY * err_y_diff
3.add bias 105 for servo degree Pan & 95 for Tilt
    x_degree = int(105 - PX * err_x + IX * err_x_sum + DX * err_x_diff)
    y_degree = int(PY * err_y + IY * err_y_sum + DY * err_y_diff + 95)
4.Send By serial :
    Serial_Port.write(('P,' + str(x_degree)).encode())
    Serial_Port.write(('T,' + str(y_degree)).encode())

Note!!!
    65<pos1<130   delay=25      for Tilt ref 95
    30<pos2<175   delay=10-20   for Pan  105
    Horiz = int((x/400)*145+30)
    Vert  = int((y/300)*65+65)
'''


# </editor-fold>
def PID_Controller(ball_x, ball_y, ball_radius):
    global err_x_past
    global err_y_past
    global err_y_sum
    global err_x_sum

    err_x = ball_x - x0
    err_x_diff = err_x - err_x_past
    err_x_sum = + err_x
    err_x_past = err_x

    err_y = ball_y - y0
    err_y_sum = + err_y
    err_Y_diff = err_y - err_y_past
    err_y_past = err_y

    if err_x_sum > 150:
        err_x_sum = 150
    if err_x_sum < -150:
        err_x_sum = -150

    if err_y_sum > 140:
        err_y_sum = 140
    if err_y_sum < -140:
        err_y_sum = -140
    if err_x_diff > 100:
        err_x_diff = 100
    if err_x_diff < -80:
        err_x_diff = -80
    if err_Y_diff > 80:
        err_Y_diff = 80
    if err_Y_diff < -80:
        err_Y_diff = -80

    x_degree = int(105 - PX * err_x + IX * err_x_sum + DX * err_x_diff)
    # print (x_degree,'x')
    if x_degree > 165:
        x_degree = 165
    if x_degree < 45:
        x_degree = 45

    y_degree = int(PY * err_y + IY * err_y_sum + DY * err_Y_diff + 95)
    # print (y_degree,'y')
    if y_degree < 25:
        y_degree = 25
    if y_degree > 130:
        y_degree = 130

    # serial.write(b'P,{}'.format).x_degree
    Serial_Port.write(('P,' + str(x_degree)).encode())
    Serial_Port.write(('T,' + str(y_degree)).encode())
    ################################
    Pwm_L = 0
    Pwm_R = 0
    teta = x_degree - 100
    # print(PX * err_x + IX * err_x_sum + DX * err_x_diff , "outPID")
    Pwm_L -= 370 * sin(radians(teta))
    Pwm_R += 370 * sin(radians(teta))
    # Pwm_L-= teta * 5.5
    # Pwm_R+= teta * 5.5
    ####
    if Pwm_L > 255:
        Pwm_L = 255
    elif -100 <= Pwm_L and Pwm_L <= 100:
        if ball_radius < 17:
            Pwm_L = 150
        elif ball_radius > 70:
            Pwm_L = -150
        else:
            Pwm_L = 0
    elif Pwm_L < -255:
        Pwm_L = -255
    ####
    if Pwm_R > 255:
        Pwm_R = 255
    elif -100 <= Pwm_R and Pwm_R <= 100:
        if ball_radius < 17:
            Pwm_R = 150
        elif ball_radius > 70:
            Pwm_R = -150
        else:
            Pwm_R = 0
    elif Pwm_R < -255:
        Pwm_R = -255
    # print(Pwm_L, 'L')

    ###
    if Pwm_L > 0:
        Serial_Port.write(('L,' + str(int(Pwm_L) + 75)).encode())
    elif Pwm_L < 0:
        Serial_Port.write(('F,' + str(int(floor(-1 * Pwm_L)) + 75)).encode())
    elif Pwm_L == 0:
        Serial_Port.write(('L,' + str(0)).encode())
    # print(Pwm_R, 'R')

    if Pwm_R > 0:
        Serial_Port.write(('R,' + str(Pwm_R + 75)).encode())
    elif Pwm_R < 0:
        Serial_Port.write(('J,' + str(int(floor(-1 * Pwm_R)) + 75)).encode())
    elif Pwm_R == 0:
        Serial_Port.write(('R,' + str(0)).encode())


# <editor-fold desc="Socket Send Image ↓">
'''
cv2.imencode
    Encodes an image into a memory buffer.
    Python: cv2.imencode(ext, img[, params]) → retval, buf
    Parameters:
        ext – File extension that defines the output format.
        img – Image to be written.
        buf – Output buffer resized to fit the compressed image.
        params – Format-specific parameters. See imwrite()

'''


# </editor-fold>
def socket_send(frame_get):
    result, imgencode = cv2.imencode('.jpg', frame_get, encode_param)
    data = array(imgencode)
    stringdata = data.tostring()
    try:
        TCP_Socket.send((str(len(stringdata)).encode()).ljust(16))
        TCP_Socket.send(stringdata)
    except:
        print("    OOPS!   \nConnection Terminated by HOST!\nThread one has been Killed!\n   :|  ")
        quit()

# <editor-fold desc="Second Thread -> Get Setting ↓">
'''
socket.recvfrom(bufsize[, flags])
Receive data from the socket.
The return value is a pair (string, address) where string is a string representing
the data received and address is the address of the socket sending the data.
See the Unix manual page recv(2) for the meaning of the optional argument flags;
it defaults to zero.
(The format of address depends on the address family.)

get setting by UDP connection and update flags
'''


# </editor-fold>
def get_setting():
    global autonomous_flag

    global x_degree
    global y_degree

    global PX
    global IX
    global DX

    global PY
    global IY
    global DY

    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        sock.bind((UDP_IP, UDP_PORT))
        string_received, address = sock.recvfrom(16)
        settings = string_received.decode()
        if settings == 'Up':
            Serial_Port.write(('L,175').encode())
            Serial_Port.write(('R,175').encode())
        elif settings == 'Down':
            Serial_Port.write(('F,175').encode())
            Serial_Port.write(('J,175').encode())
        elif settings == 'Left':
            Serial_Port.write(('R,185').encode())
            Serial_Port.write(('F,175').encode())
        elif settings == 'Right':
            Serial_Port.write(('J,185').encode())
            Serial_Port.write(('L,175').encode())
        elif settings == 'Stop':
            Serial_Port.write(('S,5').encode())
        elif settings == 'Pan+':
            x_degree -= 5
            if x_degree < 150:
                Serial_Port.write(('P,' + str(x_degree)).encode())
            else:
                x_degree = 150
        elif settings == 'Pan-':
            x_degree = x_degree + 5
            if x_degree > 50:
                Serial_Port.write(('P,' + str(x_degree)).encode())
            else:
                x_degree = 50
        elif settings == 'Tilt-':
            y_degree += 5
            if y_degree < 150:
                Serial_Port.write(('T,' + str(y_degree)).encode())
            else:
                y_degree = 150
        elif settings == 'Tilt+':
            y_degree -= 5
            if y_degree > 10:
                Serial_Port.write(('T,' + str(y_degree)).encode())
            else:
                y_degree = 10

        elif settings == 'Auto':
            autonomous_flag = 1
        elif settings == 'Manual':
            autonomous_flag = 0

        elif settings[0] == 'P' and settings[1] == 'P':
            PX = float(settings[3:])
            print(PX, "set as PX")
        elif settings[0] == 'I' and settings[1] == 'P':  ## for Pan
            IX = float(settings[3:])
            print(IX, "set as IX")
        elif settings[0] == 'D' and settings[1] == 'P':
            DX = float(settings[3:])
            print(DX, "set as DX")

        elif settings[0] == 'P' and settings[1] == 'T':
            PY = float(settings[3:])
            print(PY, "set as PY")
        elif settings[0] == 'I' and settings[1] == 'T':  ## for Tilt
            IY = float(settings[3:])
            print(IY, "set as IY")
        elif settings[0] == 'D' and settings[1] == 'T':
            DY = float(settings[3:])
            print(DY, "set as DY")
    return 0

# <editor-fold desc="Image Processing Algortim ↓">
'''



'''


# </editor-fold>
def ball_tracking():
    global x
    global y
    global radius

    frame = Video_Stream.read()

    # <editor-fold desc="Image Blurring ↓">
    '''
    Image Blurring (Image Smoothing) :
    Image blurring is achieved by convolving
    the image with a low-pass filter kernel.
    It is useful for removing noises.
    It actually removes high frequency content (eg: noise, edges) from the image
    => http://docs.opencv.org/3.1.0/d4/d13/tutorial_py_filtering.html

    '''
    # </editor-fold>
    # blurred = cv2.GaussianBlur(frame, (11, 11), 0)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # <editor-fold desc="cv.InRangeS ↓">
    '''
    Python: cv.InRange(src, lower, upper, dst) → None
    Checks if array elements lie between the elements of two other arrays.
    Parameters:
    src – first input array.
    lowerb – inclusive lower boundary array or a scalar.
    upperb – inclusive upper boundary array or a scalar.
    dst – output array of the same size as src and CV_8U type.

    '''


# </editor-fold>
    mask = cv2.inRange(hsv, greenLower, greenUpper)

    # <editor-fold desc="cv2.morphologyEx ↓">
    '''
    Morphological transformations are some simple operations based on the image shape.
    It is normally performed on binary images.
    It needs two inputs, one is our original image,
    second one is called structuring element or kernel
    which decides the nature of operation.
    Two basic morphological operators are Erosion and Dilation.
    Then its variant forms like Opening, Closing,
    Gradient etc also comes into play.

    '''


# </editor-fold>
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, None, iterations=2)

    # <editor-fold desc="cv2.erode ↓">
    '''
    Erosion :
    The basic idea of erosion is just like soil erosion only,
    it erodes away the boundaries of foreground object
    (Always try to keep foreground in white).
    So what it does? The kernel slides through the image (as in 2D convolution).
    A pixel in the original image (either 1 or 0)
    will be considered 1 only if all the pixels under the kernel is 1,
    otherwise it is eroded (made to zero).
    So what happends is that, all the pixels near boundary
    will be discarded depending upon the size of kernel.
    So the thickness or size of the foreground object decreases
    or simply white region decreases in the image.
    It is useful for removing small white noises,
    detach two connected objects etc.
    '''


    # </editor-fold>
    # mask = cv2.erode(mask, None, iterations=2)

    # <editor-fold desc="cv2.dilate ↓">
    '''
    dilation:
    It is just opposite of erosion. Here,
    a pixel element is ‘1’ if at least one pixel under the kernel is ‘1’.
    So it increases the white region in the image or size of foreground object increases.
    Normally, in cases like noise removal, erosion is followed by dilation.
    Because, erosion removes white noises, but it also shrinks our object.
    So we dilate it.
    Since noise is gone, they won’t come back, but our object area increases.
    It is also useful in joining broken parts of an object.


    '''


    # </editor-fold>
    # mask = cv2.dilate(mask, None, iterations=2)

    # <editor-fold desc="cv2.findContours ↓">
    '''
    We start by computing the contours of the object(s) in the image.
    We specify an array slice of -2
    to make the cv2.findContours  function compatible with both OpenCV 2.4 and OpenCV 3.
    cv2.findContours  changed in ver 2 & 3.

    makes a check to ensure at least one contour was found in the mask .
    Provided that at least one contour was found,
    we find the largest contour in the contours  list on Line 66,
    compute the minimum enclosing circle of the blob,
    and then compute the center (x, y)-coordinates
    '''


    # </editor-fold>
    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    if len(contours) > 0:
        # <editor-fold desc="cv2.contourArea ↓">
        '''
        cv2.contourArea :
        Calculates a contour area
        The function computes a contour area. Similarly to moments , the area is computed using the Green formula.
        Thus, the returned area and the number of non-zero pixels,
        if you draw the contour using drawContours or fillPoly , can be different.
        Also, the function will most certainly give a wrong results for contours with self-intersections.


        '''


        # </editor-fold>
        c = max(contours, key=cv2.contourArea)

        # <editor-fold desc="minEnclosingCircle ↓">
        '''
        minEnclosingCircle
        Finds a circle of the minimum area enclosing a 2D point set.
        Parameters:
        . points –
        Input vector of 2D points, stored in:

        std::vector<> or Mat (C++ interface)
        CvSeq* or CvMat* (C interface)
        Nx2 numpy array (Python interface)
        . center – Output center of the circle.
        . radius – Output radius of the circle.
        The function finds the minimal enclosing circle of
        a 2D point set using an iterative algorithm.
        See the OpenCV sample minarea.cpp .

        '''


        # </editor-fold>
        # ((x, y), radius) = cv2.minEnclosingCircle(c)

        # <editor-fold desc="cv2.moments ↓">
        '''
        cv2.moments :
        Image moments help you to calculate some features like center of mass of the object,
        area of the object etc
        The function cv2.moments() gives a dictionary of all moment values calculated.
        From this moments, you can extract useful data like area, centroid etc.
        Centroid is given by the relations, Cx=M10/M00 and Cy=M01/M00

        '''


        # </editor-fold>
        img_moments = cv2.moments(c)

        try:
            center = (int(img_moments["m10"] / img_moments["m00"]), int(img_moments["m01"] / img_moments["m00"]))
        except:
            print("ERROR")
        if radius > 10 and radius < 90:
            # print (radius)
            # <editor-fold desc="cv.Circle ↓">
            '''
            Python: cv.Circle(img, center, radius, color, thickness=1, lineType=8, shift=0) → None¶

            Parameters:
            img – Image where the circle is drawn.
            center – Center of the circle.
            radius – Radius of the circle.
            color – Circle color.
            thickness – Thickness of the circle outline, if positive. Negative thickness means that a filled circle is to be drawn.
            lineType – Type of the circle boundary. See the line() description.
            shift – Number of fractional bits in the coordinates of the center and in the radius value.
            The function circle draws a simple or filled circle with a given center and radius.
            '''


            # </editor-fold>
            cv2.circle(frame, center, int(radius),
                       (0, 255, 255), 2,cv2.LINE_AA)
            # cv2.circle(frame, center, int(radius),
            #            (255,0 ,0), 2,cv2.LINE_AA)

            # print (int(x), int(y))
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            # print (center[0],center[1])
            PID_Controller(center[0],center[1], radius)
            # PID_Controller(x, y, radius)
        else:
            Serial_Port.write(('L,0').encode())
            Serial_Port.write(('R,0').encode())

    socket_send(frame)


# <editor-fold desc="Choose How send image? with process/raw ↓">
'''
make decision by autonomous flag
    1 for ball.
    2.for Manual
'''


# </editor-fold>
def make_decision():
    global autonomous_flag
    while True:
        while autonomous_flag == 1:
            ball_tracking()
        while autonomous_flag == 0:
            frame = Video_Stream.read()
            socket_send(frame)

# <editor-fold desc="Thread Started ↓">
'''

'''


# </editor-fold>
t1 = Thread(target=make_decision)
t2 = Thread(target=get_setting)
t2.start()
t1.start()
