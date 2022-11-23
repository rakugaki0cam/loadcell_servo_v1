#   loadcell   HX711  500gf
#   servo motor SG92R
#
#       2022.11.18
#

import utime
from machine import Pin, PWM


print("##### Load cell & servo test ###########################")

### switch & LED #####
sw1 = Pin(5, mode = Pin.IN, pull = Pin.PULL_UP)
ledWhite = Pin(2, Pin.OUT)
# Power on LED
ledWhite.on()
utime.sleep_ms(500)
ledWhite.off()
utime.sleep_ms(300)
ledWhite.on()
utime.sleep_ms(100)
ledWhite.off()
utime.sleep_ms(100)
ledWhite.on()
utime.sleep_ms(100)
ledWhite.off()


### loadcell init #####
# hx711 Loadcell ADconverter
hx711Clock = Pin(14, Pin.OUT)
hx711Data = Pin(12, mode=Pin.IN, pull=None)
# reset
hx711Clock.on()
utime.sleep_ms(1)
hx711Clock.off()
utime.sleep_ms(1)

V_out = 0.000728  # センサ出力電圧 [V/V] @maxLoad 0.65~0.95mV
maxLoad = 500.0  # センサ定格 [g]
R1 = 12000  # R1抵抗値 [Ω] 3.3V版に改造
R2 = 8200  # R2抵抗値 [Ω]
Vbg = 1.25  # アナログリファレンス電圧 [V]
aVdd = Vbg * (R1+R2)/R2  # アナログ電圧フルスケールAVdd [V]
ADC1bit = aVdd / 2**24  # フルスケールを24bitで割る [V]
ADCGain = 128  # A/D ゲイン
Scale = V_out * aVdd / maxLoad  # ロードセル特性　[V/gf]

def readAdc():
    adValue = 0
    while True:
        if hx711Data.value() == 0:
            break

    for i in range(24):
        hx711Clock.value(1)
        # utime.sleep_us(0)      #遅延いれると遅すぎてダメ 20us->70usになる
        hx711Clock.value(0)
        adValue = adValue << 1
        adValue += hx711Data.value()

    hx711Clock.value(1)
    hx711Clock.value(0)
    if (adValue & 0x00800000) != 0:
        # マイナスの時の処理(24ビット)
        adValue = (adValue ^ 0xfffffe) * -1
    #print(f"{adValue:06x}", end = '  ')
    return adValue

def averageData(n, dotDisp):
    dataSum = 0
    for i in range(n):
        dataSum += readAdc()
        if dotDisp == 1:
            print('.', end = "")
    ave = int(dataSum / n)
    #print("average = 0x{:06x}".format(ave), end = '  ')
    return ave

def tare():
    # 風袋
    print('zero set ', end = '')
    dataZero = averageData(10, 1)
    print(' OK!')
    return dataZero

def loadcellTest():
    # ロードセルの連続表示　デバッグ用
    while True:
        weightT = (readAdc() - ZeroOffset) * (ADC1bit / (Scale * ADCGain))
        print(f"{weightT:8.2f}gf")


### servo init #####
armR = 10 #サーボホーンの腕の長さ[mm]
startDeg = -20	#初期角度[°]
endDeg = 30	    #初期角度[°]
incDeg = 2      #角度増分[°]

servo1 = PWM(Pin(13), freq=50)  # PWM freq 1~1000Hz
# servo 50Hz = 20msec

def pwmDuty(percent):
    value = 1024 * percent / 100  # duty 0~1024
    return int(value)

def servoDegree(setDeg):
    if (setDeg < -90) or (setDeg > 90):
        return 0
    v0 = 74  # 1.45msec = 7.25%
    vn90 = 120  # 2.4msec = 12.0%
    vp90 = 30  # 0.5msec = 2.5%
    value = -setDeg * (vn90 - vp90) / 180 + v0  #2度ごとにしか設定できない
    return int(value)

def servoPos():
    #サーボの位置確認
    print('SERVO TEST   position check  push button to next position')

    while True:
        print('zero position')
        servo1.duty(servoDegree(0))         ###### サーボ　ゼロ位置
        utime.sleep(1)
        while True:
            if oneSec() == 1:
                break

        print('start position')
        servo1.duty(servoDegree(startDeg))  ###### サーボ　スタート位置
        utime.sleep(1)
        while True:
            if oneSec() == 1:
                break

        print('end position')
        servo1.duty(servoDegree(endDeg))    ###### サーボ　エンド位置
        utime.sleep(1)
        while True:
            if oneSec() == 1:
                break

def servoMove():
    #サーボを動かして見てみる
    print('SERVO TEST   push button to 1step rotate')
    posDeg = 0
    degInc = 2
    while True:
        servo1.duty(servoDegree(posDeg))         ###### サーボ　ゼロ位置
        print(f"{posDeg:3d}deg")
        utime.sleep_ms(200)

        while True:
            if sw1.value() == 0:
                break
        posDeg += degInc
        if posDeg >= endDeg:
            #deg -= ddeg
            degInc = -2
        if posDeg <= startDeg:
            #deg -= ddeg
            degInc = 2


### 入力等 サブ #####
def oneSec():
    #1秒のボタン入力待ち
    for i in range(10):
        utime.sleep_ms(100)
        if sw1.value() == 0:
            return 1
    return 0


### テスト #####
#ZeroOffset = tare()    ###### 秤のゼロ合わせ
#loadcellTest()         ###### loadcell 連続表示テスト
#servoPos()             ###### サーボの位置
#servoMove()            ######サーボを動かしてみる


#####  MAIN ####################################################################
data = []

# main on LED
utime.sleep_ms(500)
ledWhite.on()


while True:
    #サーボ初期位置
    servo1.duty(servoDegree(startDeg))
    utime.sleep_ms(1000)

    print('push button to start measurement')
    while True:
        if sw1.value() == 0:
            break

    #測定開始
    ledWhite.value(0)
    ZeroOffset = tare()  # 毎回ゼロ合わせ
    utime.sleep_ms(300)

    for deg in range(startDeg, endDeg, incDeg):
        print(f"{deg:3d} deg  ", end = "")
        d = servoDegree(deg)
        servo1.duty(d)
        utime.sleep_ms(150)
        adV = averageData(6, 1)
        weight = (adV - ZeroOffset) * (ADC1bit / (Scale * ADCGain))
        data.append([deg, weight])
        print(f" {weight:6.1f} gf")

    #保存データを見る
    # for deg, weight in data:
    #     print(f"{deg:3d}deg  {weight:8.2f}gf")


    print('push button to next')
    while True:
        ledWhite.on()
        if oneSec() == 1:
            break
        ledWhite.off()
        if oneSec() == 1:
            break
    print()
    ledWhite.on()

