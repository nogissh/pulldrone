from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import datastructures

import ipaddress, json, socket, time
import numpy as np

from pulldrone.pypro import warai_decider #笑顔判定クラス


# Create your views here.
def index(request):

  content = {}
  try:
    content["timelimit"] = request.POST["timelimit"]
    content["player_1_ip"] = request.POST["player_1_ip"]
    content["player_2_ip"] = request.POST["player_2_ip"]
    content["dronecontroler_ip"] = request.POST["dronecontroler_ip"]
    content["dronecontroler_port"] = request.POST["dronecontroler_port"]
  except datastructures.MultiValueDictKeyError:
    pass
  return render(request, "pulldrone/index.html", content)


def toplay(request):

  # moverangeの送り先
  w_sendto = {}
  try:
    ipaddress.ip_address(request.POST["dronecontroler_ip"])
    w_sendto["ipaddress"] = request.POST["dronecontroler_ip"]
  except ValueError:
    return HttpResponse("IPアドレスが不正です: dronecontroler")
  try:
    w_sendto["port"] = int(request.POST["dronecontroler_port"])
  except ValueError:
    return HttpResponse("ポート番号には半角数字をいれてくださいs")


  # 制限時間
  try:
    timelimit = int(request.POST["timelimit"])
  except ValueError:
    return HttpResponse("制限時間には半角数字をいれてください")

  # プレイヤーのIPアドレス
  try:
    ipaddress.ip_address(request.POST["player_1_ip"])
  except ValueError:
    return HttpResponse("IPアドレスが不正です: player_1")
  try:
    ipaddress.ip_address(request.POST["player_2_ip"])
  except ValueError:
    return HttpResponse("IPアドレスが不正です: player_2")

  # 多数決機械を用意（引数：IP Address）
  player_1 = warai_decider.WaraiDecider(request.POST["player_1_ip"])
  player_2 = warai_decider.WaraiDecider(request.POST["player_2_ip"])

  # ソケットを用意（受信のみ, UDP）
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.bind(("", 8080))
  s.setblocking(0)

  # ソケットを用意（送信のみ、UDP）
  sSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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

          """ ドローン移動命令 """
          content = {

            "sentfrom": "133.78.120.61",
            "moverange": moverange,
          }
          content = json.dumps(content)
          sSend.sendto(content.encode(),
            (w_sendto["ipaddress"], w_sendto["port"]))
          """ /ドローン移動命令 """

        except ValueError:
          pass

  """ 終了後処理 """
  #send("finished") #終了時にドローンに送るメッセージ
  """ /終了後処理 """

  print(timelimit)
  content = {

    "timelimit": str(timelimit),
    "player_1_ip": player_1.playerAddress,
    "player_2_ip": player_2.playerAddress,
    "dronecontroler_ip": w_sendto["ipaddress"],
    "dronecontroler_port": w_sendto["port"],
  }
  del player_1, player_2 #クラスの削除
  return render(request, "pulldrone/finished.html", content)


def error(request):
  return HttpResponse("hogehoge")