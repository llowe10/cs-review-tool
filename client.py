# tutorial: https://codesource.io/creating-python-socket-server-with-multiple-clients/
# chat room project: https://github.com/IamLucif3r/Chat-On

import socket

HOST = '127.0.0.1'
PORT = 1891

def start_client(HOST, PORT):
    client = socket.socket()
    print("Waiting for connection...")

    try:
        client.connect((HOST, PORT))
    except socket.error as e:
        print(str(e))

    # prompt player for username
    username = input("Enter username: ")
    client.send(str.encode(username))

    # connection successful
    response = client.recv(2048).decode('utf-8')
    print(response)

    while True:
        message = input("Your message: ")
        client.send(str.encode(message))
        
        response = client.recv(2048)
        print(response.decode('utf-8'))
        if not response.decode('utf-8'):
            break

    client.close()

if __name__ == "__main__":
    start_client(HOST, PORT)