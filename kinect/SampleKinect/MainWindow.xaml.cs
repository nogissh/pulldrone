using System;
using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using Microsoft.Kinect;
using Microsoft.Kinect.Toolkit;
using Microsoft.Kinect.Toolkit.FaceTracking;

namespace FaceTrackingSample
{

    /// <summary>
    /// MainWindow.xaml の相互作用ロジック
    /// </summary>
    public partial class MainWindow : Window
    {   //プログラムの動作状況を確認するための変数
        int finish = 0;

        //座標格納変数
        string zahyo = null;

        //基準点を求める処理に使う変数
        double BlockX = 0;
        double BlockY = 0;
        double testX = 0;
        double testY = 0;

        // 解像度・フレームレート
        private ColorImageFormat rgbFormat
            = ColorImageFormat.RgbResolution640x480Fps30;
        private const DepthImageFormat depthFormat
            = DepthImageFormat.Resolution320x240Fps30;

        // KinectSensorChooser
        private KinectSensorChooser kinectChooser = new KinectSensorChooser();

        // Kinectセンサーからの画像情報を受け取るバッファ
        private byte[] pixelBuffer = null;

        // Kinectセンサーからの深度情報を受け取るバッファ
        private short[] depthBuffer = null;

        // Kinectセンサーからの骨格情報を受け取るバッファ
        private Skeleton[] skeletonBuffer = null;

        // 画面に表示するビットマップ
        private RenderTargetBitmap bmpBuffer = null;

        // ビットマップへの描画用DrawingVisual
        private DrawingVisual drawVisual = new DrawingVisual();

        // FaceTrackerオブジェクト
        private FaceTracker faceTracker = null;

        //顔の傾き
        public float rotation_x, rotation_y, rotation_z;

        public MainWindow()
        {
            InitializeComponent();
        }

        // 初期化処理(Kinectセンサーやバッファ類の初期化)
        private void WindowLoaded(object sender, RoutedEventArgs e)
        {
            kinectChooser.KinectChanged += KinectChanged;
            kinectChooser.Start();
        }

        // 終了処理
        private void WindowClosed(object sender, EventArgs e)
        {
            kinectChooser.Stop();
        }

        // Kinectセンサーの挿抜イベントに対し、初期化/終了処理を呼び出す
        private void KinectChanged(object sender, KinectChangedEventArgs args)
        {
            if (args.OldSensor != null)
                UninitKinectSensor(args.OldSensor);

            if (args.NewSensor != null)
                InitKinectSensor(args.NewSensor);
        }

        // Kinectセンサーの初期化
        private void InitKinectSensor(KinectSensor kinect)
        {
            // ストリームの有効化
            ColorImageStream clrStream = kinect.ColorStream;
            clrStream.Enable(rgbFormat);
            DepthImageStream depthStream = kinect.DepthStream;
            depthStream.Enable(depthFormat);
            SkeletonStream skelStream = kinect.SkeletonStream;
            kinect.DepthStream.Range = DepthRange.Near;
            skelStream.EnableTrackingInNearRange = true;
            skelStream.TrackingMode = SkeletonTrackingMode.Seated;
            skelStream.Enable();

            // バッファの初期化
            pixelBuffer = new byte[clrStream.FramePixelDataLength];
            depthBuffer = new short[depthStream.FramePixelDataLength];
            skeletonBuffer = new Skeleton[skelStream.FrameSkeletonArrayLength];

            // 画面に表示するビットマップの初期化
            bmpBuffer = new RenderTargetBitmap(clrStream.FrameWidth,
                                               clrStream.FrameHeight,
                                               96, 96, PixelFormats.Default);
            rgbImage.Source = bmpBuffer;

            // イベントハンドラの登録
            kinect.AllFramesReady += AllFramesReady;

            faceTracker = new FaceTracker(kinect);
        }

        // Kinectセンサーの終了処理
        private void UninitKinectSensor(KinectSensor kinect)
        {
            if (faceTracker != null)
            {
                faceTracker.Dispose();
                faceTracker = null;
            }
            kinect.AllFramesReady -= AllFramesReady;
        }

