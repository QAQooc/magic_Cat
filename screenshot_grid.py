import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

TEMP_DIR = os.path.dirname(__file__)

def take_screenshot_with_grid():
    """截图并画坐标网格，返回截图路径"""
    temp_path = os.path.join(TEMP_DIR, "temp_screenshot.png")
    grid_path = os.path.join(TEMP_DIR, "temp_screenshot_grid.png")

    # 截图
    ps_cmd = '''
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    $screen = [System.Windows.Forms.Screen]::PrimaryScreen
    $bitmap = New-Object System.Drawing.Bitmap($screen.Bounds.Width, $screen.Bounds.Height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.CopyFromScreen($screen.Bounds.Location, [System.Drawing.Point]::Empty, $screen.Bounds.Size)
    $bitmap.Save("{path}")
    $graphics.Dispose()
    $bitmap.Dispose()
    '''.format(path=temp_path.replace('\\', '\\\\'))

    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = subprocess.SW_HIDE

    subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, startupinfo=si)

    # 画网格
    img = Image.open(temp_path)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    w, h = img.size

    # 画竖线和横线（每100像素）
    for x in range(0, w, 100):
        draw.line([(x, 0), (x, h)], fill='red', width=1)
        draw.text((x + 2, 2), str(x), fill='red', font=font)
    for y in range(0, h, 100):
        draw.line([(0, y), (w, y)], fill='red', width=1)
        draw.text((2, y + 2), str(y), fill='red', font=font)

    img.save(grid_path)
    return grid_path

if __name__ == "__main__":
    path = take_screenshot_with_grid()
    print(f"Grid screenshot saved: {path}")