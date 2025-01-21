# this controls the PTT mic control, mic light, the shutdown switch and light
# etc etc.

from gpiozero import LED,Button
from time import sleep
import os
import subprocess
import signal, shlex

sound_cmd = "/usr/bin/rec -c 1 -d equalizer 400 10h -120 | /usr/bin/aplay -f cd -c 1 -t wav"
# args = shlex.split(sound_cmd)
print(sound_cmd)
# print("----")
# print(','.join(args))

def signal_handler(signum, frame):
    print(f'Handling signal {signum} ({signal.Signals(signum).name}).')

    # do whatever...
#    sleep(1)
    # TODO: shutdown the mic stream.
    exit(0)

# catch ALL signals except those tthat can't be caught.
catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
my_sigs = {signal.SIGTERM, signal.SIGINT}

for sig in my_sigs:
    signal.signal(sig, signal_handler)  

mic_led = LED(5)
ptt_button = Button(pin=27, bounce_time=0.1)
# ptt_button = Button(pin=27)
shutdown_button = Button(21)
pulldown = LED(11, initial_value=1)

# start sound stream from mic to bluetooth, and just let it run
# first mute the mic 
# os.system("amixer -c 1 cset  iface=MIXER,name='Mic Capture Volume',numid=8 0")
subprocess.run("amixer -c 1 cset  iface=MIXER,name='Mic Capture Volume',numid=8 0", shell=True)
print('starting mic stream...')
# proc = subprocess.Popen(args) #this fails cuz args is too split up
subprocess.run(sound_cmd, shell=True)

# make sure we start with the light off
mic_led.off()

def mic_on():
   # unmute the mic and start streaming audio to bluetooth
   print('dialing!')   # TODO: how to make this only happen once?
   mic_led.on()
   ptt_button.when_released = mic_off
   
   # unmute the microphone 
   subprocess.run("amixer -c 1 cset  iface=MIXER,name='Mic Capture Volume',numid=8 70%", shell=True)
   

def mic_off():
   # mute the mic
   subprocess.run("amixer -c 1 cset  iface=MIXER,name='Mic Capture Volume',numid=8 0",shell=True)

   print("mic muted")
   mic_led.off()


# main loop 
while True:
  if ptt_button.is_held:    #  pressed:
     mic_on()

  # shutdown triggers issue of CL shutdown command. also print to OLED
  if shutdown_button.is_held:
    print("shutting down")
    pulldown.blink(on_time=0.2, off_time=0.2)
    sleep(5)
    print(os.system('sudo shutdown now'))

 
