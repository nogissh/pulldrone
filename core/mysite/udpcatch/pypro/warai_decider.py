"""

笑度を算出するプログラム。
1台のkinectの座標データを受け取り、笑度をひとつ返す。

"""

import numpy as np


class WaraiDecider:

  def __init__(self, ip_address):

    self.playerAddress = ip_address           # プレイヤーのIPアドレス
    self.d_natural = self.read_csv("natural") # 自然な笑顔のパラメータ
    self.d_fake = self.read_csv("fake")       # 愛想笑いのパラメータ
    self.d_input = ""                         # プレイヤーの顔座標データ
    self.waiting = False                      # 待機状態
    return None


  def read_csv(self, filename):
    return np.loadtxt("udpcatch/data/{}.csv".format(filename), delimiter=",")


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
      return 1.0 #笑顔

    if self.dec_fake() == True:
      return 0.5 #愛想笑い

    return 0.0 #その他


if __name__ == "__main__":
  t = WaraiDecider("133.78.81.152")
