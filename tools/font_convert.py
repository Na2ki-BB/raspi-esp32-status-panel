"""
jpfont.bin 生成スクリプト

事前準備:
1. font_to_py をインストール
     pip install font_to_py
2. IPA フォントを用意（例: ipaexg.ttf）
3. jpfont.py を生成
     font_to_py -x -f ipaexg.ttf 16 jpfont.py
4. 生成した jpfont.py をこのスクリプトと同じディレクトリに置く

実行:
    python3 tools/font_convert.py

出力: esp32/jpfont.bin
"""

import sys, struct, os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
import jpfont

chars = []
for i in range(0x20, 0x7F): chars.append(chr(i))
for i in range(0x3000, 0x3040): chars.append(chr(i))
for i in range(0x3040, 0x30A0): chars.append(chr(i))
for i in range(0x30A0, 0x3100): chars.append(chr(i))
for i in range(0x4E00, 0x6FFF): chars.append(chr(i))

height = jpfont.height()
bpr = (jpfont.max_width() + 7) // 8

entries = []
for char in chars:
    try:
        buf, h, w = jpfont.get_ch(char)
        if buf and len(buf) > 0:
            char_bpr = (w + 7) // 8
            padded = bytearray(height * bpr)
            for row in range(height):
                src = buf[row * char_bpr:(row + 1) * char_bpr]
                padded[row * bpr:row * bpr + char_bpr] = src
            entries.append((ord(char), w, bytes(padded)))
    except Exception:
        pass

entries.sort(key=lambda x: x[0])
num = len(entries)

output_path = os.path.join(script_dir, '..', 'esp32', 'jpfont.bin')
with open(output_path, 'wb') as f:
    f.write(b'JFT1')
    f.write(struct.pack('<HHI', height, bpr, num))
    for cp, w, _ in entries:
        f.write(struct.pack('<I', cp))
    for _, w, bitmap in entries:
        f.write(struct.pack('<B', w))
        f.write(bitmap)

print(f'完了: {num}文字')
print(f'出力: {os.path.abspath(output_path)}')
print(f'ファイルサイズ: {os.path.getsize(output_path) / 1024:.1f}KB')
