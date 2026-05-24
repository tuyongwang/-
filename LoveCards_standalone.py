import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageGrab, ImageTk, ImageDraw, ImageFilter, ImageFont
import math
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

NAME = "baby"
MSGS = ["I love you", "You are my everything", "I miss you so much", "You make me happy"]

FONT_PATH = r"C:\Windows\Fonts\msyh.ttc"
if not os.path.exists(FONT_PATH):
    FONT_PATH = r"C:\Windows\Fonts\simhei.ttf"

font_title = ImageFont.truetype(FONT_PATH, 13)
font_body = ImageFont.truetype(FONT_PATH, 18)


def capture_desktop():
    return ImageGrab.grab()


def make_win_dialog(w, title, msg):
    pad = 20
    title_h = 38
    text_w = w - pad * 2
    lines = []
    for paragraph in msg.split("\n"):
        line = ""
        for ch in paragraph:
            test = line + ch
            if font_body.getlength(test) > text_w:
                lines.append(line)
                line = ch
            else:
                line = test
        if line:
            lines.append(line)
    line_h = 28
    content_h = len(lines) * line_h + 40
    h = title_h + content_h
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (w + 14, h + 14), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([6, 8, w + 4, h + 6], radius=12, fill=(180, 80, 100, 40))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    img.paste(shadow, (0, 0), shadow)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, w - 2, h - 2], radius=12, fill=(230, 170, 180))
    for y in range(2, h - 2):
        ratio = (y - 2) / (h - 4)
        r = int(255 - ratio * 6)
        g = int(248 - ratio * 10)
        b = int(250 - ratio * 8)
        draw.line([(2, y), (w - 4, y)], fill=(r, g, b))
    mask = Image.new("L", (w - 4, h - 4), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, w - 5, h - 5], radius=11, fill=255)
    body = img.crop((2, 2, w - 2, h - 2))
    body.putalpha(mask)
    img.paste(body, (2, 2), body)
    draw = ImageDraw.Draw(img)
    for y in range(2, title_h):
        ratio = (y - 2) / (title_h - 2)
        r = int(255 - ratio * 15)
        g = int(210 - ratio * 20)
        b = int(220 - ratio * 15)
        draw.line([(2, y), (w - 4, y)], fill=(r, g, b))
    draw.line([(12, title_h - 1), (w - 14, title_h - 1)], fill=(240, 190, 200), width=1)
    dot_y = (2 + title_h) // 2
    for i, c in enumerate([(255, 120, 140), (255, 180, 190), (255, 140, 160)]):
        dx = 14 + i * 14
        draw.ellipse([dx - 4, dot_y - 4, dx + 4, dot_y + 4], fill=c)
    draw.text((56, 11), title, fill=(160, 50, 80), font=font_title)
    ty = title_h + 16
    for i, line in enumerate(lines):
        tw = font_body.getlength(line)
        tx = (w - tw) / 2
        draw.text((tx, ty + i * line_h), line, fill=(120, 45, 65), font=font_body)
    draw.line([(w // 4, h - 14), (w * 3 // 4, h - 14)], fill=(255, 200, 210), width=1)
    return img


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.anim_index = 0
        self._photos = []
        self.win = ctk.CTkToplevel(self)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        user32 = ctypes.windll.user32
        self.sw = user32.GetSystemMetrics(0)
        self.sh = user32.GetSystemMetrics(1)
        self.win.geometry(f"{self.sw}x{self.sh}+0+0")
        desktop = capture_desktop().resize((self.sw, self.sh))
        self.bg_photo = ImageTk.PhotoImage(desktop)
        self.canvas = tk.Canvas(self.win, width=self.sw, height=self.sh, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
        self.win.bind("<Escape>", lambda e: self.destroy())
        self.canvas.bind("<Button-1>", lambda e: self.destroy())
        self.win.focus_set()
        self.points = self._heart_points()
        self._animate()

    def _heart_points(self):
        pts = []
        cx, cy = self.sw / 2, self.sh / 2
        scale = min(self.sw, self.sh) / 28
        t = 0.0
        while t < 2 * math.pi:
            sx = 16 * math.sin(t) ** 3
            sy = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
            pts.append((cx + sx * scale, cy - sy * scale))
            t += 0.08
        return pts

    def _animate(self):
        if self.anim_index >= len(self.points):
            return
        x, y = self.points[self.anim_index]
        msg = MSGS[self.anim_index % len(MSGS)]
        dw = 300
        dialog_img = make_win_dialog(dw, NAME, msg)
        photo = ImageTk.PhotoImage(dialog_img)
        self._photos.append(photo)
        self.canvas.create_image(x, y, anchor="center", image=photo)
        self.anim_index += 1
        self.after(200, self._animate)


if __name__ == "__main__":
    app = App()
    app.mainloop()
