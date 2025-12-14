from machine import Pin, SPI, PWM, unique_id
import utime

spi = SPI(0, baudrate=1_000_000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(20))

badge_data = {
    "name": None,
    "pronouns": None,
    "slack_handle": None
}
configured=False
try:
    with open("config.json", "r") as f:
        import json
        config = json.load(f)
        badge_data["name"] = config.get("userName")
        badge_data["pronouns"] = config.get("userPronouns")
        badge_data["slack_handle"] = config.get("userHandle")
        configured=True
except Exception as e:
    print("No config file found or error reading it:", e)

from einkdriver import EPD
disp_cs = Pin(24, Pin.OUT)
disp_dc = Pin(25, Pin.OUT)
disp_rst = Pin(26, Pin.OUT)
disp_busy = Pin(27, Pin.IN)

print("Initializing E-Ink display...")
display = EPD(spi, disp_cs, disp_dc, disp_rst, disp_busy)
display.init()

print("Displaying name on badge...")
display.fill(1)  # Fill with white
# Choose name to display, fallback to 'badge self-test' if not configured
name_to_show = badge_data.get("name") or "badge self-test"
# Use the new nice_text helper to pick the biggest font and center horizontally and vertically
display.nice_text(name_to_show, x=0, y=0, color=0, center=True, center_vertical=True)
display.display()
display.sleep()