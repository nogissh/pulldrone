import sys, time
import socket

import numpy as np



# プレイヤーのIPアドレス
player_1_ip = "133.78.81.152"
player_2_ip = "133:78.82.7"

# ソケットを用意（受信のみ）
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", 8080))
s.setblocking(0)

# UDP受信のための変数を初期化
data = ""
address = ""

blank = ""

while True:


  try:
    data, address = s.recvfrom(4096) #常にUDP着信を監視
    
  except socket.error:
    pass

  else:

    data = data.decode()
    #print("data: ", data)

    data = data.split(",")
    #print(data)

    try:
      data = list(map(float, data))
      print(data)
    except ValueError:
      continue

    data = np.array(data)
    print(data.shape)

    if data.shape[0] == 240:
      print("good luck")
      break

    blank = blank + ">"
    print(blank)
