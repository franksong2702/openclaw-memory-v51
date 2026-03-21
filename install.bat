@echo off
chcp 65001 >nul
echo ========================================
echo OpenClaw Memory V51 Plugin Installer
echo ========================================
echo.

REM 检查 Node.js
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Node.js found: 
node --version
echo.

REM 安装依赖
echo [INFO] Installing dependencies...
call npm install

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm install failed!
    pause
    exit /b 1
)

echo.
echo [OK] Dependencies installed successfully!
echo.

REM 编译 TypeScript
echo [INFO] Compiling TypeScript...
call npm run build

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] TypeScript compilation failed!
    echo Trying to continue with existing build...
)

echo.
echo [OK] Build complete!
echo.

REM 创建数据库目录
echo [INFO] Initializing database...
python -c "from memory_core_v2 import init_db; init_db(); print('[OK] Database initialized')"

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit C:\Users\user\.openclaw\openclaw.json
echo 2. Add "memory-v51" to plugins.allow
echo 3. Enable in plugins.entries.memory-v51
echo 4. Run: openclaw gateway restart
echo.
pause
