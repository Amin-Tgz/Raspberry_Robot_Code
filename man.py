# -*- coding: utf-8 -*-
'''
Import Necessary Library

.
'''
import socket
from time import sleep, time
from Tkinter import *
import cv2
import numpy
from imutils import resize
from threading import Thread

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

'''
Socket Types

AF_INET is an address family that is used to designate
the type of addresses that your socket can communicate with
(in this case, Internet Protocol v4 addresses).
When you create a socket, you have to specify its address family,
 and then you can only use addresses of that type with the socket.
  The Linux kernel, for example, supports 29 other address families
  such as UNIX (AF_UNIX) sockets and IPX (AF_IPX),
  and also communications with IRDA and
  Bluetooth (AF_IRDA and AF_BLUETOOTH, but it is doubtful
  you'll use these at such a low level).
For the most part, sticking with AF_INET for socket programming over a network
 is the safest option. There is also AF_INET6 for Internet Protocol v6 addresses.

 #################
There are two widely used socket types,
stream sockets, and datagram sockets.
 Stream sockets treat communications as a continuous stream of characters,
 while datagram sockets have to read entire messages at once.
  Each uses its own communications protocol.
  Stream sockets use TCP (Transmission Control Protocol),
  which is a reliable, stream oriented protocol,
  and datagram sockets use UDP (Unix Datagram Protocol),
  which is unreliable and message oriented.
'''
Socket_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Socket_TCP.bind((TCP_IP, TCP_PORT))

'''
Socket Listen

argument to listen tells the socket library
that we want it to queue up as many as 5 connect requests
(the normal max) before refusing outside connections
'''
Socket_TCP.listen(1)
conn, addr = Socket_TCP.accept()
Socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  

'''
GUI_TK  => Set Parameters

define colors can choose for button
creat a TK obj
'''
color = ["navy", "green", "blue", "red"]
GUI = Tk()
GUI.wm_iconbitmap('rasp.ico')

'''
Tkinter Variable Classes

x = StringVar() # Holds a string; default value ""
x = IntVar() # Holds an integer; default value 0
x = DoubleVar() # Holds a float; default value 0.0
x = BooleanVar() # Holds a boolean,
returns 0 for False and 1 for True
To read the current value of such a variable,
 call the method get().
 The value of such a variable can be changed
  with the set() method.
'''
v = IntVar()
v.set(2)
GUI.geometry("400x300+30+30")

'''
Forbiden resize!

window.resizable(FALSE,FALSE)
if resizable enable :
    window.minsize(200,100)
    window.maxsize(500,500)
'''
GUI.resizable(0, 0)
GUI.title("GUI for Rasperry Robot")
Modes = ["Ball Follower", "Manual"]
val = [1, 2]
Buttons = ["Right", "LEFT", "Down", "UP"]
background_image=PhotoImage(file="Q.gif")
background_label = Label(GUI, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
discon = cv2.imread('disco.jpg')

'''
Set PID Coefficients

Both for Pan & Tilt
'''
PX = "0.21"
IX = "0.045"
DX = "0.02"
#
PY = "0.21"
IY = "0.025"
DY = "0.02"

'''
Receive With Specified Length

receive from client with this method
'''
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        #<editor-fold desc="Socket.recv :">
        '''
        Socket recv:

        socket.recv(bufsize[, flags]):
        Receive data from the socket.
        The return value is a string representing the data received.
        The maximum amount of data to be received at once is specified by bufsize.
        See the Unix manual page recv(2)
        for the meaning of the optional argument flags;
        it defaults to zero.

        Note!!!!!!! For best match with hardware and network realities,
        the value of bufsize should be a relatively small power of 2,
        for example, 4096.
        '''
         #</editor-fold>
        if not newbuf : return None
        buf += newbuf
        count -= len(newbuf)
    return buf

'''
Some functions with clear duty

Ball=> run when select Ball_Follower Mode
Man => run when select Manual Mode
Setting_Send => send through UDP
'''
def Ball():
    v.set(1)
    Setting_Send("Auto")
def Man():
    v.set(2)
    Setting_Send("Manual")
def Setting_Send(MESSAGE):
        Socket_UDP.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))

