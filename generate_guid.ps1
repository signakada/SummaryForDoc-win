# GUIDを生成してクリップボードにコピーするスクリプト

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "GUID生成スクリプト" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# GUIDを生成
$guid = [System.Guid]::NewGuid().ToString().ToUpper()

Write-Host "生成されたGUID:" -ForegroundColor Green
Write-Host $guid -ForegroundColor Yellow
Write-Host ""

# クリップボードにコピー
$guid | Set-Clipboard

Write-Host "GUIDをクリップボードにコピーしました！" -ForegroundColor Green
Write-Host ""
Write-Host "installer.issファイルを開いて、以下の部分に貼り付けてください：" -ForegroundColor White
Write-Host "AppId={{" -NoNewline -ForegroundColor Gray
Write-Host "YOUR-GUID-HERE" -NoNewline -ForegroundColor Red
Write-Host "}" -ForegroundColor Gray
Write-Host "↓"
Write-Host "AppId={{" -NoNewline -ForegroundColor Gray
Write-Host "$guid" -NoNewline -ForegroundColor Green
Write-Host "}" -ForegroundColor Gray
Write-Host ""

Read-Host "Enterキーを押して終了..."
