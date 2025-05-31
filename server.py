#!/usr/bin/env python3

# Simple network socket demo - SERVER
#
# Set script as executable via: chmod +x server.py
# Run via: ./server.py <PORT>

#Port Number (use same one that client uses!)
#I used serverPort =  8765

import socket
import sys
import threading
import argparse 

parser = argparse.ArgumentParser(description='A chatroom application server in which files and text can be sent.\nPlease enter your --port (server port #)')
parser.add_argument('--version', action='version', version='%(prog)s 1.0', help='Gives you your current version of the server application')
parser.add_argument('--port', default=8765, type=int, help='Give the port # of this server to recieve your clients')    # defaults to port# 8765
args = parser.parse_args()

version = vars(args).get('version')
print(version)

port = vars(args).get('port')
print(port)


# List of all the Clients in the Chatroom
clients = []
usernames = []

def add_client(client_socket):
    clients.append(client_socket)

def delete_client(client_socket):
    # Close client socket
    try:      
        index = clients.index(client_socket) # Take client out of server's list
        clients.pop(index)
        client_socket.close()  # Close that client's connection to the server

    except socket.error as msg:
        print("Error: unable to close() socket")
        print("Description: " + str(msg))

def Broadcast(message, sending_client):
    for client in clients:
        if client is not sending_client:
            client.sendall(message)
            print("Sending Message Back to Client")

def handle_client_comms(client_socket):
    while True:  
        # Receive data
        try:
            buffer_size=1024
            raw_bytes = client_socket.recv(buffer_size)
            Broadcast(raw_bytes, client_socket)
        except:
            clients.remove(client_socket)
            client_socket.close()

            # Send Leave Protocol String (when the client closes un-naturally) to Everyone who isn't the leaving client.
            Broadcast(raw_bytes, client_socket)
            break
    
    delete_client(client_socket) # Happens when the client's 'handle_server_sends' function closes a socket when naturally (not unexpectedly) leaving
#End of handle_client_comms()

            
def main():
    # Tip: You should use argparse - argv method
    # is sloppy and inflexible

    # Create TCP socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print("Error: could not create socket")
        print("Description: " + str(msg))
        sys.exit()

    # Bind to listening port
    try:
        host=''  # Bind to all interfaces
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of address for clients
        s.bind((host,port))
    except socket.error as msg:
        print("Error: unable to bind on port %d" % port)
        print("Description: " + str(msg))
        sys.exit()
    
    while(1):
        # Listen
        try:
            backlog=10  # Number of incoming connections that can wait
                        # to be accept()'ed before being turned away
            s.listen(backlog)
        except socket.error as msg:
            print("Error: unable to listen()")
            print("Description: " + str(msg))
            sys.exit()    

        print("Listening socket bound to port %d" % port)

        # Accept an incoming request
        try:
            (client_s, client_addr) = s.accept()
            # If successful, we now have TWO sockets
            #  (1) The original listening socket s, still active
            #  (2) The new socket client_s connected to the client
        except socket.error as msg:
            print("Error: unable to accept()")
            print("Description: " + str(msg))
            sys.exit()

            print("Accepted incoming connection from client")
            print("Client IP, Port = %s" % str(client_addr))
        
        if client_s not in clients:
            add_client(client_s)
            print("Here! Clients list has this many: ", len(clients))
        
        # Function broadcasting the message from the client socket to the other sockets in other threads
        threadBrodcast = threading.Thread(target=handle_client_comms, args=(client_s,))
        threadBrodcast.start()

if __name__ == "__main__":
    sys.exit(main())
