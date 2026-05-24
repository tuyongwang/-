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

FONT_PATH = r"C:\Windows\Fonts\msyh.ttc"
if not os.path.exists(FONT_PATH):
    FONT_PATH = r"C:\Windows\Fonts\simhei.ttf"

font_title = ImageFont.truetype(FONT_PATH, 13)
font_body = ImageFont.truetype(FONT_PATH, 18)
font_btn = ImageFont.truetype(FONT_PATH, 12)


class ConfigWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Love Cards")
        self.geometry("420x520")
        self.resizable(False, False)

        ctk.CTkLabel(self, text="Love Cards", font=("Microsoft YaHei", 26, "bold")).pack(pady=(25, 15))

        ctk.CTkLabel(self, text="Name", font=("Microsoft YaHei", 14)).pack(anchor="w", padx=40)
        self.name_entry = ctk.CTkEntry(self, width=340, height=40, font=("Microsoft YaHei", 14), placeholder_text="e.g. Baby")
        self.name_entry.pack(pady=(0, 12))

        ctk.CTkLabel(self, text="Messages (one per line)", font=("Microsoft YaHei", 14)).pack(anchor="w", padx=40)
        self.msg_entry = ctk.CTkTextbox(self, width=340, height=140, font=("Microsoft YaHei", 14))
        self.msg_entry.pack(pady=(0, 20))
        self.msg_entry.insert("1.0", "I love you\nYou are my everything\nI miss you so much\nYou make me happy")

        ctk.CTkButton(self, text="Preview", width=160, height=42, font=("Microsoft YaHei", 15, "bold"),
                       command=self.preview).pack(side="left", padx=(40, 10))
        ctk.CTkButton(self, text="Generate EXE", width=160, height=42, font=("Microsoft YaHei", 15, "bold"),
                       fg_color="#0078d4", hover_color="#006cbe",
                       command=self.generate).pack(side="right", padx=(10, 40))

    def preview(self):
        name = self.name_entry.get().strip() or "Baby"
        raw = self.msg_entry.get("1.0", "end").strip()
        msgs = [m.strip() for m in raw.split("\n") if m.strip()]
        if not msgs:
            msgs = ["I love you"]
        self.withdraw()
        self.after(200, lambda: FullscreenDisplay(self, name, msgs))

    def generate(self):
        import subprocess, sys
        name = self.name_entry.get().strip() or "Baby"
        raw = self.msg_entry.get("1.0", "end").strip()
        msgs = [m.strip() for m in raw.split("\n") if m.strip()]
        if not msgs:
            msgs = ["I love you"]

        standalone_code = STANDALONE_TEMPLATE.replace("__NAME_PLACEHOLDER__", repr(name)).replace("__MSGS_PLACEHOLDER__", repr(msgs))

        gen_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_gen_target.py")
        with open(gen_script, "w", encoding="utf-8") as f:
            f.write(standalone_code)

        pyinstaller = os.path.join(os.path.dirname(sys.executable), "pyinstaller.exe")
        if not os.path.exists(pyinstaller):
            pyinstaller = "pyinstaller"

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "heart.ico")
        icon_arg = ["--icon", icon_path] if os.path.exists(icon_path) else []

        subprocess.Popen([
            pyinstaller, "--onefile", "--windowed", "--name", "LoveCards",
            "--clean", "--noconfirm", *icon_arg, gen_script
        ])


def capture_desktop():
    return ImageGrab.grab()


