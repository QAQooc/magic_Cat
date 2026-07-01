Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$screen = [System.Windows.Forms.Screen]::PrimaryScreen
$bitmap = New-Object System.Drawing.Bitmap($screen.Bounds.Width, $screen.Bounds.Height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($screen.Bounds.Location, [System.Drawing.Point]::Empty, $screen.Bounds.Size)

# 画网格线（每100像素）
$pen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(100, 255, 0, 0), 1)
for ($x = 0; $x -lt $screen.Bounds.Width; $x += 100) {
    $graphics.DrawLine($pen, $x, 0, $x, $screen.Bounds.Height)
}
for ($y = 0; $y -lt $screen.Bounds.Height; $y += 100) {
    $graphics.DrawLine($pen, 0, $y, $screen.Bounds.Width, $y)
}

# 画坐标标签
$font = New-Object System.Drawing.Font("Arial", 10)
$brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Red)
for ($x = 0; $x -lt $screen.Bounds.Width; $x += 100) {
    for ($y = 0; $y -lt $screen.Bounds.Height; $y += 100) {
        $graphics.DrawString("$x,$y", $font, $brush, $x + 2, $y + 2)
    }
}

$bitmap.Save("$env:TEMP\temp_screenshot_grid.png")
$graphics.Dispose()
$bitmap.Dispose()
$pen.Dispose()
$font.Dispose()
$brush.Dispose()
Write-Host "Grid screenshot saved"