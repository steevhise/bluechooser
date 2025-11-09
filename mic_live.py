#!/home/steev/env/bin/python3

# this controls the PTT mic control, mic light, the shutdown switch and light
# etc etc.

from gpiozero import LED,Button
from time import sleep
import os
import subprocess
import signal
import asyncio
import json
from pprint import pprint
from display import show, show_default

# we need to run 3 asynchronous tasks simultaneously:
#   listening for PTT for mic
#   listening for shutdown button
#   displaying on the OLED

background_tasks = set()

# but first set up all the stuff
sound_cmd = "/usr/bin/rec -c 1 -r 8000 -b 8 -d hilbert equalizer 400 50h -120 sinc 500-3k vol 6 db | /usr/bin/aplay -c 1 &"
# sound_cmd = "/usr/bin/rec -c 1 -d sinc 1k-4k | /usr/bin/aplay -f cd -c 1 -t wav &"
print(sound_cmd)

# set up all the pins
mic_led = LED(5)
ptt_button = Button(pin=27, bounce_time=0.1, hold_repeat=False, hold_time=0.2)
shutdown_button = Button(21)
pulldown = LED(11, initial_value=1)  # this makes the power LED dim when we shutdown.


def signal_handler(signum, frame):
    print(f'Handling signal {signum} ({signal.Signals(signum).name}).')

    mic_led.blink(on_time=0.2, off_time=0.3, n=10, background=True)
    show("software shutdown")
    sleep(2)
    #  shutdown the mic stream.
    micTask = findInSet('streamTask')
    if micTask != None:
      print(micTask)
      print(micTask.cancel())
      print("mic stream cancelled")
    exit(0)

my_sigs = {signal.SIGTERM, signal.SIGINT}
for sig in my_sigs:
    signal.signal(sig, signal_handler)


async def microphone_setup():
   # first mute the mic  - mute and turn vol down, seems to be required.
   print('muting  mic ...')
   subprocess.run("amixer -c 1 cset  iface=MIXER,name='Mic Capture Switch',numid=7 off",shell=True)
   subprocess.run("amixer -c 1 cset  iface=MIXER,name='Mic Capture Volume',numid=8 0", shell=True)

   # make sure we start with the light off
   mic_led.off()
   # start sound stream from mic to bluetooth, and just let it run
   print('starting  mic stream ...')
   stream_task = asyncio.create_task(asyncio.create_subprocess_shell(sound_cmd, stderr=asyncio.subprocess.DEVNULL), name="streamTask" )
   print("... done with microphone setup. stream started...")
   shutdown_button.when_held = shutdown

def mic_on():
   print('dialing!')   # this should only happen once per "dial"
   mic_led.blink(off_time=.01, on_time=1, n=10, background=True)  # background makes it async

   # unmute the microphone
   subprocess.run("amixer -c 1 cset  iface=MIXER,name='Mic Capture Switch',numid=7 on",shell=True)
   subprocess.run("amixer -c 1 cset  iface=MIXER,name='Mic Capture Volume',numid=8 25", shell=True)
   print("mic is live!")
   show("mic is ON")
   # audit('showresume')

def mic_off():
   # mute the mic
   subprocess.run("amixer -c 1 cset  iface=MIXER,name='Mic Capture Switch',numid=7 off",shell=True)
   subprocess.run("amixer -c 1 cset  iface=MIXER,name='Mic Capture Volume',numid=8 0", shell=True)
   print("mic is muted")
   mic_led.off()
   show("mic is OFF")
   # audit('showresume')

def shutdown():
   print("shutting down")
   pulldown.blink(on_time=0.2, off_time=0.2, background=True)
   show("shutting down!")
   sleep(2)
   print(os.system('sudo shutdown now'))

def findInSet(name="show-default"):
   for task in background_tasks:
       if task.get_name() == name:
           return task

   return None

# read in file that has the bluetooth device we're supposed to be on, 
# and make sure the one we're really connected to is the same.
def bluetooth_stuff():
   print("bluetooth stuff. Might take a moment..")
   # now look in the file that is saved by the node web interface code.
   with open("/home/steev/data/bluetooth.json") as json_data:
       d = json.load(json_data)
       json_data.close()
       pprint(d)

   connected = subprocess.getoutput("bluetoothctl info " + d['address'] + " | grep -i connected | cut -f 2 -d' '")
   print("connected? ", connected)

   if(connected == 'no'):
       reconn = subprocess.getoutput("bluetoothctl connect " + d['address'])
       print(reconn)

   # if(d['name'] == bt_current):
   return d['name']

   # otherwise... TODO: try connecting.
   # return "none"

# some setup - just to show this is working we flash the mic led.
mic_led.on()
sleep(2)
mic_led.off()

async def main():
   ptt_button.when_held = mic_on
   ptt_button.when_released = mic_off  # reference to the function (not run the function)
   bt_stuff = bluetooth_stuff()
       
   print('connected to',  bt_stuff, type(bt_stuff))
   oled_task = asyncio.create_task(show_default(bt_stuff), name="show-default")
   mic_task = asyncio.create_task(microphone_setup(), name="mic-setup")
  
   await asyncio.sleep(1)   # why did i put this here? hmm

# asyncio.run(main())
with asyncio.Runner(debug=False) as runner:
    loop = runner.get_loop()
    runner.run(main())


