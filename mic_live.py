# this controls the PTT mic control, mic light, the shutdown switch and light
# etc etc.

from gpiozero import LED,Button
from time import sleep
import os
import subprocess
import signal
import asyncio

from display import show

# we need to run 3 asynchronous tasks simultaneously:
#   listening for PTT for mic
#   listening for shutdown button
#   displaying on the OLED

# but first set up all the stuff
sound_cmd = "/usr/bin/rec -c 1 -d equalizer 400 10h -120 | /usr/bin/aplay -f cd -c 1 -t wav &"
print(sound_cmd)

# set up all the pins
mic_led = LED(5)
ptt_button = Button(pin=27, bounce_time=0.1, hold_repeat=False, hold_time=0.5)
shutdown_button = Button(21)
pulldown = LED(11, initial_value=1)  # this makes the power LED dim when we shutdown.


def signal_handler(signum, frame):
    print(f'Handling signal {signum} ({signal.Signals(signum).name}).')

    # do whatever...
    mic_led.blink(on_time=0.2, off_time=0.3)
#    sleep(2)
    # TODO: shutdown the mic stream.
    exit(0)

# catch ALL signals except those that can't be caught.
catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
my_sigs = {signal.SIGTERM, signal.SIGINT}

for sig in my_sigs:
    signal.signal(sig, signal_handler)  


# just to show this is working we flash the mic led.
mic_led.on()
sleep(2)
mic_led.off()

async def microphone_setup():
   # first mute the mic 
   print('muting  mic ...')
   subprocess.run("amixer -c 1 cset  iface=MIXER,name='Mic Capture Volume',numid=8 0", shell=True)
   
   # make sure we start with the light off
   mic_led.off()
   # start sound stream from mic to bluetooth, and just let it run
   print('starting  mic stream ...')
   stream_task = asyncio.create_task(asyncio.create_subprocess_shell(sound_cmd, shell=True, capture_output=False))
   print("... done with microphone setup. stream started...")
   print(stream_task.get_name())
   ptt_button.when_held = mic_on
   #while True:
   #   i =+ 1
      #  if ptt_button.is_held:    
      #    mic_on()
   

def mic_on():
   # unmute the mic 
   print('dialing!')   # this should only happen once per "dial"
   mic_led.on()
   show("mic is ON")
   ptt_button.when_released = mic_off  # reference to the function (not run the function)
   
   # unmute the microphone 
   subprocess.run("amixer -c 1 cset  iface=MIXER,name='Mic Capture Volume',numid=8 70%", shell=True)
   

def mic_off():
   # mute the mic
   subprocess.run("amixer -c 1 cset  iface=MIXER,name='Mic Capture Volume',numid=8 0",shell=True)

   print("mic muted")
   show("mic is OFF")
   mic_led.off()

# shutdown manager
async def shutdown():
   print("initializing shutdown listener")
   while True:
     # shutdown triggers issue of CL shutdown command. TODO: also print to OLED
     if shutdown_button.is_held:
       print("shutting down")
       pulldown.blink(on_time=0.2, off_time=0.2)
       show("shutting down!")
       sleep(5)
       print(os.system('sudo shutdown now'))


# deal with the OLED. can we have a global array hold the lines that the OLED will show?
async def start_display():
   print("starting display")
   while True:
      sleep(1)

async def main():
   print("main loop starting... ")
   background_tasks = set()
   background_tasks.add(asyncio.create_task(microphone_setup()))
   background_tasks.add(asyncio.create_task(shutdown()))
   background_tasks.add(asyncio.create_task(start_display()))
   

# asyncio.run(main()) 
with asyncio.Runner(debug=True) as runner:
    runner.run(main())

