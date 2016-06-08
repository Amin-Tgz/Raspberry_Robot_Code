#################  Imports ###################
import socket
import time
from Tkinter import *
import cv2
import numpy
from threading import Thread

######## Socket => Set Parameters ##########
UDP_IP = "192.168.137.164"
UDP_PORT = 2000
TCP_IP = '0.0.0.0'
TCP_PORT = 2222
Socker_Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Socker_Server.bind((TCP_IP, TCP_PORT))
Socker_Server.listen(1)
conn, addr = Socker_Server.accept()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
######## GUI_TK  => Set Parameters ##########
color = ["navy", "green", "blue", "red"]
root = Tk()
root.wm_iconbitmap('rasp.ico')
v = IntVar()
v.set(2)
root.geometry("390x170+30+30")
root.title("HMI for Raspduino Robot")
Modes = ["Ball", "Manual"]
val = [1, 2]
Buttons = ["Right", "LEFT", "Down", "UP"]


######### Functions ###########
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

def key(event):
    if event.keysym == 'Escape':
        root.quit()
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

def Ball():
    v.set(1)
    Setting_Send("Auto")

def Man():
    v.set(2)
    Setting_Send("Manual")

def Up():
    Setting_Send("Up")
def Down():
    Setting_Send("Down")
def Left():
    Setting_Send("Left")
def Right():
    Setting_Send("Right")

##########   GUI - CONFIG      #########

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

B1 = Button(root, text=Buttons[1], bg=color[0], fg="red", bd=12, command=Left()).place(x=95, y=90, width=80,height=45)  # LEFT
B2 = Button(root, text=Buttons[2], bg=color[0], fg='red', bd=12, command=Down()).place(x=180, y=90, width=80,height=45)  # Down
B3 = Button(root, text=Buttons[3], bg=color[0], fg='red', bd=12, command=Up()).place(x=180, y=40, width=80,height=45)  # UP
B4 = Button(root, text=Buttons[0], bg=color[0], fg='red', bd=12, command=Right()).place(x=265, y=90, width=80,height=45)  # Right

##########################################################################################
##########  Thread start ##########
Image_thread = Thread(target=Get_image)
Image_thread.start()
root.bind_all('<Key>', key)
root.mainloop()
