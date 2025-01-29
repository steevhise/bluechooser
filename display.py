import time
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont, ImageOps
import adafruit_ssd1306
import asyncio
from sys import audit, addaudithook

print("setting up the display...")
stop = False  # this is to make an event stop a while loop

# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
bigfont = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)

# this makes us wait if a certain event happens
def show_wait(event, waitseconds):
    if event == "showwait":
        seconds = waitseconds[0]
        print("received showwait event, sleeping for ", seconds, " seconds")
        stop = True
        # time.sleep(seconds)

def show_resume(event, waitseconds):
    if event == 'showresume':
      print("recieved show resume event")
      stop = False

async def show_default():

  i = 0
 
  addaudithook(show_wait)
  addaudithook(show_resume)

  while True:
     if stop:
        print(stop)
        await asyncio.sleep(0)
        continue
     print(stop)
     try:
        i += 1;
        # Draw a black filled box to clear the image.
        await asyncio.sleep(0)
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
   
        # give lots of chances for other process to update.
        await asyncio.sleep(0)
        cmd = "hostname -I | cut -d' ' -f1"
        IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = 'date +%r'
        clock = subprocess.check_output(cmd, shell=True).decode("utf-8")
   
        print(clock)
        draw.text((x, top + 0), clock, font=font, fill=255)

        # show the bluetooth device we're connected to.
        # draw.text((x, top + 8), "Connected to: ", font=font, fill=255)
    
        # show our ip address
        draw.text((x, top + 16), "  IP: " + IP, font=font, fill=255)

        await asyncio.sleep(0)
        # Display image.
        disp.image(image)
        disp.show()
        # repeated pauses so the clock will update. i think?
        await asyncio.sleep(1)

        # x times out of y we just start over here.
        print(i,"---",i%9)
        if i%9 != 0:
            await asyncio.sleep(0)
            continue 

        # but sometimes cycle to the next one.
        print("showing 2nd screen...")
        await asyncio.sleep(0)
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        draw.text((x, top + 0), "EXO ROAST CO", font=bigfont, fill=255)
        disp.image(image)
        await asyncio.sleep(0)
        disp.show()
        await asyncio.sleep(3)
        # time.sleep(3) 
        result = await asyncio.sleep(4, "back to default image task!") 
        print(result)
     except asyncio.CancelledError as e:   # this is catching when task finishes i think.
        print(e)
     finally:
        print(i)

def show(text):
    
    wait_time = 0
    # Write lines of text.
    if text is not None:
       if len(text) < 13:
          fnt = bigfont
          wait_time = 4

       else:
          fnt = font
          wait_time = 6

       # raise events - make the show_default function wait and not write anything while we write.
       audit('showwait', wait_time)

       # first Draw a black filled box to clear the image.
       disp.fill(0)
       disp.show()
       draw.rectangle((0, 0, width, height), outline=0, fill=0)
       draw.text((x, top + 0), text, font=fnt, fill=255)
       disp.image(image)
       disp.show()
       # await asyncio.sleep(wait_time)
       time.sleep(2)
       audit('showresume')
       time.sleep(2)
