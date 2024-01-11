import time
import utime
import math
import machine
from machine import Pin, I2C



#I2C設定
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=100000) 
address = 0x18
#address = 0x1A

#LIS3DH設定
i2c.writeto_mem(address, 0x20, bytes([0x57]))
#i2c.writeto_mem(address, 0x23, bytes([0x08]))

while True:
    
    #データ読み込み
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
    
    #表示
    print('X: ' + str(out_x))
    print('Y: ' + str(out_y))
    print('Z: ' + str(out_z))

    #一時停止
    time.sleep(1)
