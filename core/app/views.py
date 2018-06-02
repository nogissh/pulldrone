from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import datastructures

import ipaddress, json, socket, time
import numpy as np

from app.pypro import warai_decider #笑顔判定クラス
from app.pypro import tcptool


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
  return render(request, "app/index.html", content)


def toplay(request):

  """
  ドローン"""

  # moverangeの送り先
  try:
    ipaddress.ip_address(request.POST["dronecontroler_ip"])
    droneclient_ip = request.POST["dronecontroler_ip"]
  except ValueError:
    return HttpResponse("IPアドレスが不正です: dronecontroler")
  try:
    droneclient_port = int(request.POST["dronecontroler_port"])
  except ValueError:
    return HttpResponse("ポート番号には半角数字をいれてくださいs")

  # ドローンクライアントの情報
  droneclient = tcptool.DroneClient(
    droneclient_ip,
    droneclient_port,
  )

  #
  # フォームの情報
  #

  ## 制限時間
  try:
    timelimit = int(request.POST["timelimit"])
  except ValueError:
    return HttpResponse("制限時間には半角数字をいれてください")

  ## プレイヤーのIPアドレス
  try:
    ipaddress.ip_address(request.POST["player_1_ip"])
  except ValueError:
    return HttpResponse("IPアドレスが不正です: player_1")
  try:
    ipaddress.ip_address(request.POST["player_2_ip"])
  except ValueError:
    return HttpResponse("IPアドレスが不正です: player_2")

  #
  #### フォームの情報終わり

  """
  処理系"""

  # 多数決機械を用意（引数：IP Address）
  player_1 = warai_decider.WaraiDecider(request.POST["player_1_ip"])
  player_2 = warai_decider.WaraiDecider(request.POST["player_2_ip"])

  # TCPサーバの設定まわり
  host = '133.78.120.61'
  port = 8080
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  server.bind((host, port))
  server.listen(10)

  # ドローンを飛ばす
  droneclient.send('9999')

  # 差分施行をカウント
  count = 0

  #ゲームスタート
  starttime = time.time()
  while int(time.time()-starttime) < timelimit:

    # kinectからの接続を待つ
    print("Waiting for connections...")
    clientsock, address = server.accept()

    # 接続したkinectのIPアドレス
    print("connected:", address)

    # 座標
    coordinate = ""

    while True:

      try:
        # データを受け取る
        catch = clientsock.recv(2**12)

        # データをデコード
        catch = catch.decode()

        # 中身があれば結合する
        if catch != "":
          coordinate += catch
        
        # 返送（建前）
        resp = 'hoge'.encode()
        clientsock.sendall(resp)

      except OSError:
        # print("OSError, finished.")
        break

      except BrokenPipeError:
        # print("BrokenPipeError, finished.")
        break

    # 送信元を判別して入力情報を適切に代入
    try:
      if address[0] == player_1.playerAddress:
        tmp = np.array(list(map(np.float64, coordinate.split(","))))
        if len(tmp) != 240:
          continue #要素の数が240ではないときスキップ
        else:
          player_1.d_input = tmp
        player_1.waiting = True
      elif address[0] == player_2.playerAddress:
        tmp = np.array(list(map(np.float64, coordinate.split(","))))
        if len(tmp) != 240:
          continue #要素の数が240ではないときスキップ
        else:
          player_2.d_input = tmp
        player_2.waiting = True
      else:
        pass
    except ValueError:
      print('ValueError on Getting Facepoint')

    # 参加者全員の待機がTrueなら点数を計測する
    if player_1.waiting and player_2.waiting:

      # ドローンに送る情報を生成
      moverange = player_1.run() - player_2.run()
      moverange = str(moverange)

      # プレイヤーの待ち状態を変更
      player_1.waiting = False
      player_2.waiting = False

      # ドローンに移動命令
      count += 1
      print('moverange:', moverange)
      droneclient.send(moverange)

  """ 終了後処理 """
  droneclient.send('-9999')
  """ /終了後処理 """

  content = {
    "timelimit": str(timelimit),
    "player_1_ip": player_1.playerAddress,
    "player_2_ip": player_2.playerAddress,
    "dronecontroler_ip": droneclient_ip,
    "dronecontroler_port": droneclient_port,
    "battle_count": count,
    "player1_mochiten": player_1.mochiten,
    "player2_mochiten": player_2.mochiten,
  }
  del player_1, player_2 #クラスの削除
  return render(request, "app/finished.html", content)


def error(request):
  return HttpResponse("hogehoge")
