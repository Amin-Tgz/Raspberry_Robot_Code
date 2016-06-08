import socket
import time
from Tkinter import *
import socket
import cv2
import numpy
import time
from threading import Thread
# from sys
######## Pre_define functiron_varaiavle ##########
UDP_IP = "192.168.1.103"
UDP_PORT = 2000
TCP_IP = '192.168.1.6'
# TCP_IP = 'localhost'
TCP_PORT = 2222
Socker_Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Socker_Server.bind((TCP_IP, TCP_PORT))
Socker_Server.listen(1)  # get 1 to 5 as arguman for query
conn, addr = Socker_Server.accept()
# show_window=cv2.namedWindow('Image_Received',cv2.WINDOW_AUTOSIZE)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)  # receive from client with this method
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


def Setting_Send(MESSAGE):
    sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
def Get_image():
    while True:
        length = recvall(conn, 16)
        stringData = recvall(conn, int(length))
        data = numpy.fromstring(stringData, dtype='uint8')
        decimg = cv2.imdecode(data, 1)
        cv2.imshow('Image_Received', decimg)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


color = ["navy", "green", "blue", "red"]
root = Tk()
root.wm_iconbitmap('rasp.ico')
v = IntVar()
v.set(2)
root.geometry("390x170+30+30")
root.title("HMI for Raspduino Robot")

Modes = [
    "Ball",
    "Manual"
]
val = [1, 2]
Buttons = [
    "Right",
    "LEFT",
    "Down",
    "UP"
]


def key(event):
    if event.keysym == 'Escape':
        Stop()
        root.quit()
    elif 'Up' == event.keysym:
        Up()
    elif 'Down' == event.keysym:
        Down()
    elif 'Right' == event.keysym:
        Right()
    elif 'Left' == event.keysym:
        Left()
    elif 'Control_R' == event.keysym:
        Stop()
    elif 'F1' == event.keysym:
        v.set(1)
        Ball()
    elif 'F2' == event.keysym:
        v.set(2)
        Man()
    # for camera
    elif 'w' == event.keysym:
        print("W")
        Tilt_U()
    elif 'd' == event.keysym:
        Pan_R()
    elif 'a' == event.keysym:
        Pan_L()
    elif 's' == event.keysym:
        print("S")
        Tilt_D()


def Up():
    Setting_Send("Up")
def Down():
    Setting_Send("Down")
def Left():
    Setting_Send("Left")
def Right():
    Setting_Send("Right")
def Stop():
    Setting_Send("Stop")
def Pan_R():
    Setting_Send("Pan+")
def Pan_L():
    Setting_Send("Pan-")
def Tilt_U():
    Setting_Send("Tilt+")
def Tilt_D():
    Setting_Send("Tilt-")
def Ball():
    Setting_Send("Auto")
def Man():
    Setting_Send("Manual")
Label_GUI = Label(root,
                  text="""Choose Mode :""",
                  compound=CENTER,
                  justify=LEFT,
                  padx=20
                  ).place(x=3, y=10, width=100, height=20)

RB1 = Radiobutton(root,
                  text=Modes[0],
                  padx=20,
                  variable=v,
                  command=Ball,
                  value=val[0]).place(x=5, y=40, width=60, height=20)

RB2 = Radiobutton(root,
                  text=Modes[1],
                  padx=20,
                  variable=v,
                  command=Man,
                  value=val[1]).place(x=5, y=65, width=80, height=20)

B1 = Button(root, text=Buttons[1], bg=color[0], fg="red", bd=12, command=Left()).place(x=95, y=90, width=80,
                                                                                   height=45)  # LEFT
##############
B2 = Button(root, text=Buttons[2], bg=color[0], fg='red', bd=12, command=Down()).place(x=180, y=90, width=80,
                                                                                   height=45)  # Down
#############
B3 = Button(root, text=Buttons[3], bg=color[0], fg='red', bd=12, command=Up()).place(x=180, y=40, width=80,
                                                                                   height=45)  # UP
#############
B4 = Button(root, text=Buttons[0], bg=color[0], fg='red', bd=12, command=Right()).place(x=265, y=90, width=80,
                                                                                   height=45)  # Right
Image_thread = Thread(target=Get_image)
Image_thread.start()
root.bind_all('<Key>', key)
root.mainloop()
