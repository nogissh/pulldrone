"""

笑度を算出するプログラム。
1台のkinectの座標データを受け取り、笑度をひとつ返す。

"""

import csv

import numpy as np
import matplotlib.pyplot as plt


class WaraiDecider:

  def __init__(self):

    self.d_input = np.array([])

    self.d_natural = self.read_csv("natural")
    self.d_fake = self.read_csv("fake")
    return None


  def read_csv(self, filename):

    datadir = "" #入力ファイルがある場所
    data = np.loadtxt("{}{}.csv".format(datadir, filename), delimiter=",")
    return data


  def majority(self, d_input, d_teacher):

    # 判定する

    value = np.sum(d_teacher[:, :-1] * d_input[:-1], axis=1)
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


if __name__ == "__main__":

  t = WaraiDecider()
