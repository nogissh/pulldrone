import sys, time
import socket
import numpy as np

import warai_decider #笑顔判定クラス


#
player_1_ip = "133.78.81.152"
player_2_ip = "133:78.81.***"

# 多数決機械を用意（引数：IP Address）
player_1 = warai_decider.WaraiDecider(player_1_ip)
player_2 = warai_decider.WaraiDecider(player_2_ip)

# ソケットを用意（受信のみ）
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", 8000))
s.setblocking(0)

# UDP受信のための変数を初期化
data = ""
address = ""

# 待ち
while True:

  try:
    data, address = s.recvfrom(4096) #常にUDP着信を監視
    
  except socket.error:
    pass

  else:

    # 送信元を判別して入力情報を適切に代入
    if address == player_1.playerAddress:
      player_1.d_input = data.decode()
      player_1.d_input = np.array(player_1.d_input.split(","))
    elif address == player_2.playerAddress:
      player_2.d_input = data
      player_2.d_input = np.array(player_2.d_input.split(","))

    # 参加者全員の入力がTrueなら点数を計測する
    if (player_1.d_input) and (player_1.d_input != ""):

      try:
        print(player_1.run())
        player_1.d_input = ""

      except ValueError:
        pass

    print("rcbd: ", data.decode())