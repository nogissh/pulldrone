import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(b"hogehoge", ("133.78.120.61", 8000))