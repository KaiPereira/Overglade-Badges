"""
MicroPython library for Waveshare 1.54" E-Paper Display V2
Based on the original C++ driver from Waveshare
Converted to MicroPython format for easier use with MicroPython boards
Handles low-level comms with the display
"""

import framebuf
import utime

# Display resolution
EPD_WIDTH  = 200
EPD_HEIGHT = 200

# Command constants
DRIVER_OUTPUT_CONTROL                = 0x01
BOOSTER_SOFT_START_CONTROL           = 0x0C
GATE_SCAN_START_POSITION             = 0x0F
DEEP_SLEEP_MODE                      = 0x10
DATA_ENTRY_MODE_SETTING              = 0x11
SW_RESET                             = 0x12
MASTER_ACTIVATION                    = 0x20
DISPLAY_UPDATE_CONTROL_1             = 0x21
DISPLAY_UPDATE_CONTROL_2             = 0x22
WRITE_RAM                            = 0x24
WRITE_VCOM_REGISTER                  = 0x2C
WRITE_LUT_REGISTER                   = 0x32
SET_DUMMY_LINE_PERIOD                = 0x3A
SET_GATE_TIME                        = 0x3B
BORDER_WAVEFORM_CONTROL              = 0x3C
SET_RAM_X_ADDRESS_START_END_POSITION = 0x44
SET_RAM_Y_ADDRESS_START_END_POSITION = 0x45
SET_RAM_X_ADDRESS_COUNTER            = 0x4E
SET_RAM_Y_ADDRESS_COUNTER            = 0x4F
TERMINATE_FRAME_READ_WRITE           = 0xFF

# Waveform full refresh
WF_FULL_1IN54 = bytearray([
    0x80, 0x48, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x40, 0x48, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x80, 0x48, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x40, 0x48, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0xA, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x8, 0x1, 0x0, 0x8, 0x1, 0x0, 0x2,
    0xA, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x0, 0x0, 0x0,
    0x22, 0x17, 0x41, 0x0, 0x32, 0x20
])

# Waveform partial refresh (fast)
WF_PARTIAL_1IN54_0 = bytearray([
    0x0, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x80, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x40, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0xF, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x1, 0x1, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x0, 0x0, 0x0,
    0x02, 0x17, 0x41, 0xB0, 0x32, 0x28,
])

