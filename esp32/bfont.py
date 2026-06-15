import struct

class BinaryFont:
    def __init__(self, path):
        self._f = open(path, 'rb')
        self._f.read(4)
        self._height, self._bpr, self._num = struct.unpack('<HHI', self._f.read(8))
        self._entry_size = 1 + self._height * self._bpr
        self._index_start = 12
        self._data_start = 12 + self._num * 4

    def height(self):
        return self._height

    def _find(self, cp):
        lo, hi = 0, self._num - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            self._f.seek(self._index_start + mid * 4)
            c = struct.unpack('<I', self._f.read(4))[0]
            if c == cp:
                return mid
            elif c < cp:
                lo = mid + 1
            else:
                hi = mid - 1
        return -1

    def draw_char(self, oled, x, y, char):
        i = self._find(ord(char))
        if i < 0:
            return 6
        self._f.seek(self._data_start + i * self._entry_size)
        width = struct.unpack('<B', self._f.read(1))[0]
        bitmap = self._f.read(self._height * self._bpr)
        for row in range(self._height):
            for col in range(width):
                if bitmap[row * self._bpr + (col >> 3)] & (0x80 >> (col & 7)):
                    oled.pixel(x + col, y + row, 1)
        return width

    def draw_string(self, oled, x, y, text):
        for char in text:
            x += self.draw_char(oled, x, y, char)
            if x >= 128:
                break
