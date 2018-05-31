import socket, time


class DroneClient:

  latest_recv = ""

  def __init__(self, host, port):
    self.host = host
    self.port = port

  def send(self, content):

    # ソケットを用意（逐次）
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # ドローンクライアントと接続
    try:
      client.connect((self.host, self.port))
    except ConnectionRefusedError:
      return False

    # 送信
    client.send(content.encode())

    # レスポンスを受け取る
    try:
      self.latest_rect = client.recv(1024)
    except ConnectionResetError:
      return False
