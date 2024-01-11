from machine import I2C,Pin
from array import array
from hmc5883l import HMC5883L
import time
import utime
import sys
import math
#im



### パラメータ
SDA_PIN = 21
SCL_PIN = 22
LED_PIN = 23
CALIBRATION_TIME = 10 #[s]
###


class QMC:
    # 地磁気センサ用クラス
    def __init__(self,i2c,calibration_time):
        # 地磁気センサ初期化
        self.i2c = i2c
        self.qmc_sensor = HMC5883L(i2c , declination=(0, 0))
        
        self.mid = [0,0]
        self.qmc_calibration(calibration_time)

    def qmc_calibration(self,calibration_time):
        # 地磁気センサのキャリブレーション
        led = Pin(23,Pin.OUT)
        x, y, z = self.qmc_sensor.read()
        x_list = [x,x]
        y_list = [y,y]
        # cnt = 200
        cnt = 20 * calibration_time
        while True:
            time.sleep(0.05)
            x, y, z = self.qmc_sensor.read()
            if(x < x_list[0]):
                x_list[0] = x
            if(x > x_list[1]):
                x_list[1] = x
            if(y < y_list[0]):
                y_list[0] = y
            if(y > y_list[1]):
                y_list[1] = y
            
            x_mid = (x_list[0] + x_list[1]) / 2
            y_mid = (y_list[0] + y_list[1]) / 2

            x = x - x_mid
            y = y - y_mid

            print('calibration {} {:.0f}<x<{:.0f} , {:.0f}<y<{:.0f}'.format(cnt,x_list[0],x_list[1],y_list[0],y_list[1]))
            cnt-=1
            if(cnt%3==0):
                led.value(led.value())
            if(cnt == 0):
                print("calibration_end")
                print('xmid:{} ymid:{}'.format(x_mid,y_mid))
                self.mid = [x_mid,y_mid]
                print("sleep 5")
                time.sleep(5)
                return

    def qmc_get_angle(self):
        # 地磁気センサから角度を取得
        x, y, z = self.qmc_sensor.read()
        x = x - self.mid[0]
        y = y - self.mid[1]
        angle_taple = self.qmc_sensor.calc_deg(x , y)
        angle_str = str(angle_taple[0]) + "." + str(angle_taple[1])
        angle_float = float(angle_str)
        return(angle_float, x, y)
    
def normalize_angle(angle):
# 角度を-180から180の範囲に正規化する
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    return angle
        

def main():

    
    angle_count = 0
    angle_num = 0
    stop_count = 0
    global qmc,led
    print("START")
    led = Pin(LED_PIN,Pin.OUT)
    p21 = Pin(SDA_PIN,Pin.IN,Pin.PULL_UP)
    p22 = Pin(SCL_PIN,Pin.IN,Pin.PULL_UP)
    i2c = I2C(scl=Pin(SCL_PIN),sda=Pin(SDA_PIN), freq=100000) 


    qmc = QMC(i2c,CALIBRATION_TIME)
    n = 0
        
    while(True):
        #時間
        time_data = utime.ticks_ms() / 1000
        time.sleep(0.05)
        angle_float, x, y= qmc.qmc_get_angle()
        if(n == 0):
            n += 1
            angle1 = angle_float
            continue
        else:
            angle_change = normalize_angle(angle_float - angle1) # 角度の変化
        angle1 = angle_float

        angle_num = angle_num + angle_change
        if(angle_num > 45 or angle_num < -45):
            angle_num = 0
            angle_count += 1
            
        #if(angle_num < -45):
        #    angle_num +=45
        #    angle_count += 1

        print('xmid:{} ymid:{}'.format(x,y), "angle")
        print(angle_float, "::: ", angle_change, ":::", angle_num, ":::", angle_count)
    
   
if __name__ == "__main__":
    main()


#C:\Users\admin\Documents\ESP32-実験用