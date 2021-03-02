#For starting joystick(From PC)
Navigate to joystick.py
python3 joystick.py   (install required dependencies)


1. Switch on the robot
2. Check connectivity(IP)
3. Commands

ssh pi@multipi.local >> pw : pi


cd code_base

#For starting gui and auto entry(From vnc)
(open 2 terminals)
-GUI
cd gui
python3 main_win_x.py
pin for shutdown and reboot = 2020
pin for gui exit = 2021

-Auto entry aruco
cd robot_control
workon bot
python3 p1_auto_center.py


#For starting drive
(open another terminal)
cd robot_control
workon bot
sudo pigpiod(if system is just booted)
python3 robot_ctl.py


# to switch between manual(5) and automatic(6) modes press buttons(if not wire loose)
# lifter up (2 + 8 + 12)
# lifter down(2 + 11 + 7)
# camera up down ( top hat up down)
# camera pos reset (shooter)
# Acclerator knob for speed control



topics
*('joystick/lifter','down')
*('joystick/lifter','up')
*('joystick/cam_rst',str(trig_btn))
*('joystick/cam_up_down',str(hat_lr[1]))
('joystick/accl',str(accl_knob))
('auto_entry','0')
('auto_entry','1')
('botcmd/stop','1') # will be pub if joystick in 0,0
*('joystick/lr',str(left_right))
*('joystick/lr','0')
*('joystick/fwrev',str(fwd_rev))
*('joystick/fwrev','0')

('joystick/xy',str(left_right)+':'+str(fwd_rev))


ultrasonic_read=str(us_fl_dist)+','+str(us_fr_dist)+','+str(us_bl_dist)+','+str(us_br_dist)
client.publish('ultrasonic',ultrasonic_read)
