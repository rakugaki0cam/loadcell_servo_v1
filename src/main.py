#   loadcell   HX711  500gf
#   servo motor SG92R
#
#       2022.11.18
#

import  utime
from    machine     import Pin, PWM


print("##### Load cell & servo test #######")

### loadcell init #####
ledWhite = Pin(2, Pin.OUT)
ledWhite.value(1)
utime.sleep_ms(400)
ledWhite.value(0)
utime.sleep_ms(200)
ledWhite.value(1)
utime.sleep_ms(50)
ledWhite.value(0)
utime.sleep_ms(200)
ledWhite.value(1)
utime.sleep_ms(50)
ledWhite.value(0)

#hx711 Loadcell ADconverter
hx711Clock = Pin(14, Pin.OUT)
hx711Data = Pin(12, mode = Pin.IN, pull = None)

#reset
hx711Clock.on()
utime.sleep_ms(1)
hx711Clock.off()
utime.sleep_ms(1)

def readAdc():
    adValue = 0
    while True:
        if hx711Data.value() == 0:
            break

    for i in range(24):
        hx711Clock.value(1)
        #utime.sleep_us(0)      #遅延いれると遅すぎてダメ 20us->70usになる
        hx711Clock.value(0)
        adValue = adValue << 1
        adValue += hx711Data.value()

    hx711Clock.value(1)
    hx711Clock.value(0)
    if (adValue & 0x00800000) != 0:
        #マイナスの時の処理(24ビット)
        adValue = (adValue ^ 0xfffffe) * -1
    #print("{:06x}".format(adValue), end = '  ')
    return adValue

def averageData(n):
    dataSum = 0
    for i in range(n):
        dataSum += readAdc()
    ave = int(dataSum / n)
    #print("average = 0x{:06x}".format(ave), end = '  ')
    return ave

def tare():
    #風袋
    dataZero = averageData(10)
    return dataZero



### servo init #####
servo1 = PWM(Pin(13), freq = 50)    #PWM freq 1~1000Hz
                                    #servo 50Hz = 20msec

def pwmDuty(percent):
    value = 1024 * percent / 100    #duty 0~1024
    return int(value)

def servoDegree(setDeg):
    if (setDeg < -90) or (setDeg > 90):
        return 0
    v0 = 74     #1.45msec = 7.25%
    vn90 = 120  #2.4msec = 12.0%
    vp90 = 30   #0.5msec = 2.5%
    value = - setDeg * (vn90 - vp90) / 180 + v0    #2度ごとにしか設定できない！！！
    return int(value)


#####  MAIN ####################################################################


# servo
servo1.duty(servoDegree(20))

# loadcell
V_out = 0.000728    #センサ出力電圧 [V/V] @maxLoad 0.65~0.95mV
maxLoad  = 500.0    #センサ定格 [g]
R1    = 12000       #R1抵抗値 [Ω] 3.3V版に改造
R2    = 8200        #R2抵抗値 [Ω]
Vbg   = 1.25        #アナログリファレンス電圧 [V]
aVdd  = Vbg * (R1+R2)/R2     #アナログ電圧フルスケールAVdd [V]
ADC1bit = aVdd / 2**24       #フルスケールを24bitで割る [V]
ADCGain  = 128                  #A/D ゲイン
Scale  = V_out * aVdd / maxLoad  #ロードセル特性　[V/gf]

ZeroOffset = tare()     #ゼロ合わせ



data = []
input() #dummyなぜか最初のinputが効かないので


while True:

    input('push to start')


    for deg in range(20, -20, -2):
        d = servoDegree(deg)
        servo1.duty(d)
        utime.sleep_ms(50)
        adV = averageData(4)
        weight = (adV - ZeroOffset) * (ADC1bit / (Scale * ADCGain))
        data.append([deg, weight])
        print("{:3d}deg  {:8.2f}gf".format(deg, weight))


    #for deg, weight in data:
    #
    #     print("{:3d}deg  {:8.2f}gf".format(deg, weight))
    ledWhite.value(1)
    input('push to next')

    ledWhite.value(0)
    servo1.duty(servoDegree(20))
    utime.sleep_ms(1000)
    print()
