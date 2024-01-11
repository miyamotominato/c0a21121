import utime
import time
import urequests
import ujson
import utime
import machine
import math
import sys
import os
from machine import Pin, UART, I2C, Pin
from array import array
from hmc5883l import HMC5883L
from utime import sleep

#im



### パラメータ
SDA_PIN = 21
SCL_PIN = 22
LED_PIN = 23
CALIBRATION_TIME = 10 #[s]
###

count_gps = 0
lis_Y = 0
count_Y_stop = 0
lis_X = 0
count_X_stop = 0
lis_Z = 0
count_Z_stop = 0
LIS_count = 0

def check_LIS(out_x, out_y, out_z):
    global lis_X, lis_Y, lis_Z, count_X_stop, count_Y_stop, count_Z_stop, count_gps, LIS_count
    LisX = 0.05
    LisY = 0.05
    if (lis_X + LisX) < out_x or (lis_X - LisX) > out_x:
        #LisX = 0.05
        lis_X = out_x
        count_X_stop = 0
    elif count_X_stop == 15:
        #print("GPS__X")
        gps()
        LIS_count+=1
        count_Y_stop +=16
        #count_Z_stop +=16
        count_X_stop += 1
        count_gps += 1
    else:
        count_X_stop+=1
        #if count_X_stop == 5:
        #    LisX = 0.1
    
    if (lis_Y + LisY) < out_y or (lis_Y - LisY) > out_y:
        #LisY = 0.05
        lis_Y = out_y
        count_Y_stop = 0
    elif count_Y_stop == 15:
        #print("GPS__Y")
        gps()
        LIS_count+=1
        count_X_stop +=16
        #count_Z_stop +=16
        count_Y_stop += 1
        count_gps += 1
    else:
        count_Y_stop+=1
        #if count_Y_stop == 5:
        #    LisY = 0.1

#-------------------------------------------------------------------------
#GPS

URTN = 1
BPS = 9600

#RXPIN = 3 #RX3
#TXPIN = 1 #TX1

RXPIN = 16 #RX2
TXPIN = 17 #TX2
count = 0
check = 0
GPS_count = 0
p3 = Pin(3,Pin.IN,Pin.PULL_UP)
#p1 = Pin(1,Pin.IN,Pin.PULL_UP)
uart = UART(URTN,BPS)
uart.init(9600, bits=8, parity=None, stop=1, tx=TXPIN, rx=RXPIN)


def gps():
    URTN = 1
    BPS = 9600

    #RXPIN = 3 #RX1
    #TXPIN = 1 #TX1

    RXPIN = 16 #RX2
    TXPIN = 17 #TX2
    count = 0
    check = 0
    GPS_count = 0
    p3 = Pin(3,Pin.IN,Pin.PULL_UP)
    #p1 = Pin(1,Pin.IN,Pin.PULL_UP)
    uart = UART(URTN,BPS)
    uart.init(9600, bits=8, parity=None, stop=1, tx=TXPIN, rx=RXPIN)

    count = 0
    #global GPS_count

    while True:
        #sleep(0.1)
        check_num = 0
        num = uart.any()
        #print(num)
        if check == num:
            count+=1
        if count > 10 or num >= 240:
            check_num = check_GNGLL()
            #break
            if check_num == 1:
                #print("break")
                break
            else:
                #print("continue")
                count = 0
                check = 0
                continue
        elif check < num:
            check = int(num)
            count = 0
    
#stopcount = 0
    while(True):
        #sleep(0.1)
        sp = uart.readline()
        sp = str(sp)
        sp = sp.split(',')
        #print(sp)
        gps_latitude = list()

        try:
            if sp[0][3:8] == 'GNGLL':
                #print(sp)
                
                count = 1
                while count <= 2:
                    if count == 1:
                        #print(sp[count])
                        logger_latitude = float(sp[count])
                        decimal, integer = math.modf(logger_latitude/100.0)
                        gps_latitude.append(integer + decimal / 60.0 * 100.0)
                    
                    else:
                        #print(sp[count])
                        count = 3
                        logger_latitude = float(sp[count])
                        decimal, integer = math.modf(logger_latitude/100.0)
                        gps_latitude.append(integer + decimal / 60.0 * 100.0)                
                    count += 1

                print('gps_latitude : ', gps_latitude[0] , ' , ' , gps_latitude[1])
                #g = open('GPS_1226_1.txt', 'w')
                g.write(str(GPS_count)+","+ str(time_data)+ "," + str(gps_latitude[0]) +','+ str(gps_latitude[1]) + "\n")
                #g.close()
                GPS_count+=1
                #PS_count+=1
                
                break

            elif sp[0][:4] == 'None':
                #print("None, GNGLL_None")
                continue
        except Exception:
            print("GNGLLの値取得失敗")
            continue

