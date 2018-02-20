import socket

text = "I am Toshiki Ohnogi, studying at Tokyo City University."

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(text.encode(), ("133.78.120.61", 8000))