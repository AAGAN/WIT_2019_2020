# Pure python implementation of MicroPython framebuf module.
# This is intended for boards with limited flash memory and the inability to
# use the native C version of the framebuf module.  This python module can be
# added to the board's file system to provide a functionally identical framebuf
# interface but at the expense of speed (this python version will be _much_
# slower than the C version).
# This is a direct port of the framebuf module C code to python:
#   https://github.com/micropython/micropython/blob/master/extmod/modframebuf.c
# Original file created by Damien P. George.
# Python port below created by Tony DiCola.


# Framebuf format constats:
MVLSB     = 0  # Single bit displays (like SSD1306 OLED)
RGB565    = 1  # 16-bit color displays
GS4_HMSB  = 2  # Unimplemented!


class MVLSBFormat:

    def setpixel(self, fb, x, y, color):
        index = (y >> 3) * fb.stride + x
        offset = y & 0x07
        fb.buf[index] = (fb.buf[index] & ~(0x01 << offset)) | ((color != 0) << offset)

    def getpixel(self, fb, x, y):
        index = (y >> 3) * fb.stride + x
        offset = y & 0x07
        return ((fb.buf[index] >> offset) & 0x01)

    def fill_rect(self, fb, x, y, width, height, color):
        while height > 0:
            index = (y >> 3) * fb.stride + x
            offset = y & 0x07
            for ww in range(width):
                fb.buf[index+ww] = (fb.buf[index+ww] & ~(0x01 << offset)) | ((color != 0) << offset)
            y += 1
            height -= 1


class RGB565Format:

    def setpixel(self, fb, x, y, color):
        index = (x + y * fb.stride) * 2
        fb.buf[index]   = (color >> 8) & 0xFF
        fb.buf[index+1] = color & 0xFF

    def getpixel(self, fb, x, y):
        index = (x + y * fb.stride) * 2
        return (fb.buf[index] << 8) | fb.buf[index+1]

    def fill_rect(self, fb, x, y, width, height, color):
        while height > 0:
            for ww in range(width):
                index = (ww + x + y * fb.stride) * 2
                fb.buf[index]   = (color >> 8) & 0xFF
                fb.buf[index+1] = color & 0xFF
            y += 1
            height -= 1


class FrameBuffer:

    def __init__(self, buf, width, height, buf_format=MVLSB, stride=None):
        self.buf = buf
        self.width = width
        self.height = height
        self.stride = stride
        if self.stride is None:
            self.stride = width
        if buf_format == MVLSB:
            self.format = MVLSBFormat()
        elif buf_format == RGB565:
            self.format = RGB565Format()
        else:
            raise ValueError('invalid format')

    def fill(self, color):
        self.format.fill_rect(self, 0, 0, self.width, self.height, color)

    def fill_rect(self, x, y, width, height, color):
        if width < 1 or height < 1 or (x+width) <= 0 or (y+height) <= 0 or y >= self.height or x >= self.width:
            return
        xend = min(self.width, x+width)
        yend = min(self.height, y+height)
        x = max(x, 0)
        y = max(y, 0)
        self.format.fill_rect(self, x, y, xend-x, yend-y, color)

    def pixel(self, x, y, color=None):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        if color is None:
            return self.format.getpixel(self, x, y)
        else:
            self.format.setpixel(self, x, y, color)

    def hline(self, x, y, width, color):
        self.fill_rect(x, y, width, 1, color)

    def vline(self, x, y, height, color):
        self.fill_rect(x, y, 1, height, color)

    def rect(self, x, y, width, height, color):
        self.fill_rect(x, y, width, 1, color)
        self.fill_rect(x, y+height, width, 1, color)
        self.fill_rect(self, x, y, 1, height, color)
        self.fill_rect(self, x+width, y, 1, height, color)

    def line(self, x0, y0, x1, y1, color):
        """Bresenham's line algorithm"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = -1 if x0 > x1 else 1
        sy = -1 if y0 > y1 else 1
        if dx > dy:
            err = dx / 2.0
            while x != x1:
                self.pixel(x,y,color)
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                self.pixel(x,y,1)
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        self.pixel(x,y,1)
    
    def blit(self):
        raise NotImplementedError()

    def scroll(self):
        raise NotImplementedError()

    def text(self):
        raise NotImplementedError()


class FrameBuffer1(FrameBuffer):
    pass
	
# MicroPython SSD1306 OLED driver, I2C and SPI interfaces

from micropython import const


# register definitions
SET_CONTRAST        = const(0x81)
SET_ENTIRE_ON       = const(0xa4)
SET_NORM_INV        = const(0xa6)
SET_DISP            = const(0xae)
SET_MEM_ADDR        = const(0x20)
SET_COL_ADDR        = const(0x21)
SET_PAGE_ADDR       = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP       = const(0xa0)
SET_MUX_RATIO       = const(0xa8)
SET_COM_OUT_DIR     = const(0xc0)
SET_DISP_OFFSET     = const(0xd3)
SET_COM_PIN_CFG     = const(0xda)
SET_DISP_CLK_DIV    = const(0xd5)
SET_PRECHARGE       = const(0xd9)
SET_VCOM_DESEL      = const(0xdb)
SET_CHARGE_PUMP     = const(0x8d)

# Subclassing FrameBuffer provides support for graphics primitives
# http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
class SSD1306(FrameBuffer):
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, 0)#MONO_VLSB)
        self.init_display()

    def init_display(self):
        for cmd in (
            SET_DISP | 0x00, # off
            # address setting
            SET_MEM_ADDR, 0x00, # horizontal
            # resolution and layout
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01, # column addr 127 mapped to SEG0
            SET_MUX_RATIO, self.height - 1,
            SET_COM_OUT_DIR | 0x08, # scan from COM[N] to COM0
            SET_DISP_OFFSET, 0x00,
            SET_COM_PIN_CFG, 0x02 if self.height == 32 else 0x12,
            # timing and driving scheme
            SET_DISP_CLK_DIV, 0x80,
            SET_PRECHARGE, 0x22 if self.external_vcc else 0xf1,
            SET_VCOM_DESEL, 0x30, # 0.83*Vcc
            # display
            SET_CONTRAST, 0xff, # maximum
            SET_ENTIRE_ON, # output follows RAM contents
            SET_NORM_INV, # not inverted
            # charge pump
            SET_CHARGE_PUMP, 0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01): # on
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)

    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def show(self):
        x0 = 0
        x1 = self.width - 1
        if self.width == 64:
            # displays with width of 64 pixels are shifted by 32
            x0 += 32
            x1 += 32
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)


class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3c, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        self.write_list = [b'\x40', None] # Co=0, D/C#=1
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80 # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.write_list[1] = buf
        self.i2c.writevto(self.addr, self.write_list)

import machine
i2c = machine.I2C(1, freq = 400000)
display = SSD1306_I2C(128,64,i2c)

display.fill(0)
display.show()
import time
display.fill(1)
display.show()
time.sleep(1)
display.fill(0)
display.show()
time.sleep(1)
display.hline(2,3,25,1)
display.vline(5,0,15,1)
display.fill_rect(5,5,100,20,1)
display.show()