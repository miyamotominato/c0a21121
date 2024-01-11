
import math
import urequests
import ujson
import utime
import machine
import time
from machine import UART, Pin
from utime import sleep



URTN = 1
BPS = 9600

RXPIN = 16 #RX2
TXPIN = 17 #TX2
count = 0
check = 0
GPS_count = 0
p3 = Pin(3,Pin.IN,Pin.PULL_UP)
uart = UART(URTN,BPS)
uart.init(9600, bits=8, parity=None, stop=1, tx=TXPIN, rx=RXPIN)

while True:
  num = uart.any()
  print(num)
  if check == num:
    count+=1
    if count > 10 or check >= 240:
       break
  elif check < num:
    check = int(num)
    count = 0
  time.sleep(0.1)

while(True):
    sp = uart.readline()
    sp = str(sp)
    sp = sp.split(',')
    #print(sp)
    gps_latitude = list()
    if sp[0][3:8] == 'GNGLL':
        print(sp)
        
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


    elif sp[0][:4] == 'None':
        continue
