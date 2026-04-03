from machine import Pin, SoftSPI 
import framebuf
import utime

# Display resolution
EPD_WIDTH       = 152
EPD_HEIGHT      = 296

RST_PIN         = 19
DC_PIN          = 17
CS_PIN          = 18
BUSY_PIN        = 14


WF_PARTIAL_2IN66 =[
0x00,0x40,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x80,0x80,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x40,0x40,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x80,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x0A,0x00,0x00,0x00,0x00,0x00,0x02,0x01,0x00,0x00,
0x00,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x22,0x22,0x22,0x22,0x22,0x22,
0x00,0x00,0x00,0x22,0x17,0x41,0xB0,0x32,0x36,
]

class EPD:
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.lut = WF_PARTIAL_2IN66

        self.spi = SoftSPI(baudrate=1_000_000, polarity=0, phase=0, sck=Pin(15), mosi=Pin(16), miso=Pin(20))
        self.dc_pin = Pin(DC_PIN, Pin.OUT)
        
        self.buffer_Landscape = bytearray(self.height * self.width // 8)
        self.buffer_Portrait = bytearray(self.height * self.width // 8)
        
        self.image_Landscape = framebuf.FrameBuffer(self.buffer_Landscape, self.height, self.width, framebuf.MONO_VLSB)
        self.image_Portrait = framebuf.FrameBuffer(self.buffer_Portrait, self.width, self.height, framebuf.MONO_HLSB)
        self.init(0)

    # Hardware reset
    def reset(self):
        self.reset_pin(1)
        utime.sleep_ms(200) 
        self.reset_pin(0)
        utime.sleep_ms(200)
        self.reset_pin(1)
        utime.sleep_ms(200)   

    def send_command(self, command):
        self.cs_pin(1)
        self.dc_pin(0)
        self.cs_pin(0)
        self.spi.write(bytearray([command]))
        self.cs_pin(1)

    def send_data(self, data):
        self.cs_pin(1)
        self.dc_pin(1)
        self.cs_pin(0)
        self.spi.write(bytearray([data]))
        self.cs_pin(1)
        
    def send_data1(self, buf):
        self.cs_pin(1)
        self.dc_pin(1)
        self.cs_pin(0)
        self.spi.write(bytearray(buf))
        self.cs_pin(1)
        
    def ReadBusy(self):
        print('e-Paper busy')
        utime.sleep_ms(100)   
        while(self.busy_pin.value() == 1):      # 0: idle, 1: busy
            utime.sleep_ms(100)    
        print('e-Paper busy release')
        utime.sleep_ms(100)  
        
    def TurnOnDisplay(self):
        self.send_command(0x20)        
        self.ReadBusy()
        
    def SendLut(self):
        self.send_command(0x32)
        for i in range(0, 153):
            self.send_data(self.lut[i])
        self.ReadBusy()
    
    def SetWindow(self, x_start, y_start, x_end, y_end):
        self.send_command(0x44) # SET_RAM_X_ADDRESS_START_END_POSITION
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x_start>>3) & 0xFF)
        self.send_data((x_end>>3) & 0xFF)
        self.send_command(0x45) # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)

    def SetCursor(self, x, y):
        self.send_command(0x4E) # SET_RAM_X_ADDRESS_COUNTER
        self.send_data(x & 0xFF)
        
        self.send_command(0x4F) # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)
    
    def init(self, mode):
        
        self.reset()
         
        self.send_command(0x12)  #SWRESET
        self.ReadBusy()
        
        self.send_command(0x11)
        self.send_data(0x03)
        
        self.SetWindow(8, 0, self.width, self.height)
   
        if(mode == 0):
            self.send_command(0x3c)
            self.send_data(0x01)
        elif(mode == 1):
            self.SendLut()
            self.send_command(0x37) # set display option, these setting turn on previous function
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x00)  
            self.send_data(0x40)
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x00)

            self.send_command(0x3C)
            self.send_data(0x80)

            self.send_command(0x22)
            self.send_data(0xcf)
            
            self.send_command(0x20)
            self.ReadBusy()
            
        else: 
            print("There is no such mode")
    
    def display(self, image):
        if (image == None):
            return            
            
        self.SetCursor(1, 295)
        
        self.send_command(0x24) # WRITE_RAM
        self.send_data1(image)
        self.TurnOnDisplay()
        
    def display_Landscape(self, image):
        if(self.width % 8 == 0):
            Width = self.width // 8
        else:
            Width = self.width // 8 +1
        Height = self.height
        
        self.SetCursor(1, 295)
        
        self.send_command(0x24)
        for j in range(Height):
            for i in range(Width):
                self.send_data(image[(Width-i-1) * Height + j])
                
        self.TurnOnDisplay()
    
    def Clear(self, color):
        self.send_command(0x24) # WRITE_RAM
        self.send_data1([color] * self.height * int(self.width / 8))
        self.TurnOnDisplay()
    
    def sleep(self):
        self.send_command(0x10) # DEEP_SLEEP_MODE
        self.send_data(0x01)

    def text_scaled(self, text, x, y, scale=1, color=0):
        """Draw scaled text using the built-in font as a bitmap and expanding pixels.

        This creates a temporary small framebuffer for each input line (8px tall) and scales
        each pixel up by `scale` into the main framebuffer. Works with multiple lines (`\n`).
        """
        if scale <= 1:
            # simple pass-through
            self.image_Landscape.text(text, x, y, color)
            return

        lines = text.split('\n')
        for li, line in enumerate(lines):
            if len(line) == 0:
                continue
            # size of single-line small buffer
            small_w = len(line) * 8
            small_h = 8
            byte_w = (small_w + 7) // 8
            small_buf = bytearray(byte_w * small_h)
            small_fb = framebuf.FrameBuffer(small_buf, small_w, small_h, framebuf.MONO_HLSB)
            small_fb.fill(1)
            small_fb.text(line, 0, 0, 0)

            # For each pixel, copy scaled
            for sy in range(small_h):
                for sx in range(small_w):
                    if small_fb.pixel(sx, sy) == 0:
                        # compute destination
                        dst_x = x + sx * scale
                        dst_y = y + (li * small_h + sy) * scale
                        # fill the scaled pixel block
                        self.image_Landscape.fill_rect(dst_x, dst_y, scale, scale, color)

    def nice_text(self, text, x=0, y=0, color=0, max_scale=None, center=False, center_vertical=False):
        """Draw text using the largest integer scale of the default font that fits the display.

        - Attempts to find the biggest `scale` such that the text (with smart word wrapping)
          fits into the display's width and height.
        - If `center` is True the text will be horizontally centered.
        - If text contains `\n`, those are honored as existing line breaks.

        Returns the scale used and the final list of lines drawn.
        """
        # Compute maximum reasonable scale
        max_scale_possible = min(self.width // 8, self.height // 8)
        if max_scale_possible <= 0:
            max_scale_possible = 1
        if max_scale is not None and max_scale < max_scale_possible:
            max_scale_possible = max_scale

        # Clean newlines and preserve existing
        input_lines = [l.strip() for l in text.split('\n')]

        def wrap_for_scale(scale):
            max_chars = self.width // (8 * scale)
            max_lines = self.height // (8 * scale)
            if max_chars <= 0 or max_lines <= 0:
                return None

            final_lines = []
            for in_l in input_lines:
                if in_l == "":
                    final_lines.append("")
                    continue
                words = in_l.split()
                cur = ""
                for w in words:
                    if len(w) > max_chars:
                        # This scale can't fit the single word
                        return None
                    if cur == "":
                        cur = w
                    elif len(cur) + 1 + len(w) <= max_chars:
                        cur = cur + " " + w
                    else:
                        final_lines.append(cur)
                        cur = w
                if cur != "":
                    final_lines.append(cur)
            if len(final_lines) <= max_lines:
                return final_lines
            return None

        chosen_scale = 3
        chosen_lines = [text]
        for scale in range(max_scale_possible, 0, -1):
            wrapped = wrap_for_scale(scale)
            if wrapped is not None:
                chosen_scale = scale
                chosen_lines = wrapped
                break

        # Now draw lines using scaled text
        total_height = len(chosen_lines) * 8 * chosen_scale
        if center_vertical:
            # Recompute starting y centered vertically inside display
            y = (self.image_Landscape.height - total_height) // 2
        for li, line in enumerate(chosen_lines):
            # compute x offset
            if center:
                text_width = len(line) * 8 * chosen_scale
                xoff = x + (self.width - text_width) // 2
            else:
                xoff = x
            yoff = y + li * 8 * chosen_scale
            self.text_scaled(line, xoff, yoff, scale=chosen_scale, color=color)

        return chosen_scale, chosen_lines
