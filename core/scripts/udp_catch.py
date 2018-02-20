import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", 8000))
s.setblocking(0)

data = ""
address = ""

while True:

  try:
    data, address = s.recvfrom(4096)
    
  except socket.error:
    pass

  else:
    print("rcbd: ", data)