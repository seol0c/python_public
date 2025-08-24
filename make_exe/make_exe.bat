@echo off
setlocal

:: 드롭된 .py 파일의 전체 경로 및 이름 분리
set "PYFILE=%~1"
set "PYPATH=%~dp1"
set "EXENAME=%~n1.exe"

:: 외부 실행 아이콘: bat과 같은 폴더의 exeico.ico
set "EXEICON=%~dp0exeico.ico"

:: 내부 GUI 아이콘: py와 같은 폴더에 있는 {이름}ico.ico
set "GUIICON=%PYPATH%%~n1ico.ico"

:: .exe 생성 (내부 아이콘 파일이 없으면 기본 아이콘 적용)
if exist "%GUIICON%" (
    pyinstaller --onefile --windowed --clean --icon "%EXEICON%" --add-data "%GUIICON%;." "%PYFILE%"
) else (
    pyinstaller --onefile --windowed --clean --icon "%EXEICON%" "%PYFILE%"
)

:: dist 폴더에서 바탕화면으로 복사
copy /y "dist\%EXENAME%" "%USERPROFILE%\Desktop\%EXENAME%" >nul

:: 빌드 찌꺼기 정리
rd /s /q build
rd /s /q dist
del "%~n1.spec" 2>nul

:: 완료 안내
echo.
echo ===== .exe build complete =====
pause
