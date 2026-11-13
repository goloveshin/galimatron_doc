# exports every drawio/*.drawio to source/images/*.svg
# the .drawio files are the source, the .svg files are generated
#
# usage: powershell -File export_drawio.ps1 [-DrawioExe "C:\Program Files\draw.io\draw.io.exe"]

param(
    [string]$DrawioExe = 'C:\Program Files\draw.io\draw.io.exe'
)

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceDir = Join-Path $here 'drawio'
$imagesDir = Join-Path $here 'source\images'

New-Item -ItemType Directory -Force $imagesDir | Out-Null

foreach ($file in Get-ChildItem -Path $sourceDir -Filter '*.drawio')
{
    $target = Join-Path $imagesDir ($file.BaseName + '.svg')
    & $DrawioExe -x -f svg -b 10 -o $target $file.FullName
}
