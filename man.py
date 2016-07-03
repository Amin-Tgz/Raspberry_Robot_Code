#################  Imports ###################
import socket
import time
from Tkinter import *
import cv2
import numpy
from imutils import resize
from threading import Thread
######## Socket => Set Parameters ##########
UDP_IP = "192.168.1.103"
# UDP_IP = 'localhost'
UDP_PORT = 2000
TCP_IP = '192.168.1.6'
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
root.geometry("400x300+30+30")
root.resizable(0,0)
root.title("GUI for Rasperry Robot")
Modes = ["Ball Follower", "Manual"]
val = [1, 2]
Buttons = ["Right", "LEFT", "Down", "UP"]
background_image=PhotoImage(file="Q.gif")
background_label = Label(root, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
##
discon = cv2.imread('disco.jpg')
########
PX = "0.20"
IX = "0.05"
DX = "0.01"
#
PY = "0.2"
IY = "0.01"
DY = "0.02"
######### Functions ###########
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)  # receive from client with this method
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


def Ball():
    v.set(1)
    Setting_Send("Auto")


def Man():
    v.set(2)
    Setting_Send("Manual")


def Setting_Send(MESSAGE):
        sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))

def Get_image():
    sss=time.time()
    xx=0
    while True:
        length = recvall(conn, 1024)
        try:
            stringData = recvall(conn, int(length))
        except TypeError:
            print ("Connection Lost!\ntry to reconnect plz\n    o__o")
            quit()
        data = numpy.fromstring(stringData, dtype='uint8')
        decimg = cv2.imdecode(data, 1)
        image_resized = resize(decimg,480,320,inter=cv2.INTER_CUBIC)# inter = cv2.INTER_LINEAR \\ INTER_CUBIC \\INTER_LANCZOS4
        cv2.imshow("Recieved", image_resized)
        xx += 1
        if cv2.waitKey(32) == ord(' '):
            e=time.time()
            print (xx/(e-sss))
            cv2.imshow("Recieved",discon)
            cv2.waitKey(1500)
            root.quit()
            break

def key(event):
    if event.keysym == 'F4':
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

##########   GUI - CONFIG      #########

Label_GUI = Label(root,
                  text="""Choose Mode :""",
                  compound=CENTER,
                  justify=LEFT,
                  padx=20
                  ).place(x=3, y=10, width=100, height=20)
############################################
Label_Pan = Label(root,
                  text="""Pan:""",
                  compound=CENTER,
                  justify=LEFT,
                  padx=1
                  ).place(x=15, y=215, width=30, height=20)
Label_Tilt = Label(root,
                  text="""Tilt:""",
                  compound=CENTER,
                  justify=LEFT,
                  padx=1
                  ).place(x=200, y=215, width=30, height=20)
############################################
Label_PP = Label(root,
                  text="""P""",
                  compound=CENTER,
                  justify=LEFT,
                  padx=20
                  ).place(x=65, y=180, width=20, height=20)
EPP = Entry(root, bd =5)
EPP.place(x=100, y=180, width=60, height=30)
EPP.bind("<Return>", set_PP)
EPP.insert(5,PX)
######
Label_IP = Label(root,
                  text="""I""",
                  compound=CENTER,
                  justify=LEFT,
                  padx=20
                  ).place(x=65, y=215, width=20, height=20)
EIP = Entry(root, bd =5)
EIP.place(x=100, y=215, width=60, height=30)
EIP.insert(0,IX)
EIP.bind("<Return>", set_IP)
######
Label_DP = Label(root,
                  text="""D""",
                  compound=CENTER,
                  justify=LEFT,
                  padx=20
                  ).place(x=65, y=250, width=20, height=20)
EDP = Entry(root, bd =5)
EDP.place(x=100, y=250, width=60, height=30)
EDP.insert(0,DX)
EDP.bind("<Return>", set_DP)
############################################
Label_PT = Label(root,
                  text="""P""",
                  compound=CENTER,
                  justify=LEFT,
                  padx=20
                  ).place(x=250, y=180, width=20, height=20)
EPT = Entry(root, bd =5)
EPT.place(x=300, y=180, width=60, height=30)
EPT.insert(0,PY)
EPT.bind("<Return>", set_PT)

Label_IT = Label(root,
                  text="""I""",
                  compound=CENTER,
                  justify=LEFT,
                  padx=20
                  ).place(x=250, y=215, width=20, height=20)
EIT = Entry(root, bd =5)
EIT.place(x=300, y=215, width=60, height=30)
EIT.insert(0,IY)
EIT.bind("<Return>", set_IT)

Label_DT = Label(root,
                  text="""D""",
                  compound=CENTER,
                  justify=LEFT,
                  padx=20
                  ).place(x=250, y=250, width=20, height=20)
EDT = Entry(root, bd =5)
EDT.place(x=300, y=250, width=60, height=30)
EDT.insert(0,DY)
EDT.bind("<Return>", set_DT)


RB1 = Radiobutton(root,
                  text=Modes[0],
                  padx=20,
                  variable=v,
                  command=Ball,
                  value=val[0]).place(x=3, y=40, width=110, height=20)

RB2 = Radiobutton(root,
                  text=Modes[1],
                  padx=20,
                  variable=v,
                  command=Man,
                  value=val[1]).place(x=5, y=65, width=80, height=20)

B1 = Button(root, text=Buttons[1], bg=color[0], fg="red", bd=12, command=Left()).place(x=100, y=95, width=80,height=45)  # LEFT
B2 = Button(root, text=Buttons[2], bg=color[0], fg='red', bd=12, command=Down()).place(x=185, y=95, width=80,height=45)  # Down
B3 = Button(root, text=Buttons[3], bg=color[0], fg='red', bd=12, command=Up()).place(x=185, y=45, width=80,height=45)  # UP
B4 = Button(root, text=Buttons[0], bg=color[0], fg='red', bd=12, command=Right()).place(x=270, y=95, width=80,height=45)  # Right

##########################################################################################
##########  Thread start ##########
Image_thread = Thread(target=Get_image)
Image_thread.start()
root.bind_all('<Key>', key)
root.mainloop()
