# Networked Tic-Tac-Toe Game with Python Sockets

This is a Tic-tac-toe game written in python version 3.8 and powered by python sockets. The application is separated into two different sections: client.py and server.py.

# client.py
This file manages everything that the client sees and interact with to communicate to the socket server. server.py: All clients must interact with the socket server which is created in this file. The file manages all the game board logic + encryption, and client to client interactions.

# server.py
server.py: This file contains all the actions that the client can send to the socket server. its responsible for storing and minipulate the data that is recieved from the server to the client.

# To get started

- Start the server
```
server.py
```
- Run the client twice
```
client.py
```
