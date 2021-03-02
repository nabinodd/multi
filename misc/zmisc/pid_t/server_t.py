import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


server_address = ('0.0.0.0', 1200)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

dataz=b'\x05'

while True:
    print('\nwaiting to receive message')
    data, address = sock.recvfrom(4096)

    print('received {} bytes from {}'.format(len(data), address))
    print(data)
    if data:
        sent = sock.sendto(dataz, address)
        print('sent {} bytes back to {}'.format(sent, address))