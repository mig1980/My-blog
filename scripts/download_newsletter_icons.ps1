# Newsletter Icon Downloader Script
# Downloads free PNG icons from Icons8 for the Quantum Investor newsletter

$iconsDir = "c:\Users\mgavril\Documents\GitHub\My-blog\Media\icons"

if (-not (Test-Path $iconsDir)) {
    New-Item -ItemType Directory -Path $iconsDir -Force | Out-Null
    Write-Host "Created icons directory: $iconsDir" -ForegroundColor Green
}

$icons = @{
    "storage.png" = "https://img.icons8.com/fluency/96/database.png"
    "industrial.png" = "https://img.icons8.com/fluency/96/factory.png"
    "tech.png" = "https://img.icons8.com/fluency/96/laptop.png"
    "trophy.png" = "https://img.icons8.com/fluency/96/trophy.png"
    "chart.png" = "https://img.icons8.com/fluency/96/line-chart.png"
    "trending-up.png" = "https://img.icons8.com/fluency/96/stocks-growth.png"
    "rocket.png" = "https://img.icons8.com/fluency/96/rocket.png"
    "sp500.png" = "https://img.icons8.com/fluency/96/stock-share.png"
    "bitcoin.png" = "https://img.icons8.com/fluency/96/bitcoin.png"
}

Write-Host ""
Write-Host "Downloading newsletter icons..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($icon in $icons.GetEnumerator()) {
    $fileName = $icon.Key
    $url = $icon.Value
    $outputPath = Join-Path $iconsDir $fileName

    try {
        Write-Host "  Downloading $fileName... " -NoNewline
        Invoke-WebRequest -Uri $url -OutFile $outputPath -UseBasicParsing -TimeoutSec 10

        if ((Test-Path $outputPath) -and ((Get-Item $outputPath).Length -gt 0)) {
            Write-Host "OK" -ForegroundColor Green
            $successCount++
        } else {
            throw "File empty"
        }
    } catch {
        Write-Host "FAILED: $_" -ForegroundColor Red
        $failCount++
    }
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Successful: $successCount" -ForegroundColor Green
Write-Host "Failed: $failCount" -ForegroundColor Red
Write-Host ""

if ($successCount -gt 0) {
    Write-Host "Icons saved to: $iconsDir" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Review downloaded icons in File Explorer"
    Write-Host "  2. Upload to: quantuminvestor.net/Media/icons/"
    Write-Host "  3. Test your newsletter"
    Write-Host ""
    Write-Host "Opening folder..." -ForegroundColor Yellow
    Start-Process explorer.exe $iconsDir
    Write-Host ""
    Write-Host "ATTRIBUTION REQUIRED:" -ForegroundColor Yellow
    Write-Host "  Add to newsletter footer: Icons by Icons8 (icons8.com)" -ForegroundColor Gray
    Write-Host "  Or purchase license: https://icons8.com/pricing" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
Write-Host ""
