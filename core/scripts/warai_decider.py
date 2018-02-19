"""

笑度を算出するプログラム。
1台のkinectの座標データを受け取り、笑度をひとつ返す。

"""

import numpy as np


class WaraiDecider:

  def __init__(self):

    self.d_natural = self.read_csv("natural")
    self.d_fake = self.read_csv("fake")
    return None


  def read_csv(self, filename):

    datadir = "" #入力ファイルがある場所
    data = np.loadtxt("{}{}.csv".format(datadir, filename), delimiter=",")
    return data


  def majority(self, d_input, d_teacher):

    # 判定する

    value = np.sum(d_teacher[:, :-1] * d_input, axis=1)
    value += d_teacher[:, -1]
    if np.sum(value > 0) / len(value) >= 0.5:
      result = True
    else:
      result = False
    return result


  def dec_natural(self):

    # 自然な笑顔か判定 

    cp_input = np.copy(self.d_input)
    cp_natural = np.copy(self.d_natural)
    result = self.majority(cp_input, cp_natural)
    return result


  def dec_fake(self):

    # 愛想笑いかを判定

    cp_input = np.copy(self.d_input)
    cp_fake = np.copy(self.d_fake)
    result = self.majority(cp_input, cp_fake)
    return result


  def run(self, inputter):

    # 呼び出し部分
    # 入力は numpy 配列であること 

    self.d_input = inputter

    if self.dec_natural() == True:
      return 1.0 #笑顔

    if self.dec_fake() == True:
      return 0.5 #愛想笑い

    return 0.0 #その他


  def test(self):
    sample = self.read_csv("input")
    print(self.run(sample))

if __name__ == "__main__":

  t = WaraiDecider()
  t.test()