class EPD:
    def __init__(self, spi, cs, dc, rst, busy, width=EPD_WIDTH, height=EPD_HEIGHT):
        """
        Initialize E-Paper display
        
        Args:
            spi: SPI bus instance
            cs: Chip select pin
            dc: Data/Command pin
            rst: Reset pin
            busy: Busy pin
            width: Display width (default 200)
            height: Display height (default 200)
        """
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.busy = busy
        self.width = width
        self.height = height
        
        # Initialize pins
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.busy.init(self.busy.IN)
        
        # Create buffer for frame
        self.buffer_size = (self.width // 8) * self.height
        self.buffer = bytearray(self.buffer_size)
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_HLSB)
        
        # Initialize display (default to horizontal direction)
        self.init()
    
    def send_command(self, command):
        """Send command to display"""
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytearray([command]))
        self.cs.value(1)

    def send_data(self, data):
        """Send data to display"""
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(bytearray([data]))
        self.cs.value(1)
    
    def reset(self):
        """Reset the display"""
        self.rst.value(1)
        utime.sleep_ms(20)
        self.rst.value(0)
        utime.sleep_ms(5)
        self.rst.value(1)
        utime.sleep_ms(20)
    
    def wait_until_idle(self):
        """Wait until the busy pin goes HIGH"""
        while self.busy.value() == 1:      # LOW: idle, HIGH: busy
            utime.sleep_ms(100)
        utime.sleep_ms(200)
    
    def lut(self, lut_array):
        """Send lookup table to display"""
        self.send_command(WRITE_LUT_REGISTER)
        for i in range(153):
            self.send_data(lut_array[i])
        self.wait_until_idle()
    
    def set_lut(self, lut_array):
        """Set lookup table and related registers"""
        self.lut(lut_array)
        
        self.send_command(0x3f)
        self.send_data(lut_array[153])
        
        self.send_command(0x03)
        self.send_data(lut_array[154])
        
        self.send_command(0x04)
        self.send_data(lut_array[155])
        self.send_data(lut_array[156])
        self.send_data(lut_array[157])
        
        self.send_command(0x2c)
        self.send_data(lut_array[158])
    
    def init(self, orientation='h'):
        """
        Initialize display
        
        Args:
            orientation: 'h' for horizontal (default) or 'v' for vertical
        """
        self.reset()
        
        self.wait_until_idle()
        self.send_command(SW_RESET)  # SWRESET
        self.wait_until_idle()
        
        self.send_command(DRIVER_OUTPUT_CONTROL)  # Driver output control
        self.send_data(0xC7)
        self.send_data(0x00)
        if orientation == 'h':  # Horizontal
            self.send_data(0x01)
            
            self.send_command(DATA_ENTRY_MODE_SETTING)  # Data entry mode
            self.send_data(0x01)
            
            self.send_command(SET_RAM_X_ADDRESS_START_END_POSITION)  # Set Ram-X address start/end position
            self.send_data(0x00)
            self.send_data(0x18)  # 0x0C-->(18+1)*8=200
            
            self.send_command(SET_RAM_Y_ADDRESS_START_END_POSITION)  # Set Ram-Y address start/end position
            self.send_data(0xC7)  # 0xC7-->(199+1)=200
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x00)
        else:  # Vertical (Low direction)
            self.send_data(0x00)
            
            self.send_command(DATA_ENTRY_MODE_SETTING)  # Data entry mode
            self.send_data(0x03)
            
            self.send_command(SET_RAM_X_ADDRESS_START_END_POSITION)
            self.send_data((0 >> 3) & 0xFF)
            self.send_data((199 >> 3) & 0xFF)
            
            self.send_command(SET_RAM_Y_ADDRESS_START_END_POSITION)
            self.send_data(0 & 0xFF)
            self.send_data((0 >> 8) & 0xFF)
            self.send_data(199 & 0xFF)
            self.send_data((199 >> 8) & 0xFF)
        
        self.send_command(BORDER_WAVEFORM_CONTROL)  # BorderWaveform
        self.send_data(0x01)
        
        self.send_command(0x18)
        self.send_data(0x80)
        
        self.send_command(DISPLAY_UPDATE_CONTROL_2)  # Load Temperature and waveform setting
        self.send_data(0xB1)
        self.send_command(MASTER_ACTIVATION)
        
        self.send_command(SET_RAM_X_ADDRESS_COUNTER)  # Set RAM x address count
        self.send_data(0x00)
        
        self.send_command(SET_RAM_Y_ADDRESS_COUNTER)  # Set RAM y address count
        self.send_data(0xC7)
        self.send_data(0x00)
        
        self.wait_until_idle()
        
        # Set LUT
        self.set_lut(WF_FULL_1IN54)
    
    def clear(self):
        """Clear the display with white"""
        w = (self.width + 7) // 8  # Width in bytes, ceiling division
        h = self.height
        
        self.send_command(WRITE_RAM)
        for j in range(h):
            for i in range(w):
                self.send_data(0xFF)  # White
        
        # Display refresh
        self.display_frame()
    
    def display(self, buffer=None):
        """
        Display a frame buffer
        
        Args:
            buffer: Buffer to display (uses internal buffer if None)
        """
        self.reset()
        self.init_full_mode()
        
        if buffer is None:
            buffer = self.buffer
        
        w = (self.width + 7) // 8  # Width in bytes, ceiling division
        h = self.height
        
        self.send_command(WRITE_RAM)  # Write to RAM area 0x24
        for j in range(h):
            for i in range(w):
                self.send_data(buffer[i + j * w])
        
        
        # Display refresh
        self.display_frame()

    def display_base_image(self, buffer=None):
        """
        Display a base image for partial refresh mode
        This writes to both RAM areas to ensure consistent partial updates
        
        Args:
            buffer: Buffer to display (uses internal buffer if None)
        """
        # Reset display to clear any partial display settings
        self.reset()
        self.init_full_mode()
        
        if buffer is None:
            buffer = self.buffer
            
        w = (self.width + 7) // 8  # Width in bytes, ceiling division
        h = self.height
        
        self.send_command(WRITE_RAM)  # Write to RAM area 0x24
        for j in range(h):
            for i in range(w):
                self.send_data(buffer[i + j * w])
        
        # Display refresh with full update
        self.display_frame()
    
    def display_partial(self, x=0, y=0, w=None, h=None, buffer=None):
        """
        Perform a partial update of the display for a specific region
        
        Args:
            x: X position of region to update (must be multiple of 8)
            y: Y position of region to update
            w: Width of region to update (must be multiple of 8, defaults to full width)
            h: Height of region to update (defaults to full height)
            buffer: Buffer to display (uses internal buffer if None)
        """
        if buffer is None:
            buffer = self.buffer
            
        # Set defaults if not specified
        if w is None:
            w = self.width
        if h is None:
            h = self.height
            
        # Make sure x and width are multiples of 8
        x &= 0xF8  # Force to be multiple of 8
        w &= 0xF8  # Force to be multiple of 8
        
        # Calculate end positions
        x_end = min(x + w - 1, self.width - 1)
        y_end = min(y + h - 1, self.height - 1)
        
        # Initialize partial refresh mode
        self.init_partial_mode()
        
        # Set the area to update
        self.set_memory_area(x, y, x_end, y_end)
        self.set_memory_pointer(x, y)
        
        # Calculate buffer offsets and sizes
        bytes_per_line = (w + 7) // 8
        buffer_width = (self.width + 7) // 8
        
        # Send data for the specified region
        self.send_command(WRITE_RAM)
        for j in range(y, y_end + 1):
            for i in range(x // 8, (x_end // 8) + 1):
                # Get the data from the buffer
                # Adjust index based on full buffer width
                index = i + j * buffer_width
                self.send_data(buffer[index])
        
        # Partial display refresh
        self.display_partial_frame()
    
    def init_partial_mode(self):
        """Initialize the display for partial refresh mode"""
        # Reset display
        self.reset()
        
        # Set LUT for partial update
        self.set_lut(WF_PARTIAL_1IN54_0)
        
        # Additional settings for partial refresh
        self.send_command(0x37)
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
        
        self.send_command(DISPLAY_UPDATE_CONTROL_2)
        self.send_data(0xC0)
        self.send_command(MASTER_ACTIVATION)
        self.wait_until_idle()
    
    def init_full_mode(self):
        """Initialize the display for full refresh mode"""
        # Reset display
        self.reset()
        
        # Set LUT for full update
        self.set_lut(WF_FULL_1IN54)
        
        self.send_command(0x3C)
        self.send_data(0x80)
        
        self.send_command(DISPLAY_UPDATE_CONTROL_2)
        self.send_data(0xC7)  # Option for LUT from register - full refresh
        self.send_command(MASTER_ACTIVATION)
        self.wait_until_idle()
    
    def set_memory_area(self, x_start, y_start, x_end, y_end):
        """
        Set the memory area for data read/write
        
        Args:
            x_start: X start position
            y_start: Y start position
            x_end: X end position
            y_end: Y end position
        """
        self.send_command(SET_RAM_X_ADDRESS_START_END_POSITION)
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x_start >> 3) & 0xFF)
        self.send_data((x_end >> 3) & 0xFF)
        
        self.send_command(SET_RAM_Y_ADDRESS_START_END_POSITION)
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)
    
    def set_memory_pointer(self, x, y):
        """
        Set the memory pointer for data read/write
        
        Args:
            x: X position
            y: Y position
        """
        self.send_command(SET_RAM_X_ADDRESS_COUNTER)
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x >> 3) & 0xFF)
        
        self.send_command(SET_RAM_Y_ADDRESS_COUNTER)
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)
        
        self.wait_until_idle()
    
    def display_frame(self):
        """Update the display (full refresh)"""
        self.send_command(DISPLAY_UPDATE_CONTROL_2)
        self.send_data(0xC7)
        self.send_command(MASTER_ACTIVATION)
        self.wait_until_idle()
    
    def display_partial_frame(self):
        """
        Update the display using partial refresh mode
        This is faster but may cause some ghosting over time
        """
        self.send_command(DISPLAY_UPDATE_CONTROL_2)
        self.send_data(0xCF)  # Option for LUT from register - partial refresh
        self.send_command(MASTER_ACTIVATION)
        self.wait_until_idle()
    
    def set_frame_memory(self, image_buffer, x, y, image_width, image_height):
        """
        Set frame memory with an image buffer
        
        Args:
            image_buffer: Image buffer
            x: X position
            y: Y position
            image_width: Width of image
            image_height: Height of image
        """
        if (image_buffer is None or 
                x < 0 or image_width < 0 or
                y < 0 or image_height < 0):
            return
            
        # Reset display
        self.rst.value(0)  # Module reset
        utime.sleep_ms(2)
        self.rst.value(1)
        utime.sleep_ms(2)
        
        self.send_command(0x3C)
        self.send_data(0x80)
        
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        x &= 0xF8
        image_width &= 0xF8
        
        if x + image_width >= self.width:
            x_end = self.width - 1
        else:
            x_end = x + image_width - 1
            
        if y + image_height >= self.height:
            y_end = self.height - 1
        else:
            y_end = y + image_height - 1
            
        self.set_memory_area(x, y, x_end, y_end)
        self.set_memory_pointer(x, y)
        
        self.send_command(WRITE_RAM)
        # Send the image data
        for j in range(y_end - y + 1):
            for i in range((x_end - x + 1) // 8):
                self.send_data(image_buffer[i + j * (image_width // 8)])
    
    def set_frame_memory_partial(self, image_buffer, x, y, image_width, image_height):
        """
        Set frame memory with an image buffer for partial refresh
        This function updates a specific region with the provided image_buffer
        
        Args:
            image_buffer: Image buffer containing the region to update
            x: X position (must be multiple of 8)
            y: Y position
            image_width: Width of image (must be multiple of 8)
            image_height: Height of image
        """
        if (image_buffer is None or 
                x < 0 or image_width < 0 or
                y < 0 or image_height < 0):
            return
            
        # Initialize partial refresh mode
        self.init_partial_mode()
        
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        x &= 0xF8
        image_width &= 0xF8
        
        if x + image_width >= self.width:
            x_end = self.width - 1
        else:
            x_end = x + image_width - 1
            
        if y + image_height >= self.height:
            y_end = self.height - 1
        else:
            y_end = y + image_height - 1
            
        self.set_memory_area(x, y, x_end, y_end)
        self.set_memory_pointer(x, y)
        
        self.send_command(WRITE_RAM)
        # Send the image data
        bytes_per_line = image_width // 8
        for j in range(y_end - y + 1):
            for i in range((x_end - x + 1) // 8):
                self.send_data(image_buffer[i + j * bytes_per_line])
    
    def sleep(self):
        """Put display into deep sleep mode to save power"""
        self.send_command(DEEP_SLEEP_MODE)
        self.send_data(0x01)
        utime.sleep_ms(200)
        
        # Pull reset pin low to ensure sleep mode
        self.rst.value(0)
    
    # Framebuffer methods for easy drawing
    def fill(self, color):
        """Fill the entire buffer with a color (0=black, 1=white)"""
        self.framebuf.fill(color)
    
    def pixel(self, x, y, color):
        """Set a pixel color (0=black, 1=white)"""
        self.framebuf.pixel(x, y, color)
    
    def hline(self, x, y, w, color):
        """Draw a horizontal line"""
        self.framebuf.hline(x, y, w, color)
    
    def vline(self, x, y, h, color):
        """Draw a vertical line"""
        self.framebuf.vline(x, y, h, color)
    
    def line(self, x1, y1, x2, y2, color):
        """Draw a line"""
        self.framebuf.line(x1, y1, x2, y2, color)
    
    def rect(self, x, y, w, h, color):
        """Draw a rectangle"""
        self.framebuf.rect(x, y, w, h, color)
    
    def fill_rect(self, x, y, w, h, color):
        """Draw a filled rectangle"""
        self.framebuf.fill_rect(x, y, w, h, color)
    
    def text(self, text, x, y, color=0):
        """Draw text"""
        self.framebuf.text(text, x, y, color)

    def text_scaled(self, text, x, y, scale=1, color=0):
        """Draw scaled text using the built-in font as a bitmap and expanding pixels.

        This creates a temporary small framebuffer for each input line (8px tall) and scales
        each pixel up by `scale` into the main framebuffer. Works with multiple lines (`\n`).
        """
        if scale <= 1:
            # simple pass-through
            self.text(text, x, y, color)
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
                        self.fill_rect(dst_x, dst_y, scale, scale, color)

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

        chosen_scale = 1
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
            y = (self.height - total_height) // 2
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