        // FrameReady イベントのハンドラ
        // (Kinectセンサーの情報をもとにFaceTrackingを行い、
        //  認識した顔の各点に赤い点を描画)
        private void AllFramesReady(object sender, AllFramesReadyEventArgs e)
        {
            KinectSensor kinect = sender as KinectSensor;

            using (ColorImageFrame colorImageFrame = e.OpenColorImageFrame())
            using (DepthImageFrame depthImageFrame = e.OpenDepthImageFrame())
            using (SkeletonFrame skeletonFrame = e.OpenSkeletonFrame())
            {
                if (colorImageFrame == null || depthImageFrame == null
                    || skeletonFrame == null)
                    return;

                // 顔の各点の座標を保持するバッファ
                EnumIndexableCollection<FeaturePoint, PointF> facePoints = null;

                colorImageFrame.CopyPixelDataTo(pixelBuffer);
                depthImageFrame.CopyPixelDataTo(depthBuffer);
                skeletonFrame.CopySkeletonDataTo(skeletonBuffer);

                foreach (Skeleton skeleton in skeletonBuffer)
                {
                    // トラックできている骨格だけを対象とする
                    if (skeleton.TrackingState == SkeletonTrackingState.Tracked)
                    {
                        // 今回のフレームにFaceTrackingを適用
                        FaceTrackFrame frame
                            = faceTracker.Track(rgbFormat, pixelBuffer,
                                                depthFormat, depthBuffer,
                                                skeleton);

                        // FaceTrackingが成功したら顔の各点を取得
                        if (frame.TrackSuccessful)
                        {
                            //＊＊＊＊＊＊＊＊＊＊＊＊＊
                            finish++;
                            //＊＊＊＊＊＊＊＊＊＊＊＊＊
                            //撮影のたびにカウントをリセット
                            rotation_x = frame.Rotation.X;
                            rotation_y = frame.Rotation.Y;
                            rotation_z = frame.Rotation.Z;
                            facePoints = frame.GetProjected3DShape();
                            break;
                        }
                    }
                }

                // 描画の準備
                var drawContext = drawVisual.RenderOpen();
                int frmWidth = colorImageFrame.Width;
                int frmHeight = colorImageFrame.Height;

                // カメラの画像情報から背景のビットマップを作成し描画
                var bgImg = new WriteableBitmap(frmWidth, frmHeight, 96, 96,
                                                PixelFormats.Bgr32, null);
                bgImg.WritePixels(new Int32Rect(0, 0, frmWidth, frmHeight),
                                                pixelBuffer, frmWidth * 4, 0);
                var rect = new System.Windows.Rect(0, 0, frmWidth, frmHeight);
                drawContext.DrawImage(bgImg, rect);


                if (facePoints != null)
                {

                    // 基準点を再取得するため
                    int i = 0;

                    // 取得した顔の各点に赤い点を描画
                    foreach (var facePt in facePoints)
                    {
                        var pt = new System.Windows.Point(facePt.X, facePt.Y);

                        //座標の基準点を求める処理
                        if (i == 0)
                        {
                            BlockX = facePt.X;
                            BlockY = facePt.Y;
                        }
                        testX = facePt.X - BlockX;
                        testY = facePt.Y - BlockY;

                        if (i >= 1)
                        {
                            zahyo += testX.ToString();
                            zahyo += (",");
                            zahyo += testY.ToString();
                            zahyo += (",");
                        }
                        i++;
                    }
                    //末尾のカンマを削除
                    zahyo = zahyo.Trim(',');

                    //TCP通信
                    //サーバーのIPアドレス（または、ホスト名）とポート番号
                    string ipaddress = "133.78.120.61";
                    int port = 9000;

                    //TcpClientを作成し、サーバーと接続する
                    System.Net.Sockets.TcpClient tcp =
                        new System.Net.Sockets.TcpClient(ipaddress, port);

                    //NetworkStreamを取得する
                    System.Net.Sockets.NetworkStream ns = tcp.GetStream();

                    // スリープ
                    System.Threading.Thread.Sleep(1000);

                    //データを送信する
                    System.Text.Encoding enc = System.Text.Encoding.UTF8;
                    byte[] sendBytes = enc.GetBytes(zahyo);
                    ns.Write(sendBytes, 0, sendBytes.Length);
                    Console.WriteLine("座標を送信しました");

                    //サーバーから送られたデータを受信する
                    System.IO.MemoryStream ms = new System.IO.MemoryStream();
                    byte[] resBytes = new byte[1024];
                    int resSize = 0;

                    // メモリをバッファに蓄積
                    ms.Write(resBytes, 0, resSize);

                    //受信したデータを文字列に変換
                    string resMsg = enc.GetString(ms.GetBuffer(), 0, (int)ms.Length);

                    ms.Close();
                    Console.WriteLine("切断しました。");
                }
                //座標初期化
                zahyo = null;

                // 画面に表示するビットマップに描画
                // bmpBuffer.Render(drawVisual);

            }
        }
    }
}