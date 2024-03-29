# ESP32でMicroPythonを用いて, 加速度センサと地磁気センサでGPSの取得条件を設ける

## 使用したもの
・ESP32
・LIS3DH 加速度センサ
・GY-271(QMC5883L) 地磁気センサ
・GT-902PMGG GPSモジュール

## プログラム
### LIS3DH.py
・加速度センサ LIS3DHからデータを取得することができる.
・加速度から停止を判定するために使う.(このコードは加速度の測定のみ)

### GY-271_QMC5883L.py & hmc5883l.py
・地磁気センサGY-271から地磁気のデータを取得する.
・QMC5883Lは地磁気のモジュール名で使用するにはhmc5883l.pyのモジュールのコードが必須である.
・地磁気から角度の算出が行える.

### GT-902PMGG_GPS.py
・GPSから緯度経度の位置情報を取得することができる.
・モジュールを使い, 位置測定を行うには電源Offの状態から約30秒必要なため注意が必要.

### QMC_LIS3DH.py
・加速度センサと地磁気センサから停止と曲がりの検出を行い, GPSを取得することができる.
・提案の評価実験に使用したコード.
