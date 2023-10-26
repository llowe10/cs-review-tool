# https://codesource.io/creating-python-socket-server-with-multiple-clients/

import socket

HOST = '127.0.0.1'
PORT = 1891

if __name__ == "__main__":
    client = socket.socket()
    print("Waiting for connection...")

    try:
        client.connect((HOST, PORT))
    except socket.error as e:
        print(str(e))
    
    response = client.recv(2048)
    while True:
        message = input("Your message: ")
        client.send(str.encode(message))
        
        response = client.recv(2048)
        print(response.decode('utf-8'))
        if not response.decode('utf-8'):
            break
    
    client.close()