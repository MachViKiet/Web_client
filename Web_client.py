from tkinter import *
import tkinter as tk
import socket
import os
from bs4 import BeautifulSoup
from threading import Thread
import threading 
import time
import sys


def find_content_length(_bytes):
    contentLength = None
    for line in _bytes.split(b'\r\n'):
        if b"Content-Length:" in line:
            contentLength = line
    if contentLength is not None:
        return int(contentLength[16:])
    return None
def check_if_is_chunk(_bytes):
    for line in _bytes.split(b'\r\n'):
        if b"Transfer-Encoding:" in line and b'chunked' in line:
            return True
    return False
def check_if_is_closed(_bytes):
    for line in _bytes.split(b'\r\n'):
        if b"Connection:" in line and b'Close' in line:
            return True
        return False
def get_alive(URL,s,if_closed):
    global killThread
    try:
        protocol, rest = URL.split('://', 1)
        if(rest.find('/')==-1):
            rest=rest+'/'
        host, path = rest.split('/', 1)
        path = '/%s' % path
        request='GET %s HTTP/1.1\r\nHost: %s\r\nConnection: keep-alive\r\nKeep-Alive: timeout, max=50\r\n\r\n' % (path,host)

        request='GET %s HTTP/1.1\r\nHost: %s\r\nConnection: Close\r\nKeep-Alive: timeout, max=50\r\n\r\n' % (path,host)
        try:
            a = s.send(request.encode())
        except Exception as e:
            print(e)
            return False

        recv_length = 4096
        data = None
        content_length = None
        is_chunk = False
        received = 0
        headers=None
        while True:
            if(killThread == True):
                return False
            block = s.recv(recv_length)
            received += len(block)
            if if_closed is True:
                break
            if data is None:
                data = block
                headers = data.split(b"\r\n\r\n")[0]
                received=received-len(headers)-4
                content_length = find_content_length(headers)
                is_chunk = check_if_is_chunk(headers)
                if_closed=check_if_is_closed(headers)
            else:
                data += block
            if (content_length is not None and received == content_length) or \
                (is_chunk == True and block.endswith(b'\r\n\r\n')):
                break 
        raw_headers, content = data.split(b"\r\n\r\n",1)
        if_closed=True
        return content
    except:
        return False
def download_file(url,s,folder):
    global killThread
    if(killThread == True):
        return False
    protocol, rest = url.split('://', 1)
    if(rest.find('/')==-1):
        rest=rest+'/'
    host, path = rest.split('/', 1)
    path="/"+path
    dummy,fn=path.rsplit('/',1)
    if(fn==''):
        fn=f"{host}"+"_index.html"
    else: fn=f"{host}"+"_"+fn
    try:
        print(f'DOWNLOADING : {fn}')
        res = get_alive(f'{url}',s,if_closed=False)
        if(killThread == True):
            return False
        if(res == False):
            return False
        open(f'{folder}/{fn}', 'wb').write(res)
    except Exception as e:
        print(e)
def download_folder(url, folder, fn,s,if_closed):
    global killThread
    try:
        print(f'DOWNLOADING : {fn}')
        res = get_alive(f"{url}/{fn}",s,if_closed)
        if(killThread == True):
            return False
        if(res == False):
            return False
        open(f'{folder}/{fn}', 'wb').write(res)
    except Exception as e:
        print(e)
def run(URL):
    global killThread
    s = socket.socket()
    s.connect(("localhost", 8080))
    try:
        
        #else: 
            #label.configure(text= "Folder is downloading")
            # folder='D:\\Download'
            # if not os.path.exists(folder):
            #     os.mkdir(folder)
            # download_file(URL,s,folder)
            # if(killThread == True):
            #     return False
            # s.close()
        while(True):
            request='GET HTTP/1.1\r\n\r\n'
            a = s.send(request.encode())
        #label.configure(text= "Complete downloading!")
        #buttonClear.configure(state='normal')
    except:
        label.configure(text= "Server unconnected!")
        buttonClear.configure(state='normal')
        return False


def clear():
    buttonDownload.configure(state='normal')
    input.delete(0,END)
    input2.delete(0,END)
    input3.delete(0,END)
    input.configure(state='disable')
    input2.configure(state='disable')
    input3.configure(state='disable')
    label.configure(text= "Enter your URL: ")
def download():
    DSURL=[]
    threads=[]
    buttonDownload.configure(state='disable')
    buttonClear.configure(state='disable')
    if(selected.get() == 1):
        URL = input.get()
        this_thread=Thread(target=run,args=(URL,),kwargs={}, daemon = True)
        if(killThread == True):
            return False
        threads.append(Thread)
        this_thread.start()
    else:
        URL1 = input.get()
        DSURL.append(URL1)
        URL2 = input2.get()
        DSURL.append(URL2)
        URL3 = input3.get() 
        DSURL.append(URL3)
        for link in DSURL:
            if(killThread == True):
                return False
            this_thread=Thread(target=run,args=(link,),kwargs={}, daemon = True)
            threads.append(Thread)
            this_thread.start()
    input.delete(0,END)
    input2.delete(0,END)
    input3.delete(0,END)
    input.configure(state='disable')
    input2.configure(state='disable')
    input3.configure(state='disable')   
    label.configure(text= "Is downloading!")
    print(URL)
def openAllInput():
    clear()
    buttonClear.configure(state='normal')
    input.configure(state='normal')
    input2.configure(state='normal')
    input3.configure(state='normal')
def openInput():
    clear()
    buttonClear.configure(state='normal')
    input.configure(state='normal')
    input2.configure(state='disable')
    input3.configure(state='disable')
def quitWin():
    buttonClose.quit()
    killThread = True
    root.destroy()
 


killThread = False
root = Tk()
step= root.attributes()
step = LabelFrame(root, text="FILE MANAGER", font="Arial 20 bold italic")
root.geometry("400x300")

selected = IntVar()
rad1 = Radiobutton(root,text='Only server', value=1,command= openInput,variable=selected)
rad2 = Radiobutton(root,text='Various servers', value=2,command= openAllInput,variable=selected)
root.title("Client project")
label = Label(root,text='Enter your URL: ',font=('Helvetica 15'))
input = Entry(root,width=30,text = "Enter URL",state="disable")
input2 = Entry(root,width=30 ,text = "URL2",state="disable")
input3 = Entry(root,width=30,text = "URL3",state="disable")
buttonDownload = Button(root,text="       Download       ",command=download,font=('Helvetica 10'),activebackground= "turquoise")
buttonClear =    Button(root,text="          Clear          ",command=clear,font=('Helvetica 10'),activebackground= "turquoise")
buttonClose =    Button(root,text="          Close          ",command=quitWin,font=('Helvetica 10'),activebackground= "turquoise")
label.pack()
input.pack()
input2.pack()
input3.pack()
buttonDownload.pack(pady=10)
buttonClear.pack()
buttonClose.pack(pady=10)
rad1.pack(side='left',fill=BOTH, pady=0, padx=60, expand=True)
rad2.pack(side='right',fill=BOTH, pady=0, padx=49, expand=True)
if(killThread == True):
    sys.exit()
# while(True):
#     root.update_idletasks()
#     root.update()
root.mainloop()
print("System is close")
sys.exit()