'''
Get image from TCP Socket

Resized & show it
'''
def Get_image():
    sss = time()
    xx = 0
    while True:
        #<editor-fold desc="This ↓ Line Means">
        '''
        Get length of input package

        16 byte for length
        '''
        #</editor-fold>
        length = recvall(conn, 16)
        try:
            stringData = recvall(conn, int(length))
        except TypeError:
            print("Connection Lost!\ntry to reconnect plz\n    o__o")
            quit()
        #<editor-fold desc="numpy.fromstring ↓">
        '''
        A new 1-D array initialized from raw binary or text data in a string
        Parameters:
        string : str
        A string containing the data.
        dtype : data-type, optional
        The data type of the array; default: float. For binary input data, the data must be in exactly this format.
        count : int, optional
        Read this number of dtype elements from the data. If this is negative (the default), the count will be determined from the length of the data.
        sep : str, optional
        If not provided or, equivalently, the empty string, the data will be interpreted as binary data; otherwise, as ASCII text with decimal numbers. Also in this latter case, this argument is interpreted as the string separating numbers in the data; extra whitespace between elements is also ignored.
        Returns:
        arr : ndarray
        The constructed array.
        Raises:
        ValueError
        If the string is not the correct size to satisfy the requested dtype and count.
        '''
        #</editor-fold>
        data = numpy.fromstring(stringData, dtype='uint8')
        #<editor-fold desc="cv2.imdecode ↓">
        '''
        Python: cv2.imdecode(buf, flags) → retval

        Parameters:
        buf – Input array or vector of bytes.
        flags – The same flags as in imread() .
        dst – The optional output placeholder for the decoded matrix.
        It can save the image reallocations when the function is called repeatedly for images of the same size.
        The function reads an image from the specified buffer in the memory.
        If the buffer is too short or contains invalid data, the empty matrix/image is returned.

        See imread() for the list of supported formats and flags description.

        Note!!!!! In the case of color images, the decoded images will have the channels stored in B G R order.
        '''
        #</editor-fold>
        DecodeImg = cv2.imdecode(data, 1)
        #<editor-fold desc="cv2.resize ↓">
        '''
        Python: cv.Resize(src, dst, interpolation=CV_INTER_LINEAR) → None
        Parameters:
        src – input image.
        dst – output image;
        interpolation method:

        INTER_NEAREST - a nearest-neighbor interpolation

        INTER_LINEAR - a bilinear interpolation (used by default)  ✓

        INTER_AREA - resampling using pixel area relation.
        It may be a preferred method for image decimation,
        as it gives moire’-free results.
        But when the image is zoomed, it is similar to the INTER_NEAREST method.

        INTER_CUBIC - a bicubic interpolation over 4x4 pixel neighborhood ✓

        INTER_LANCZOS4 - a Lanczos interpolation over 8x8 pixel neighborhood ✓
        '''
        #</editor-fold>
        image_resized = resize(DecodeImg,480,320,inter=cv2.INTER_CUBIC)# inter = cv2.INTER_LINEAR \\ INTER_CUBIC \\INTER_LANCZOS4
        cv2.imshow("Received", image_resized)
        xx += 1
        #<editor-fold desc="cv2.waitKey ↓">
        '''
        Python: cv.WaitKey(delay=0) → int
        Parameters:	delay – Delay in milliseconds.
        0 is the special value that means “forever”.
        '''
        #</editor-fold>
        if cv2.waitKey(1) == ord(' '):
            e = time()
            print(xx / (e - sss))
            cv2.imshow("Received", discon)
            cv2.waitKey(3000)
            GUI.quit()
            break

'''
 Get key Pressed by event & Send

    set_xx functions use for entry's
'''

def key(event):
    #<editor-fold desc="Key Event ↓">
    '''
    . Tkinter also lets you install callables to call back when needed to handle a variety of events.
    However,
    Tkinter does not let you create your own custom events;
    you are limited to working with events predefined by Tkinter itself.
    16.9.1 The Event Object

    General event callbacks must accept one argument event that is a Tkinter event object.
    Such an event object has several attributes describing the event:

    char
    A single-character string that is the key's code (only for keyboard events)

    keysym
    A string that is the key's symbolic name (only for keyboard events)

    num
    Button number (only for mouse-button events); 1 and up

    x, y
    Mouse position, in pixels, relative to the upper left corner of the widget

    x_root , y_root
    Mouse position, in pixels, relative to the upper left corner of the screen

    widget
    The widget in which the event has occurred
    '''
    #</editor-fold>
    if event.keysym == 'F4':
        GUI.quit()
    elif 'Up' == event.keysym:
        Setting_Send("Up")
    elif 'Down' == event.keysym:
        Setting_Send("Down")
    elif 'Right' == event.keysym:
        Setting_Send("Right")
    elif 'Left' == event.keysym:
        Setting_Send("Left")
    elif 'Control_R' == event.keysym:
        Setting_Send("Stop")
    elif 'F1' == event.keysym:
        v.set(1)
        Setting_Send("Auto")
    elif 'F2' == event.keysym:
        v.set(2)
        Setting_Send("Manual")
    # for camera
    elif 'w' == event.keysym:
        Setting_Send("Tilt+")
    elif 'd' == event.keysym:
        Setting_Send("Pan+")
    elif 'a' == event.keysym:
        Setting_Send("Pan-")
    elif 's' == event.keysym:
        Setting_Send("Tilt-")

def Up():
    Setting_Send("Up")
def Down():
    Setting_Send("Down")
def Left():
    Setting_Send("Left")
def Right():
    Setting_Send("Right")

def set_PP(event):
    Setting_Send ('PP,'+EPP.get())
def set_IP(event):
    Setting_Send ('IP,'+EIP.get())
def set_DP(event):
    Setting_Send ('DP,'+EDP.get())

def set_PT(event):
    Setting_Send ('PT,'+EPT.get())
