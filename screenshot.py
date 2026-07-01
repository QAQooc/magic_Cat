# -*- coding: utf-8 -*-
"""
截图模块
使用PowerShell截取全屏
"""
import os
import subprocess
import tempfile

TEMP_DIR = os.path.dirname(__file__)


def take_screenshot():
    """使用PowerShell截取全屏，返回截图路径"""
    temp_path = os.path.join(TEMP_DIR, "temp_screenshot.png")

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
    return temp_path
