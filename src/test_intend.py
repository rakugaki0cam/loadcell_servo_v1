# error test
#
# >>> 
# Traceback (most recent call last):
# File "<stdin>", line 2
# IndentationError: unexpected indent
# >
# MicroPython v1.19.1 on 2022-06-18; ESP module with ESP8266
# Type "help()" for more information.
# >>> 
#
# 原因は　全角の "！"
# これがあるところまでのコードが無視されて
# 次の行からしかRunされないみたい
# Uploadしたときは正常に動くよう
#
#

print("test")
print("Hello world!")

def testSub():
    i = 0   ####　！！！！！！！！！  ← これがダメ
    return i

print("end")
