"""

笑度を算出するプログラム。
1台のkinectの座標データを受け取り、笑度をひとつ返す。

"""
import numpy as np

from app.models import Fake, Natural


class WaraiDecider:

  def __init__(self, ip_address):

    self.playerAddress = ip_address           # プレイヤーのIPアドレス
    self.d_natural = None                     # 自然な笑顔のパラメータ
    self.d_fake = None                        # 愛想笑いのパラメータ
    self.d_input = ""                         # プレイヤーの顔座標データ
    self.waiting = False                      # 待機状態

    self.mochiten = 0                         # 持ち点

    self.set_default_params()


  def read_csv(self, filename):
    return np.loadtxt("pulldrone/data/{}.csv".format(filename), delimiter=",")


  def set_default_params(self):

    # DBから値を取得（自然な笑顔）
    tmp_natural = Natural.objects.all().values().latest('id')
    tmp_natural = tmp_natural['params'].split('\r\n')
    for i in range(len(tmp_natural)):
      tmp_natural[i] = list(map(np.float64, tmp_natural[i].split(',')))

    # DBから値を取得（愛想笑い）
    tmp_fake = Fake.objects.all().values().latest('id')
    tmp_fake = tmp_fake['params'].split('\r\n')
    for i in range(len(tmp_fake)):
      tmp_fake[i] = list(map(np.float64, tmp_fake[i].split(',')))

    # 代入
    self.d_natural = tmp_natural
    self.d_fake = tmp_fake


  def majority(self, d_input, d_teacher):

    # 判定する

    value = np.sum(d_teacher[:, :-1] * d_input, axis=1)
    value += d_teacher[:, -1]
    if np.sum(value > 0) / len(value) >= 0.5:
      return True
    else:
      return False


  def dec_natural(self):

    # 自然な笑顔か判定 

    cp_input = np.copy(self.d_input)
    cp_natural = np.copy(self.d_natural)
    return self.majority(cp_input, cp_natural)


  def dec_fake(self):

    # 愛想笑いかを判定
    cp_input = np.copy(self.d_input)
    cp_fake = np.copy(self.d_fake)
    return self.majority(cp_input, cp_fake)


  def run(self):

    # 呼び出し部分
    # 入力は numpy 配列であること 

    if self.dec_natural() == True:
      point = 1.0
      self.mochiten += point
      return point #笑顔

    if self.dec_fake() == True:
      point = 0.5
      self.mochiten += point
      return point #愛想笑い

    return 0.0 #その他


if __name__ == "__main__":
  t = WaraiDecider("133.78.81.152")
