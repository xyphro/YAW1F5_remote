from micropython import const
from machine import Pin
from UpyIrTx import UpyIrTx


data = bytearray([0, 0, 0, 0, 0, 0, 0, 0])

BIT_PAUSE  = const(760-152)
BIT_0      = const(450+116)
BIT_1      = const(1540+129)
BIT_START0 = const(9110-485)
BIT_START1 = const(4360+150)
BIT_GAP    = const(19870+140)
global tx
#tx = None

global lastmode
lastmode = 0

global lasttemp
lasttemp = 20



def send():
    # calculate checksum & update
    s = 10
    for d in data[0:4]:
        s = s + (d & 0xf)
    for d in data[4:7]:
        s = s + (d>>4)
    s = s & 0xf
    data[7] = (data[7] & 0x0f) | (s<<4)
        
    # construct pulse stream
    out = [BIT_START0, BIT_START1, BIT_PAUSE]
    for d in data[0:4]:
        for b in range(0, 8):
            if (d>>b) & 1 == 1:
                bit = BIT_1
            else:
                bit = BIT_0
            out.append(bit)
            out.append(BIT_PAUSE)
    
    out.append(BIT_0);   out.append(BIT_PAUSE)
    out.append(BIT_1);   out.append(BIT_PAUSE)
    out.append(BIT_0);   out.append(BIT_PAUSE)
    out.append(BIT_GAP); out.append(BIT_PAUSE)
                       
    for d in data[4:]:
        for b in range(0, 8):
            if (d>>b) & 1 == 1:
                bit = BIT_1
            else:
                bit = BIT_0
            out.append(bit)
            out.append(BIT_PAUSE)
            
    #print(data)
    global tx
    a = tx.send(out)
    print(a)
    
# on / off
# Auto SWING 1000  1	MODE= 1		AUTO=1
# TOP        0100  0	MODE= 2		AUTO=0
# TOP-1      1100  0	MODE= 3		AUTO=0
# MID        0010  0	MODE= 4		AUTO=0
# LOW-1      1010  0	MODE= 5		AUTO=0
# LOW        0110  0	MODE= 6		AUTO=0
# LOW SWING  1110  1	MODE= 7		AUTO=1
# MID SWING  1001  1	MODE= 9		AUTO=1
# TOP SWING  1101  1	MODE=11		AUTO=1
# OFF:       0000  0	MODE= 0		AUTO=0
def setSwing(sw):
    if sw == 'on':
        auto  = 1
        mode = 1
    else:
        auto  = 0
        mode = 2
    data[4] = (data[4] & 0xf0) | (mode<<0); ## Swing range TODO
    if auto:
        data[0] = data[0] | (1<<6)
    else:
        data[0] = data[0] & ~(1<<6)

    

# off, auto, cool, dry, heat, fan_only
def setMode(md):
    pwr = 1
    mode = 0
    global lastmode
    if md == 'off':
        pwr = 0
        mode = lastmode
        setTemperature(lasttemp)
    elif md == 'auto':
        mode = 0
        #setTemperature(lasttemp)
        data[1] = 0;
    elif md == 'cool':
        mode = 1
        setTemperature(lasttemp)
    elif md == 'dry':
        mode = 2
        setTemperature(lasttemp)
    elif md == 'fan_only':
        mode = 3
        setTemperature(lasttemp)
    elif md == 'heat':
        mode = 4
        setTemperature(lasttemp)
    lastmode = mode    
    data[0] = (data[0] & 0xf0) | (mode<<0) | (pwr << 3)

def setFan(fn):
    v = 0
    if fn == 'auto':
        v = 0
    elif fn == 'low':
        v = 1
    elif fn == 'medium':
        v = 2
    elif fn == 'high':
        v = 3
    data[0] = (data[0] & ~(3<<4)) | (v<<4)


def setPreset(ps):
    turbo = 0
    sleep = 0
    if ps == 'boost':
        turbo = 1
        sleep = 0
    elif ps == 'sleep':
        turbo = 0
        sleep = 1
    elif ps == 'none':
        turbo = 0
        sleep = 0
    elif ps == 'activity':
        turbo = 0
        sleep = 0
    data[0] = (data[0] & ~(1<<7)) | (sleep<<7)
    data[2] = (data[2] & ~(1<<4)) | (turbo<<4)


def setTemperature(tp):
    if tp < 16:
        tp = 16;
    if tp > 30:
        tp = 30;
    
    global lasttemp
    lasttemp = tp

    tp = tp - 16;
    data[1] = tp;


def init():
    tx_pin = Pin(19, Pin.OUT)
    global tx
    tx = UpyIrTx(0, tx_pin, const(38000), const(30), const(0))
    data[3] = data[3] | (5<<4) # fixed value
    #data[5] = data[5] | (4<<3) # fixed value
    data[2] = data[2] | (1<<5) # light
    data[2] = data[2] | (1<<6) # model
    setTemperature(20)
    setPreset('activity')
    setFan('auto')
    setMode('off')
    setSwing('on')
    