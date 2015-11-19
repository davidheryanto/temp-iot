from __future__ import print_function
import socket
import binascii

if __name__ == '__main__':
    host = ''
    port = 5000
    backlog = 5
    size = 4096
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(backlog)

    client, address = s.accept()
    print('Connected to {}'.format(address))
    count = 0
    while 1:
        data = client.recv(size)
        count += 1
        print('Message #{}'.format(count))
        print(str(binascii.b2a_qp(data)))
    client.close()
