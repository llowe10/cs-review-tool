# https://codesource.io/creating-python-socket-server-with-multiple-clients/

import socket
from _thread import *

HOST = '127.0.0.1'
PORT = 1891
THREAD_COUNT = 0

def client_handler(connection):
    connection.sendall(str.encode("You are now connected to the server... Type BYE to stop"))

    while True:
        data = connection.recv(2048)
        message = data.decode('utf-8')
        if message == "BYE":
            break
        reply = f'Server: {message}'
        connection.sendall(str.encode(reply))
    
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