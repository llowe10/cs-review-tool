# tutorial: https://codesource.io/creating-python-socket-server-with-multiple-clients/
# chat room project: https://github.com/IamLucif3r/Chat-On

import socket
from _thread import *
import random

HOST = '127.0.0.1'
PORT = 1891

clients = []
usernames = []
topics = []
sessions = {} # {id: topic}

def join_game(connection):
    id = None

    # list all available game session IDs and topics
    avail_sess = ""
    for id in sessions:
        avail_sess += (str(id) + " -- " + sessions[id] + "\n")
    connection.sendall(str.encode(f'Available games:\n{avail_sess}'))

    # capture game session ID from client
    while True:
        id = int(connection.recv(2048).decode('utf-8'))
        if id not in sessions:
            connection.sendall(str.encode(f'Game {id} does not exist.\n'))
        else:
            break
    
    connection.sendall(str.encode(f'Joining game {id}...\n'))

def create_game(connection):
    id = None
    topic = None

    # TODO: get available topics from database
    topics.append('TBD')

    # list available game topics to client
    avail_top = ""
    for top in topics:
        avail_top += (top + "\n")
    connection.sendall(str.encode(f'Available topics:\n{avail_top}'))

    # capture game topic from client
    while True:
        topic = connection.recv(2048).decode('utf-8')
        if topic not in topics:
            connection.sendall(str.encode(f'Topic \'{topic}\' does not exist.\n'))
        else:
            break

    # randomly generate session ID
    while True:
        id = random.randint(1000, 9999)
        if id not in sessions:
            sessions[id] = topic
            break
    
    connection.sendall(str.encode(f'New game created! Session ID: {id}\n'))

def client_handler(connection):
    # get player username
    while True:
        username = connection.recv(2048).decode('utf-8')

        if username not in usernames:
            connection.sendall(str.encode(f'Welcome to CS Review Tool, {username}!\n'))
            clients.append(connection)
            usernames.append(username)
            break
        else:
            connection.sendall(str.encode(f'User {username} already exists.'))
    
    # determine if player wants to create game or join game
    choice = connection.recv(2048).decode('utf-8')
    if choice == 'C':
        create_game(connection)
    else:
        join_game(connection)
    
    connection.close()

def accept_connections(ss):
    client, address = ss.accept()
    print("Connected to: " + address[0] + ":" + str(address[1]))
    start_new_thread(client_handler, (client, ))

def start_server(HOST, PORT):
    ss = socket.socket()
    try:
        ss.bind((HOST, PORT))
    except socket.error as e:
        print(str(e))
    
    print(f'Server is listening on port {PORT}...')
    ss.listen()

    while True:
        accept_connections(ss)

if __name__ == "__main__":
    start_server(HOST, PORT)