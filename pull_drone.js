'use strict';                             // 厳格モードにする

// モジュールの読み込み
const Drone = require('rolling-spider');  // rolling-spider モジュールを使う
const keypress = require('keypress');     // キーボード操作を取得する keypress モジュールを使う（rolling-spider と同時にインストールされる）

// 変数の設定
let ACTIVE = true;                        // ドローンがアクティブ状態か否か
const STEPS = 2;                          // 一度のキー操作で命令を出す回数（動かすステップ数、0-100）

// rolling-spider のインスタンスを作る
const d = new Drone();
// ドローンの初期設定
d.connect( () => {                        // BLE でドローンに接続し、接続できたらコールバック
  d.setup( () => {                        // ドローンを初期設定してサービスや特徴を取得、その後コールバック
    d.flatTrim();                         // トリムをリセット
    d.startPing();                        // 不明
    d.flatTrim();                         // なぜ二回呼ぶのかは不明
    ACTIVE = true;                        // ドローンを ACTIVE 状態とする
    console.log(d.name, 'is ready!');     // 準備OKなことをコンソール出力
  });
});

//UDPソケット部分
var PORT = 8000;
var HOST = '133.78.120.61';

var dgram = require('dgram');
var server = dgram.createSocket('udp4');

server.on('listening', function () {
    var address = server.address();
    console.log('UDP Server listening on ' + address.address + ":" + address.port);
});

server.on('message', function (message, remote) {
    console.log(remote.address + ':' + remote.port +' - ' + message);

});

server.bind(PORT, HOST);


// キー操作でイベントを発生させる
keypress(process.stdin);                  // 標準入力に keypress イベントを発生させる
process.stdin.setRawMode(true);           // raw mode（修飾を伴わない）で標準入力を受け付ける
process.stdin.resume();                   // keypress イベントをリッスン

// キー操作後に少しのあいだ入力を受け付けないようにする関数
function cooldown() {
  ACTIVE = false;       // いったん ACTIVE 状態でなくしておいて
  setTimeout( () => {   // 一定時間後に
    ACTIVE = true;      // ACTIVE に戻す
  }, STEPS * 12);       // この例では 24 ms
}

// キーボードからの入力による操作
process.stdin.on('keypress', (ch, key) => {   // keypress イベントが発生したら
  if (ACTIVE && key) {                        // ドローンが ACTIVE で key があれば
    // 緊急停止
    if (key.name === 'm') {             // m キー
      d.emergency();                      // 緊急停止（モーターを即時停止）
      setTimeout( () => {                 // 3秒後にプログラム終了
        process.exit();
      }, 3000);

    // 離陸（t; take-off）
    } else if (key.name === 't') {      // t キー
      console.log('takeoff');             // コンソール出力
      d.takeOff();                        // 離陸

    // w/s/a/d キー（前後左右の移動）
    } else if (key.name === 'w') {      // w キー
      d.forward({ steps: STEPS });        // 前進（前ピッチ）
      cooldown();                         // 少しの間キー操作を受け付けない
    } else if (key.name === 's') {      // s キー
      d.backward({ steps: STEPS });       // 後退（後ピッチ）
      cooldown();                         // 少しの間キー操作を受け付けない
    } else if (key.name === 'a') {      // a キー
      d.tiltLeft({ steps: STEPS });       // 左水平移動（左ロール）
      cooldown();                         // 少しの間キー操作を受け付けない
    } else if (key.name === 'd') {      // d キー
      d.tiltRight({ steps: STEPS });      // 右水平移動（右ロール）
      cooldown();                         // 少しの間キー操作を受け付けない

    // カーソルキー（上下と左右スピン）ttt
    } else if (key.name === 'left') {   // 左カーソルキー
      d.turnLeft({ steps: STEPS });       // 左旋回（左スピン（ヨー））
      cooldown();                         // 少しの間キー操作を受け付けない
    } else if (key.name === 'right') {  // 右カーソルキー
      d.turnRight({ steps: STEPS });      // 右旋回（右スピン（ヨー））
      cooldown();                         // 少しの間キー操作を受け付けない
    } else if (key.name === 'up') {     // 上カーソルキー
      d.up({ steps: STEPS * 2.5 });       // 上昇
      cooldown();                         // 少しの間キー操作を受け付けない
    } else if (key.name === 'down') {   // 下カーソルキー
      d.down({ steps: STEPS * 2.5 });     // 下降
      cooldown();                         // 少しの間キー操作を受け付けない


    // 着陸（q; quit）
    } else if (key.name === 'q') {      // q キー
      console.log('landing...');          // コンソール出力
      d.land();                           // 着陸
    }
  }

  // プログラム終了（ctrl + c）
  if (key && key.ctrl && key.name === 'c') {  // ctrl + c なら
    process.stdin.pause();                    // 標準入力を一時停止
    process.exit();                           // プログラム終了
  }
});
