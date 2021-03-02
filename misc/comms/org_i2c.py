from smbus2 import SMBus
import threading
import time

bus=SMBus(1)
ADDR=0x9

lpwr='0.556'
rpwr='0.987'
pwrr=lpwr+','+rpwr
pwrr=bytearray(pwrr,'ascii')

def get_data():
    global bus
    while True:
        try:
            data=bus.read_i2c_block_data(ADDR,5,2)
            print('Bat-1 : ',data[0],'   ','Bat-2 : ',data[1])
            time.sleep(5)
        
        except:
            print('Cannot request @ ',time.time())
            time.sleep(1)

x=threading.Thread(target=get_data,daemon=True)
x.start()

while True:
    try:
        bus.write_block_data(ADDR,3,pwrr)
        print('Sent @ ',time.time())
        time.sleep(0.1)
    except:
        print('Cannot write @ ',time.time())
        time.sleep(1)
