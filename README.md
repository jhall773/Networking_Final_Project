# Networking_Final_Project
Final project for computer networking course: A Chatroom Client-Server application with a special message type (similar to https Get and Receive) using python.

1. First, please download the files for both the server and the clients.
2. Second, run the server file first, and then the client files (running the server and every client each in their own individual terminal windows) from the command line using the command line arguments. Please see the "Terminal Commands to Run.txt" file for more information about running the application from the terminal.

Alternatively, you may download the App_Example_Run folder and open (double-click) the Bat (.bat) file to see an example of the Application run without running any program (python) scripts. An example of what you should see when using the application from the Bat file (and similarly if running the python scripts in the command line from the terminals) is shown in the Example_Image.

# For Example: 
The server may be ran with an optional port number argument (though the port number will be assumed as port 8675) on the command line and a run of the file may be written as follows: "python3 server.py --port 8675"

The client may be ran with a target IP address argument (the default is localhost), may be ran with port # argument, and must be ran with a username argument on the command line and a run of the file may be written as follows: "python3 client.py --target 192.168.1.229 --port 8675 --username Max"


