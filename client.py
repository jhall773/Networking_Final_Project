#!/usr/bin/env python3

# Simple network socket demo - CLIENT
#
# Set script as executable via: chmod +x client.py
# Run via:  ./client.py <IP> <PORT>
#
# To connect to a server on the same computer, <IP> could
# either be 127.0.0.1 or localhost (they have the same meaning)

#Port Number (use same one that client uses!)
#I used serverPort =  8765

import socket
#import socket module 

import sys
import os
import threading
import tkinter
import time
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askopenfilename
import argparse

# Basic global variables:
# Tip: You should use argparse - argv method
    # is sloppy and inflexible
parser = argparse.ArgumentParser(description='A chatroom application in which files and text can be sent accross a network.\nPlease enter your --target (ip address) --port (port # of the server) --username (your chatroom name)')
parser.add_argument('--version', action='version', version='%(prog)s 1.0', help='Gives you your current version of the client application')
parser.add_argument('--target', default='localhost', type=str, help='Give your ip address')   # defaults to local_host
parser.add_argument('--port', default=8765, type=int, help='Give the port # of the server to connect to')    # defaults to port# 8765
parser.add_argument('--username', required=True, help='Give a unique username you would like to be called by in the chatroom. Note: This is required.') # Required and has no default
args = parser.parse_args()

version = vars(args).get('version')
print(version)

ip = vars(args).get('target')
print(ip)

port = vars(args).get('port')
print(port)

username = vars(args).get('username')
print(username)


leaving = False # Variable that determines if the client is leaving or not. This helps it close its socket and alert the server.

foreign_msg = "" # Message recieved when being sent by someone else

my_socket = socket.socket() # This client's socket used for all of its connections

def JOIN_Protocol():
    str= f"CHAT/1.0 JOIN\r\nUsername: {username}\r\n\r\n"
    return str

def TXT_Protocol(len, text):
    str = f"CHAT/1.0 TEXT\r\nUsername: {username}\r\nMsg-len: {len}\r\n{text}\r\n\r\n"
    return str

def LEAVE_Protocol():
    str= f"CHAT/1.0 LEAVE\r\nUsername: {username}\r\n\r\n"
    return str


def handle_server_sends(protocol_str, my_Socket):
    global ip
    global port
    global leaving

    # Send message to server
    string_unicode = protocol_str
    raw_bytes = bytes(string_unicode,'ascii')

    if (leaving == True): # If you want to leave, close your socket to the server, and the server will notice and handle it.
        try:
            my_Socket.close()
        except socket.error as msg:
            print("Unable to close: " + str(msg))
    else:
        try:
            # Send the string
            # Note: send() might not send all the bytes!
            # You should loop, or use sendall()
            my_Socket.sendall(raw_bytes)
            print("Sent all bytes to server")
        except socket.error as msg:
            print("Error: send() failed")
            print("Description: " + str(msg))
            sys.exit()
# End of handle_server_sends()


def handle_server_recieves(my_socket):
    global ui
    while True:
        # Receive data
        try:
            buffer_size=1024
            raw_bytes = my_socket.recv(buffer_size)
        except socket.error as msg:
            print("Error: unable to recv()")
            print("Description: " + str(msg))
            sys.exit()

        print("Client is recieving data!\n")
        string_unsplit = raw_bytes.decode('ascii')
        print("Received %d bytes from client" % len(raw_bytes))
        print("Message contents:\n" + string_unsplit)

        string_unicode = raw_bytes.decode('ascii').split()

        if ( (string_unicode[1]) == "JOIN"):
            print("Recieved Request:\n'%s'.\nJoining you to my chat room!" % string_unicode)
            message = "" + str(string_unicode[3]) + " has entered the chat room."
            print("foreign msg: ", message)

            # Add this data to the message window
            ui.ui_messages.insert(tkinter.INSERT, "%s\n" % (message))
            ui.ui_messages.yview(tkinter.END)  # Auto-scrolling

        elif ( (string_unicode[1]) == "TEXT"):
            recieved_msg_place = 6 # 6 is the index for the start of the text being sent. The first 5 indicies are related to the message type and username and the 'Msg-len' header.
            recieved_msg = ""
            while recieved_msg_place < len(string_unicode):
                recieved_msg = recieved_msg + " " + string_unicode[recieved_msg_place]
                recieved_msg_place += 1

            message = str(string_unicode[3]) + f": {recieved_msg}"
            print("Adding you to my chat room message window!")
            print("foreign msg: ", message)

            # Add this data to the message window
            ui.ui_messages.insert(tkinter.INSERT, "%s\n" % (message)) # If it was your message. You can just print it.
            ui.ui_messages.yview(tkinter.END)  # Auto-scrolling

        elif ( (string_unicode[1]) == "LEAVE"):
            print("Recieved Request: '%s'. Taking you out of my chat room!" % string_unicode)
            message = str(string_unicode[3]) + " has left the chat room."
            # Inform other users that a user left the chat
            print("foreign msg: ", message)

            # Add this data to the message window
            ui.ui_messages.insert(tkinter.INSERT, "%s\n" % (message))
            ui.ui_messages.yview(tkinter.END)  # Auto-scrolling
# End handle_server_recieves()


# Function to run the UI
def UI():
    print("Running GUI Demo")

    # Instantiate class for UI
    global ui
    ui = clientUI()

    # Run the UI, and capture CTRL-C to terminate
    try:
        ui.start()
        return ui
    except KeyboardInterrupt:
        print("Caught CTRL-C, shutting down client")
        ui.eventDeleteDisplay()
    
    print("GUI Demo exiting")
