from smbus2 import SMBus
import threading
import time
import random
bus=SMBus(1)
ADDR=0x9

# lpwr='0.556'
# rpwr='0.987'

l_st=['F','R','S']
r_st=['F','R','S']

alert_dir=['F','B','F','B','B','F']
alert_act=['0','1','0','1','0','1']

drive_st_reg=0
alert_reg=1
bat_reg=2

dir_data_delay=2
alert_data_delay=3
bat_data_req_delay=5

def get_data():
    global bus,bat_reg,ADDR
    while True:
        try:
            data=bus.read_i2c_block_data(ADDR,bat_reg,2)
            print('Received     Bat-1 : ',data[0],'   ','Bat-2 : ',data[1])
            time.sleep(5)

        except:
            print('Cannot request battery @ ',time.time())
        finally:
            time.sleep(bat_data_req_delay)

x=threading.Thread(target=get_data,daemon=True)
x.start()

def send_alert():
    global bus,alert_act,alert_dir,alert_reg,ADDR
    while True:
        try:
            alert_dir_rand=random.choice(alert_dir)
            alert_act_rand=random.choice(alert_act)
            alert_st=alert_dir_rand+':'+alert_act_rand

            alert_st_byte=bytearray(alert_st,'ascii')
            bus.write_block_data(ADDR,alert_reg,alert_st_byte)
            print('Sent alert :',alert_st)
        except:
            print('Cannot write alert state @ ',time.time())
        finally:
            time.sleep(alert_data_delay)

y=threading.Thread(target=send_alert,daemon=True)
y.start()



while True:
    try:
        drive_st=random.choice(l_st)+':'+random.choice(r_st)
        drive_st_byte=bytearray(drive_st,'ascii')
        print(drive_st_byte)
        bus.write_block_data(ADDR,drive_st_reg,drive_st_byte)
        print('Sent drive st : ',drive_st)
        time.sleep(0.1)
    except:
        print('Cannot write bot state @ ',time.time())
    finally:
        time.sleep(dir_data_delay)
