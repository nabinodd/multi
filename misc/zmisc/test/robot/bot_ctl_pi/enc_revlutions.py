from gpiozero import Robot, DigitalInputDevice
import time

r = Robot((3,2), (15,14))

m1_speed = 1.0
m2_speed = 1.0

r.value = (m1_speed, m2_speed)


enc1 = DigitalInputDevice(27)
enc2 = DigitalInputDevice(17)

enc1_clicks=0
enc1_rev=0

enc2_clicks=0
enc2_rev=0

def enc1_fn():
    global enc1_clicks,enc1_rev
    enc1_clicks=enc1_clicks+1

    if enc1_clicks==40:
        enc1_clicks=0
        enc1_rev=enc1_rev+1
        print(enc1_rev,' Revolutions completed by enc 1')

def enc2_fn():
    global enc2_clicks,enc2_rev
    enc2_clicks=enc2_clicks+1

    if enc2_clicks==40:
        enc2_clicks=0
        enc2_rev=enc2_rev+1
        print(enc2_rev,' Revolutions completed enc 2')


enc1.when_activated = enc1_fn
enc1.when_deactivated = enc1_fn

enc2.when_activated = enc2_fn
enc2.when_deactivated = enc2_fn
    

while True:
    time.sleep(1)