def set_IT(event):
    Setting_Send ('IT,'+EIT.get())
def set_DT(event):
    Setting_Send ('DT,'+EDT.get())

'''
GUI Configs

Label,Entry,Button are placed in window
'''

#<editor-fold desc="Label Choose Mode">
Label_GUI = Label(GUI,
                  text='''Choose Mode :''',
                  compound=CENTER,
                  justify=LEFT,
                  padx=20
                  ).place(x=3, y=10, width=100, height=20)
#</editor-fold>
#<editor-fold desc="Label Pan & Tilt">
Label_Pan = Label(GUI,
                  text='''Pan:''',
                  compound=CENTER,
                  justify=LEFT,
                  padx=1
                  ).place(x=15, y=215, width=30, height=20)
Label_Tilt = Label(GUI,
                   text='''Tilt:''',
                   compound=CENTER,
                   justify=LEFT,
                   padx=1
                   ).place(x=200, y=215, width=30, height=20)
#</editor-fold>
#<editor-fold desc="Label P for Pan">
Label_PP = Label(GUI,
                 text='''P''',
                 compound=CENTER,
                 justify=LEFT,
                 padx=20
                 ).place(x=65, y=180, width=20, height=20)
EPP = Entry(GUI, bd =5)
EPP.place(x=100, y=180, width=60, height=30)
EPP.bind("<Return>", set_PP)
EPP.insert(5,PX)
#</editor-fold>
#<editor-fold desc="Label I for Pan">
Label_IP = Label(GUI,
                 text='''I''',
                 compound=CENTER,
                 justify=LEFT,
                 padx=20
                 ).place(x=65, y=215, width=20, height=20)
EIP = Entry(GUI, bd =5)
EIP.place(x=100, y=215, width=60, height=30)
EIP.insert(0,IX)
EIP.bind("<Return>", set_IP)
#</editor-fold>
#<editor-fold desc="Label D for Pan">
Label_DP = Label(GUI,
                 text='''D''',
                 compound=CENTER,
                 justify=LEFT,
                 padx=20
                 ).place(x=65, y=250, width=20, height=20)
EDP = Entry(GUI, bd =5)
EDP.place(x=100, y=250, width=60, height=30)
EDP.insert(0,DX)
EDP.bind("<Return>", set_DP)
#</editor-fold>
#<editor-fold desc="Label P for Tilt">
Label_PT = Label(GUI,
                 text='''P''',
                 compound=CENTER,
                 justify=LEFT,
                 padx=20
                 ).place(x=250, y=180, width=20, height=20)
EPT = Entry(GUI, bd =5)
EPT.place(x=300, y=180, width=60, height=30)
EPT.insert(0,PY)
EPT.bind("<Return>", set_PT)
#</editor-fold>
#<editor-fold desc="Label I for Tilt">
Label_IT = Label(GUI,
                 text='''I''',
                 compound=CENTER,
                 justify=LEFT,
                 padx=20
                 ).place(x=250, y=215, width=20, height=20)
EIT = Entry(GUI, bd =5)
EIT.place(x=300, y=215, width=60, height=30)
EIT.insert(0,IY)
EIT.bind("<Return>", set_IT)
#</editor-fold>
#<editor-fold desc="Label D for Tilt">
Label_DT = Label(GUI,
                 text='''D''',
                 compound=CENTER,
                 justify=LEFT,
                 padx=20
                 ).place(x=250, y=250, width=20, height=20)
EDT = Entry(GUI, bd =5)
EDT.place(x=300, y=250, width=60, height=30)
EDT.insert(0,DY)
EDT.bind("<Return>", set_DT)

#</editor-fold>
#<editor-fold desc="Radio Button">
RB1 = Radiobutton(GUI,
                  text=Modes[0],
                  padx=20,
                  variable=v,
                  command=Ball,
                  value=val[0]).place(x=3, y=40, width=110, height=20)

RB2 = Radiobutton(GUI,
                  text=Modes[1],
                  padx=20,
                  variable=v,
                  command=Man,
                  value=val[1]).place(x=5, y=65, width=80, height=20)
#</editor-fold>
#<editor-fold desc="Direction Button">
B1 = Button(GUI, text=Buttons[1], bg=color[0], fg="red", bd=12, command=Left).place(x=100, y=95, width=80, height=45)  # LEFT
B2 = Button(GUI, text=Buttons[2], bg=color[0], fg='red', bd=12, command=Down).place(x=185, y=95, width=80, height=45)  # Down
B3 = Button(GUI, text=Buttons[3], bg=color[0], fg='red', bd=12, command=Up).place(x=185, y=45, width=80, height=45)  # UP
B4 = Button(GUI, text=Buttons[0], bg=color[0], fg='red', bd=12, command=Right).place(x=270, y=95, width=80, height=45)  # Right
#</editor-fold>

'''
Threads Start

two thread start here
'''
Image_thread = Thread(target=Get_image)
Image_thread.start()
GUI.bind_all('<Key>', key)
GUI.mainloop()