def make_win_dialog(w, title, msg):
    """Romantic style rectangular dialog with gradient and decorative details"""
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

    # Shadow with depth
    shadow = Image.new("RGBA", (w + 14, h + 14), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([6, 8, w + 4, h + 6], radius=12, fill=(180, 80, 100, 40))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    img.paste(shadow, (0, 0), shadow)

    draw = ImageDraw.Draw(img)

    # Outer border (rose gold)
    draw.rounded_rectangle([0, 0, w - 2, h - 2], radius=12, fill=(230, 170, 180))

    # Window body - gradient effect (top lighter, bottom slightly warmer)
    for y in range(2, h - 2):
        ratio = (y - 2) / (h - 4)
        r = int(255 - ratio * 6)
        g = int(248 - ratio * 10)
        b = int(250 - ratio * 8)
        draw.line([(2, y), (w - 4, y)], fill=(r, g, b))

    # Clip to rounded rect shape
    mask = Image.new("L", (w - 4, h - 4), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, w - 5, h - 5], radius=11, fill=255)
    body = img.crop((2, 2, w - 2, h - 2))
    body.putalpha(mask)
    img.paste(body, (2, 2), body)

    draw = ImageDraw.Draw(img)

    # Title bar with gradient (darker rose at top)
    for y in range(2, title_h):
        ratio = (y - 2) / (title_h - 2)
        r = int(255 - ratio * 15)
        g = int(210 - ratio * 20)
        b = int(220 - ratio * 15)
        draw.line([(2, y), (w - 4, y)], fill=(r, g, b))

    # Title bar bottom separator
    draw.line([(12, title_h - 1), (w - 14, title_h - 1)], fill=(240, 190, 200), width=1)

    # Decorative dots on title bar
    dot_y = (2 + title_h) // 2
    for i, c in enumerate([(255, 120, 140), (255, 180, 190), (255, 140, 160)]):
        dx = 14 + i * 14
        draw.ellipse([dx - 4, dot_y - 4, dx + 4, dot_y + 4], fill=c)

    # Title text (elegant, shifted right to avoid dots)
    draw.text((56, 11), title, fill=(160, 50, 80), font=font_title)

    # Message text (centered, with subtle line decoration)
    ty = title_h + 16
    for i, line in enumerate(lines):
        tw = font_body.getlength(line)
        tx = (w - tw) / 2
        draw.text((tx, ty + i * line_h), line, fill=(120, 45, 65), font=font_body)

    # Bottom decorative line
    draw.line([(w // 4, h - 14), (w * 3 // 4, h - 14)], fill=(255, 200, 210), width=1)

    return img


class FullscreenDisplay(ctk.CTkToplevel):
    def __init__(self, parent, name, msgs):
        super().__init__(parent)
        self.parent = parent
        self.name = name
        self.msgs = msgs
        self.anim_index = 0
        self._photo_images = []

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        user32 = ctypes.windll.user32
        self.sw = user32.GetSystemMetrics(0)
        self.sh = user32.GetSystemMetrics(1)
        self.geometry(f"{self.sw}x{self.sh}+0+0")

        desktop_img = capture_desktop().resize((self.sw, self.sh))
        self.bg_photo = ImageTk.PhotoImage(desktop_img)

        self.canvas = tk.Canvas(self, width=self.sw, height=self.sh, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)

        self.bind("<Escape>", lambda e: self.close())
        self.canvas.bind("<Button-1>", lambda e: self.close())
        self.focus_set()

        self.points = self._heart_points()
        self._pre_render()
        self._animate()

    def _heart_points(self):
        pts = []
        cx, cy = self.sw / 2, self.sh / 2 - 30
        scale = min(self.sw, self.sh) / 28
        t = 0.0
        while t < 2 * math.pi:
            sx = 16 * math.sin(t) ** 3
            sy = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
            pts.append((cx + sx * scale, cy - sy * scale))
            t += 0.08
        return pts

    def _pre_render(self):
        dw = 300
        for i, (x, y) in enumerate(self.points):
            msg = self.msgs[i % len(self.msgs)]
            dialog_img = make_win_dialog(dw, self.name, msg)
            photo = ImageTk.PhotoImage(dialog_img)
            self._photo_images.append((x, y, photo))

    def _animate(self):
        if self.anim_index >= len(self._photo_images):
            return
        x, y, photo = self._photo_images[self.anim_index]
        self.canvas.create_image(x, y, anchor="center", image=photo)
        self.anim_index += 1
        self.after(130, self._animate)

    def close(self):
        self.destroy()
        self.parent.deiconify()


STANDALONE_TEMPLATE = r'''
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

NAME = __NAME_PLACEHOLDER__
MSGS = __MSGS_PLACEHOLDER__

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
        self._pre_render()
        self._animate()

    def _heart_points(self):
        pts = []
        cx, cy = self.sw / 2, self.sh / 2 - 30
        scale = min(self.sw, self.sh) / 28
        t = 0.0
        while t < 2 * math.pi:
            sx = 16 * math.sin(t) ** 3
            sy = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
            pts.append((cx + sx * scale, cy - sy * scale))
            t += 0.08
        return pts

    def _pre_render(self):
        dw = 300
        for i, (x, y) in enumerate(self.points):
            msg = MSGS[i % len(MSGS)]
            dialog_img = make_win_dialog(dw, NAME, msg)
            photo = ImageTk.PhotoImage(dialog_img)
            self._photos.append((x, y, photo))

    def _animate(self):
        if self.anim_index >= len(self._photos):
            return
        x, y, photo = self._photos[self.anim_index]
        self.canvas.create_image(x, y, anchor="center", image=photo)
        self.anim_index += 1
        self.after(130, self._animate)


if __name__ == "__main__":
    app = App()
    app.mainloop()
'''

if __name__ == "__main__":
    app = ConfigWindow()
    app.mainloop()
