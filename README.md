CLAUDE.md
该文件为使用 Claude Code（claude.ai/code）在本仓库中的代码工作提供了指导。

项目概述
一个Windows桌面应用程序，会生成浪漫的弹窗动画——对话框一个接一个地弹出，形成一个心形。使用用户的实际桌面作为背景。可以生成独立的.exe用于分发。

技术栈
Python 3.12+ with customtkinter， Pillow （PIL）， tkinter
PyInstaller for EXE 打包
仅限Windows（使用ctypes.windll进行DPI感知和屏幕指标）
跑步
# Run the config app (lets user set name, messages, preview, generate EXE)
python love_app.py

# Run the standalone version (hardcoded name/messages, no config UI)
python LoveCards_standalone.py
建筑EXE
pyinstaller --onefile --windowed --icon=heart.ico --name LoveCards --clean --noconfirm _gen_target.py
该文件由的“生成 EXE”按钮自动生成——它将用户的名称/消息嵌入独立模板中。_gen_target.pylove_app.py

建筑
love_app.py — 主要入口。 （CTk）用于用户输入，（CTkToplevel）用于心形动画。包含作为原始字符串的字面量，用于生成EXE源代码。ConfigWindowFullscreenDisplaySTANDALONE_TEMPLATE
LoveCards_standalone.py — 自包含版本，带有硬编码的 NAME/MSGS。作为参考;实际的EXE源码是从love_app.py模板生成的。
make_win_dialog（） — 渲染单一浪漫风格对话图像（PIL）。渐变正体，玫瑰金边框，装饰性点，居中文字。
_heart_points（） — 使用参数方程生成心形曲线坐标：， 。x=16sin³(t)y=13cos(t)-5cos(2t)-2cos(3t)-cos(4t)
_pre_render（） — 启动时预渲染所有对话图像，实现流畅动画。
关键定制点
dw = 300——对话宽度
self.after(120, self._animate)— 动画间隔（每对话的毫数秒）
font_body = ImageFont.truetype(FONT_PATH, 18)— 消息字体大小
t += 0.13在 —— 心点密度（较小=更多对话）_heart_points()
line_h = 28——对话正文中的行高
依赖关系
安装后再运行：

pip install customtkinter Pillow pyinstaller
注释
DPI 意识是在脚本开始时通过以下方式设置的ctypes.windll.shcore.SetProcessDpiAwareness(2)
屏幕尺寸是基于（不是 tkinter winfo）在不同 DPI 设置下的准确性GetSystemMetrics
支持中文字体需要Windows或msyh.ttcsimhei.ttf
这无害，可以忽略libpng warning: iCCP: known incorrect sRGB profile
前端设计技能可通过 UI 改进获得.claude/skills/frontend-design/
