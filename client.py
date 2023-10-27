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
    while True:
        username = input("Enter username: ")
        client.send(str.encode(username))
        response = client.recv(2048).decode('utf-8')
        print(response)

        if response.startswith('Welcome'):
            break

    # prompt player to create or join game
    print("Do you want to create or join a game?")
    while True:
        choice = input("Enter C to create or J to join: ")
        if choice == 'C' or choice == 'J':
            client.send(str.encode(choice))
            print(client.recv(2048).decode('utf-8'))
            break
        else:
            print("Invalid input.\n")

    client.close()

if __name__ == "__main__":
    start_client(HOST, PORT)