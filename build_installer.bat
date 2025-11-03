@echo off
chcp 65001 > nul
echo ====================================
echo SummaryForDoc インストーラービルドスクリプト
echo ====================================
echo.

:: Inno Setup Compilerのパスを確認
set ISCC_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if not exist %ISCC_PATH% (
    echo エラー: Inno Setup Compilerが見つかりません
    echo パス: %ISCC_PATH%
    echo.
    echo Inno Setupをインストールしてください
    echo https://jrsoftware.org/isinfo.php
    pause
    exit /b 1
)

:: distフォルダの存在確認
if not exist "dist\SummaryForDoc\SummaryForDoc.exe" (
    echo エラー: ビルドされたアプリケーションが見つかりません
    echo パス: dist\SummaryForDoc\SummaryForDoc.exe
    echo.
    echo 先にPyInstallerでアプリケーションをビルドしてください
    pause
    exit /b 1
)

echo ビルドされたファイルを確認しています...
echo.

:: installer.issファイルの存在確認
if not exist "installer.iss" (
    echo エラー: installer.issファイルが見つかりません
    pause
    exit /b 1
)

echo Inno Setupでコンパイルを開始します...
echo.

:: Inno Setup Compilerを実行
%ISCC_PATH% installer.iss

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ====================================
    echo インストーラーのビルドが完了しました！
    echo ====================================
    echo.
    echo 出力先: InnoSetupOutput\SummaryForDoc-Setup.exe
    echo.

    :: 出力フォルダを開く
    if exist "InnoSetupOutput\SummaryForDoc-Setup.exe" (
        explorer /select,"InnoSetupOutput\SummaryForDoc-Setup.exe"
    )
) else (
    echo.
    echo エラー: インストーラーのビルドに失敗しました
    echo エラーコード: %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

pause
