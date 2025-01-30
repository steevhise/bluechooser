# this controls the PTT mic control, mic light, the shutdown switch and light
# etc etc.

from gpiozero import LED,Button
from time import sleep
import os
import subprocess
import signal
import asyncio
from pprint import pprint
from display import show, show_default

# we need to run 3 asynchronous tasks simultaneously:
#   listening for PTT for mic
#   listening for shutdown button
#   displaying on the OLED

background_tasks = set()

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

    mic_led.blink(on_time=0.2, off_time=0.3, n=10, background=True)
    sleep(2)
    #  shutdown the mic stream.
    micTask = findInSet('streamTask')
    if micTask != None:
      print(micTask)
      micTask.cancel()
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
   subprocess.run("amixer -c 1 cset  iface=MIXER,name='Mic Capture Switch',numid=7 mute",shell=True)
   subprocess.run("amixer -c 1 cset  iface=MIXER,name='Mic Capture Volume',numid=8 0", shell=True)
   
   # make sure we start with the light off
   mic_led.off()
   # start sound stream from mic to bluetooth, and just let it run
   print('starting  mic stream ...')
   stream_task = asyncio.create_task(asyncio.create_subprocess_shell(sound_cmd, stderr=asyncio.subprocess.DEVNULL), name="streamTask" )
   print("... done with microphone setup. stream started...")
   ptt_button.when_held = mic_on
   ptt_button.when_released = mic_off  # reference to the function (not run the function)
   shutdown_button.when_held = shutdown
   

def mic_on():
   print('dialing!')   # this should only happen once per "dial"
   mic_led.blink(time_off=.01, time_on=4, n=10, background=True)  # background makes it async
   
   # unmute the microphone 
   subprocess.run("amixer -c 1 cset  iface=MIXER,name='Mic Capture Switch',numid=7 80%", shell=True)
   print("mic is live!")
   show("mic is ON")

def mic_off():
   # mute the mic
   subprocess.run("amixer -c 1 cset  iface=MIXER,name='Mic Capture Switch',numid=7 mute",shell=True)
   print("mic muted")
   mic_led.off()
   show("mic is OFF")

def shutdown():
   print("shutting down")
   pulldown.blink(on_time=0.2, off_time=0.2, background=True)
   show("shutting down!")
   time.sleep(2)
   print(os.system('sudo shutdown now'))

def findInSet(name="show-default"):
   for task in background_tasks:
       if task.get_name() == name:
           return task
   
   return None

async def main():
   # The OLED screen has to be async.
   oled_task = asyncio.create_task(show_default(), name="show-default")
  
   # run other stuff outside the event loop
   await microphone_setup()

   await asyncio.sleep(1)
   tasks = asyncio.all_tasks()
   # pprint(tasks)


# asyncio.run(main()) 
with asyncio.Runner(debug=False) as runner:
    loop = runner.get_loop()
    runner.run(main())