# End of UI() function

# Start of clientUI Class
class clientUI():
    def __init__(self):
        self.first_click = True

    def start(self):
        print("Starting clientUI...")
        self.initDisplay()

        # Send the JOIN protocol to clients so that they know who is entering the chatroom
        str_protocol = JOIN_Protocol()
        handle_server_sends(str_protocol, my_socket)

        self.ui_messages.insert(tkinter.END, "Adding a message to the text field...\n")
        self.ui_input.insert(tkinter.END, "<Enter message>")

        # This call to mainloop() is blocking and will last for the lifetime
        # of the GUI.
        self.ui_top.mainloop()

        # Should only get here after destroy() is called on ui_top
        print("Stopping clientUI...")

        #SEND LEAVE msg through Client to Server.
        str_protocol = (str) ( LEAVE_Protocol() )
        handle_server_sends(str_protocol, my_socket)
        global leaving
        leaving = True

    def initDisplay(self):
        self.ui_top = tkinter.Tk()
        self.ui_top.wm_title("GUI Demo")
        self.ui_top.resizable('1','1')
        self.ui_top.protocol("WM_DELETE_WINDOW", self.eventDeleteDisplay)
        
        self.ui_messages = ScrolledText(
            master=self.ui_top,
            wrap=tkinter.WORD,
            width=50,  # In chars
            height=25)  # In chars     

        self.ui_input = tkinter.Text(
            master=self.ui_top,
            wrap=tkinter.WORD,
            width=50,
            height=4)
        
        # Bind the button-1 click of the Entry to the handler
        self.ui_input.bind('<Button-1>', self.eventInputClick)
        
        self.ui_button_send = tkinter.Button(
            master=self.ui_top,
            text="Send",
            command=self.sendMsg)

        self.ui_button_file = tkinter.Button(
            master=self.ui_top,
            text="File",
            command=self.sendFile)


        # Compute display position for all objects
        self.ui_messages.pack(side=tkinter.TOP, fill=tkinter.BOTH)
        #self.ui_messages.insert(tkinter.INSERT, "%s\n" % ("alice has entered the chatroom")) # Join message
        self.ui_input.pack(side=tkinter.TOP, fill=tkinter.BOTH)
        self.ui_button_send.pack(side=tkinter.LEFT)
        self.ui_button_file.pack(side=tkinter.RIGHT)


    # SEND button pressed
    def sendMsg(self):

        # Get user input (minus newline character at end)
        msg = self.ui_input.get("0.0", tkinter.END+"-1c")

        print("UI: Got text: '%s'" % msg) # If it was your message. You can just print it.

        # Add this data to the message window
        self.ui_messages.insert(tkinter.INSERT, "%s\n" % (msg)) # If it was your message. You can just print it.
        self.ui_messages.yview(tkinter.END)  # Auto-scrolling

        
        #SEND msg through Client to Server.
        str_protocol = (str) ( TXT_Protocol(len=sys.getsizeof(msg), text=msg) )
        handle_server_sends(str_protocol, my_socket)
        

        # Clean out input field for new data
        self.ui_input.delete("0.0", tkinter.END)


    # FILE button pressed
    def sendFile(self):
        file = askopenfilename()

        if(len(file) > 0 and os.path.isfile(file)):
            print("UI: Selected file: %s" % file)

            #SEND msg through Client to Server. This file_path openning and reading concept is from: https://www.geeksforgeeks.org/how-to-read-from-a-file-in-python/
            file_path = os.path.abspath(file)
            file_copy = open(file_path, "r")
            try:
                content = file_copy.read()
                str_protocol = (str) ( TXT_Protocol(len=sys.getsizeof(file), text=content) )
                file_copy.close()
                handle_server_sends(str_protocol, my_socket)
            except:
                content = "Sorry, I'm not able to read this file type at the moment. Please try simple types that are like .txt or simple programming files like .c."
                # Add this data to the message window
                self.ui_messages.insert(tkinter.INSERT, "%s\n" % (content)) # If it was your message. You can just print it.
                self.ui_messages.yview(tkinter.END)  # Auto-scrolling

                # Clean out input field for new data
                self.ui_input.delete("0.0", tkinter.END)
                

        else:
            print("UI: File operation canceled")

    # Event handler - User closed program via window manager or CTRL-C
    def eventDeleteDisplay(self):
        print("UI: Closing")

        # Continuing closing window now
        self.ui_top.destroy()

    # Event handler - User clicked inside the "ui_input" field
    def eventInputClick(self, event):
        if(self.first_click):
            # If this is the first time the user clicked,
            # clear out the tutorial message currently in the box.
            # Otherwise, ignore it.
            self.ui_input.delete("0.0", tkinter.END)
            self.first_click = False
# End of clientUI Class


def startUP():
    # Create my Client Socket and send data
    try:
        my_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print("Error: could not create socket")
        print("Description: " + str(msg))
        sys.exit()

    print("Connecting to server at " + ip + " on port ", str(port))
     
    # Connect to server
    try:
        my_Socket.connect((ip , port))
        return my_Socket
    except socket.error as msg:
        print("Error: Could not open connection")
        print("Description: " + str(msg))
        sys.exit()
    
    print("Connection established")
#End of StartUP()


def main():
    print("Running in main()...")
    global my_socket
    my_socket = startUP()
    threadUI = threading.Thread(target=UI)
    threadUI.start()
    thread_Recv = threading.Thread(target=handle_server_recieves, args=(my_socket,))
    thread_Recv.start()
    print("Exiting main()...")

if __name__ == "__main__":
    sys.exit(main())