#GPSから値が取得できているかの判定
def check_GNGLL():
   while(True):
    try:
        sp = uart.readline()
        sp = str(sp)
        sp = sp.split(',')
        #print(sp)
        gps_latitude = list()
    
        if sp[0][3:8] == 'GNGLL':
            #print("check")
            #print(sp)
            count = 1
            while count <= 2:
                try:
                    if count == 1:
                        #print(sp[count])
                        logger_latitude = float(sp[count])
                        decimal, integer = math.modf(logger_latitude/100.0)
                        gps_latitude.append(integer + decimal / 60.0 * 100.0)
                    
                    else:
                        #print(sp[count])
                        count = 3
                        logger_latitude = float(sp[count])
                        decimal, integer = math.modf(logger_latitude/100.0)
                        gps_latitude.append(integer + decimal / 60.0 * 100.0)
                except Exception:
                   #print("count1~2: GNGLL None-----")
                   return 0
                if count <=2:
                    return 1            
        elif sp[0][:4] == 'None':
            #print("None, GNGLL_None")
            continue
    except Exception:
       #print("GNGLLの値取得失敗-----")
       return 0
#-----------------------------------------------------------------------------
# 地磁気センサ用クラス
    
class QMC:
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

#-------------------------------------------------------------------------
        

#def main():
n = 0
count = 0
angle_num = 0
angle_count = 0
stop_count = 0
cell_count = 1
global qmc,led
print("START")
led = Pin(LED_PIN,Pin.OUT)
p21 = Pin(SDA_PIN,Pin.IN,Pin.PULL_UP)
p22 = Pin(SCL_PIN,Pin.IN,Pin.PULL_UP)
i2c = I2C(scl=Pin(SCL_PIN),sda=Pin(SDA_PIN), freq=100000) 
#通信できない場合クロック数を1万(1kHz)に変更



#LIS3DH 
address = 0x18
i2c.writeto_mem(address, 0x20, bytes([0x57]))
start_time_ms = utime.ticks_ms()

qmc = QMC(i2c,CALIBRATION_TIME)



l = open('LIS3DH_0109_2_echigoya.txt', 'w')
l.write("time,out_x,out_y,count_x,count_y,LIS_GPS,QMC_x,QMC_y,QMC_angle, QMC_GPS,\n")
#q = open('QMC5883l_1226_1.txt', 'w')
#q.write("QMC_x,QMC_y,QMC_angle, QMC_GPS\n")
g = open('GPS_0109_2_echigoya.txt', 'w')

while(True):
    #現在の時間を取得
    try:
        current_time_ms = utime.ticks_ms()

        #最初のデータを取り始めた時間からの経過時間を計算
        time_data = (current_time_ms - start_time_ms) / 1000
        
        #データ読み込み
        #地磁気
        angle_float, x, y= qmc.qmc_get_angle()

        if(n == 0):
            n += 1
            angle1 = angle_float
            continue
        else:
            angle_change = normalize_angle(angle_float - angle1) # 角度の変化
        angle1 = angle_float

        angle_num = angle_num + angle_change
        if(angle_num > 80 or angle_num < -80): #角度の判定
            #print("gps open Qmc")
            gps()
            angle_num =0 #- 30
            angle_count += 1


        
        i2c = I2C(scl=Pin(22), sda=Pin(21), freq=100000) 
        address = 0x18
        #i2c.writeto_mem(address, 0x20, bytes([0x57]))

        #データ読み込み(LIS3DH)
    
        xl = i2c.readfrom_mem(address, 0x28, 1)[0]
        xh = i2c.readfrom_mem(address, 0x29, 1)[0]
        yl = i2c.readfrom_mem(address, 0x2A, 1)[0]
        yh = i2c.readfrom_mem(address, 0x2B, 1)[0]
        zl = i2c.readfrom_mem(address, 0x2C, 1)[0]
        zh = i2c.readfrom_mem(address, 0x2D, 1)[0]
    
        #データ変換
        out_x = (xh << 8 | xl) >> 4
        out_y = (yh << 8 | yl) >> 4
        out_z = (zh << 8 | zl) >> 4
        #極性判断
        if out_x >= 2048:
            out_x -= 4096
        if out_y >= 2048:
            out_y -= 4096
        if out_z >= 2048:
            out_z -= 4096
        #物理量（加速度）に変換
        out_x = out_x / 1024
        out_y = out_y / 1024
        out_z = out_z / 1024
    except Exception:
        print("LIS err")
        continue

    #加速度の移動・停止判定

    check_LIS(out_x, out_y, out_z)
    print(time_data, count_X_stop, count_Y_stop, angle_num, "   LIS:",LIS_count, "   QMC:",angle_count)


    #ファイルへの書き込み
    l.write(str(count)+","+str(time_data)+","+str(out_x)+","+str(out_y)+","+str(count_X_stop)+","+str(count_Y_stop)+","+str(LIS_count)+","+str(x)+","+str(y)+","+str(angle_num)+","+str(angle_count)+"\n")
    time.sleep(0.05)
    count+=1
 


    if time_data > 270 or LIS_count > 8:
        l.close()
        g.close()
        break


#if __name__ == "__main__":
#    main()