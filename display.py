
import time
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont, ImageOps
import adafruit_ssd1306

print("setting up the display...")

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


# Load default font.
# font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
bigfont = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
i = 0

def test_func(text):
   print("testing, testing!")
   time.sleep(1)
   print(text)


# while True:
async def show(text):

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    cmd = "hostname -I | cut -d' ' -f1"
    IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = 'date +%r'
    clock = subprocess.check_output(cmd, shell=True).decode("utf-8")

    # Write lines of text.

    draw.text((x, top + 0), clock, font=font, fill=255)

    # show the bluetooth device we're connected to.
    # draw.text((x, top + 8), "Connected to: ", font=font, fill=255)
    draw.text((x, top + 16), "IP: " + IP, font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.show()
    time.sleep(0.1)
    i += 1

    if i == 30:
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        draw.text((x, top + 0), "EXO ROAST CO", font=bigfont, fill=255)
        disp.image(image)
        disp.show()
        time.sleep(3)
        i = 0
