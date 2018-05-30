var net = require('net');
var HOST = '133.78.83.160';
var PORT = 8000;

// モジュールの読み込み
const Drone = require('rolling-spider');  // rolling-spider モジュールを使う
const keypress = require('keypress');     // キーボード操作を取得する keypress モジュールを使う（rolling-spider と同時にインストールされる）

// 変数の設定
let ACTIVE = true;                        // ドローンがアクティブ状態か否か
const STEPS = 2;                          // 一度のキー操作で命令を出す回数（動かすステップ数、0-100）

// rolling-spider のインスタンスを作る
const d = new Drone();

function initDrone(){
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
}
initDrone()

// サーバーインスタンスを生成し、リッスンします
// net.createServer()に渡す関数は、'connection'イベントハンドラーになります。
// コールバック関数が受け取るsockeオブジェクトは各接続ごとにユニークなものとなります。
net.createServer(function(sock) {
    // TCPサーバーが接続しました。socketオブジェクトが自動的に割り当てられます。
    console.log('CONNECTED: ' + sock.remoteAddress +':'+ sock.remotePort);
    // 'data' イベントハンドラー
    
    sock.on('data', function(data) {
        console.log(data);
        data = Number(data);
        if(data == 9999){
            console.log("take off");
            d.takeOff();
        }
        else if(data == -1.0){
            console.log("-");
            d.tiltLeft({ steps: 10 });
        }
        else if(data == -0.5){
            console.log("-");
            d.tiltLeft({ steps: 5 });
        }
        else if(data == 0.5){
            console.log("+");
            d.tiltRight({ steps: 5});
        }
        else if(data == 1.0){
            console.log("-");
            d.tiltRight({ steps: 10 });
        }
        else if (data == -9999){
            d.land();
            console.log("land on");
        }
        else{
        }
        // ソケットに応答を書き込みます。クライアントはその書き込みを受信します。
        sock.write('RECIEVED');
    });
    // 'close'イベントハンドラー
    sock.on('close', function(had_error) {
        console.log('CLOSED. Had Error: ' + had_error);
    });
    // 'errer'イベントハンドラー
    sock.on('error', function(err) {
        console.log('ERROR: ' + err.stack);
    });
}).listen(PORT, HOST);
console.log('Server listening on ' + HOST +':'+ PORT);
