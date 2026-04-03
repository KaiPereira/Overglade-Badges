from machine import Pin, SoftSPI, PWM, unique_id
import utime
import framebuf
import struct

# The pins selected on the microcontroller on the badges are not default SPI pins.
spi = SoftSPI(
    baudrate=1_000_000,
    polarity=0,
    phase=0,
    sck=Pin(15),
    mosi=Pin(16),
    miso=Pin(20),
)

# Data is fetched from the config.json file, use the badge tool to upload a file.

badge_data = {
    "name": None,
    "pronouns": None,
    "slack_handle": None,
    "other": None
}
# Is Staff configures the badge to show "Staff" since staff were not part of a party during the event.
is_staff = False
configured = False
try:
    with open("config.json", "r") as f:
        import json

        config = json.load(f)
        badge_data["name"] = config.get("userName")
        badge_data["pronouns"] = config.get("userPronouns")
        badge_data["slack_handle"] = config.get("userHandle")
        badge_data["other"] = config.get("other")

        configured = all(v is not None for v in badge_data.values())
except Exception as e:
    print("Config error:", e)
    configured = False


"""
File conversion helper to write a bitmap into the display. 
This only supports bitmaps of 1b depth.
Use Magick or similar tool to construct a valid bitmap.
"""

def bmp_to_framebuf_at(path, fb, x0, y0, max_w=80, max_h=80, invert=False):
    with open(path, "rb") as f:
        if f.read(2) != b"BM":
            raise ValueError("Not a BMP")
        f.seek(10)
        data_offset = struct.unpack("<I", f.read(4))[0]
        f.seek(18)
        w, h = struct.unpack("<ii", f.read(8))
        h = abs(h)
        f.seek(28)
        bpp = struct.unpack("<H", f.read(2))[0]
        if bpp not in (1, 24):
            raise ValueError("Unsupported BMP depth")
        f.seek(data_offset)
        row_bytes = ((w * bpp + 31) // 32) * 4
        draw_w = min(w, max_w)
        draw_h = min(h, max_h)

        for y in range(draw_h):
            row = f.read(row_bytes)
            py = h - 1 - y  # BMP bottom-up
            for x in range(draw_w):
                if bpp == 1:
                    bit = row[x >> 3] & (0x80 >> (x & 7))
                    color = 0 if bit else 1
                else:
                    b, g, r = row[x * 3 : x * 3 + 3]
                    color = 0 if (r + g + b) > 384 else 1

                if invert:
                    color = 1 - color  # invert in code

                fb.pixel(x0 + x, y0 + py, color)


# Configure misc display (non-SPI)
from einkdriver import EPD

disp_cs = Pin(18, Pin.OUT)
disp_dc = Pin(17, Pin.OUT)
disp_rst = Pin(19, Pin.OUT)
disp_busy = Pin(14, Pin.IN)

epd = EPD()

# Main Render code
epd.image_Landscape.fill(0xFF)
# Thanks froppii for the overglade.bmp design :)
bmp_to_framebuf_at("overglade.bmp", epd.image_Landscape, 0, 0, 296, 152)
# image.bmp (80x80), loaded via badge tool into the badge. Must be 1b depth.
bmp_to_framebuf_at("image1.bmp", epd.image_Landscape, 15, 25, 80, 80, invert=True)

# All the text configurations
if configured:
    epd.image_Landscape.rect(10, 20, 90, 90, 0x00)
    
    epd.text_scaled(badge_data["name"], 105, 40, 2, 0x00)
    epd.text_scaled(badge_data["other"], 105, 64, 2, 0x00)
    epd.text_scaled("(" + badge_data["pronouns"] + ")", 105, 100, 1, 0x00)
    epd.text_scaled("@" + badge_data["slack_handle"], 105, 108, 1, 0x00)

# Fallback
else:
    epd.text_scaled("Configuration", 10, 13, 2, 0x00)
    epd.text_scaled("Missing", 10, 32, 2, 0x00)

epd.display_Landscape(epd.buffer_Landscape)

# die
utime.sleep_ms(2000)
epd.init(0)
utime.sleep_ms(2000)
epd.sleep()
