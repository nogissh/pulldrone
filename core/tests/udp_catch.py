import sys, time
import socket
import numpy as np

import warai_decider #笑顔判定クラス


timelimit = 1000 #制限時間

# プレイヤーのIPアドレス
player_1_ip = "133.78.81.152" #大野木
player_2_ip = "133.78.82.7"   #松村

# 多数決機械を用意（引数：IP Address）
player_1 = warai_decider.WaraiDecider(player_1_ip)
player_2 = warai_decider.WaraiDecider(player_2_ip)

# ソケットを用意（受信のみ）
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", 8080))
s.setblocking(0)

# UDP受信のための変数を初期化
data = ""
address = ""

#ゲームスタート
starttime = time.time()
while True:

  if (time.time() - starttime) > timelimit:
    break #タイムアップ

  try:
    data, address = s.recvfrom(4096) #常にUDP着信を監視
    
  except socket.error:
    pass

  else:

    # 送信元を判別して入力情報を適切に代入
    if address[0] == player_1.playerAddress:
      data = data.decode().split(",")
      player_1.d_input = np.array(list(map(float, data)))
      player_1.waiting = True

    if address[0] == player_2.playerAddress:
      data = data.decode().split(",")
      player_2.d_input = np.array(list(map(float, data)))
      player_2.waiting = True

    # 参加者全員の待機がTrueなら点数を計測する
    if player_1.waiting and player_2.waiting:

      try:
        moverange = player_1.run() - player_2.run()
        player_1.waiting = False
        player_2.waiting = False

        # ドローン移動命令
        # /ドローン移動命令

      except ValueError:
        pass


# 終了後処理

# /終了後処理

print("finished")