from time import sleep

SAMPLETIME = 0.2

KP = 0.02
KD = 0.01
KI = 0.005


e1_prev_error = 0
e2_prev_error = 0

e1_sum_error = 0
e2_sum_error = 0

def calc_pid(target,m1_speed,m2_speed):
    global e1_prev_error,e2_prev_error,e1_sum_error,e2_sum_error

    e1_error = target - e1.value
    e2_error = target - e2.value

    m1_speed += (e1_error * KP) + (e1_prev_error * KD) + (e1_sum_error * KI)
    m2_speed += (e2_error * KP)  + (e1_prev_error * KD) + (e2_sum_error * KI)

    m1_speed = max(min(1, m1_speed), 0)
    m2_speed = max(min(1, m2_speed), 0)

    sleep(SAMPLETIME)

    e1_prev_error = e1_error
    e2_prev_error = e2_error

    e1_sum_error += e1_error
    e2_sum_error += e2_error
    
    return(m1_speed,m2_speed)