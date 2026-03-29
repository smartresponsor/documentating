REM --- Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp ---
@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM --- Resolve repo dir: prefer git root, else cmd location ---
set "REPO_DIR="
for /f "usebackq delims=" %%R in (`git rev-parse --show-toplevel 2^>nul`) do set "REPO_DIR=%%R"
if not defined REPO_DIR (
  for %%I in ("%~dp0..") do set "REPO_DIR=%%~fI"
)
for %%I in ("%REPO_DIR%") do set "REPO_NAME=%%~nI"

REM --- Where the menu script is (relative to repo root) ---
set "COMMANDING_SH=.commanding/commanding.sh"

REM --- Detect Windows Terminal ---
set "WT=0"
where wt.exe >nul 2>nul && set "WT=1"

REM --- Detect Git Bash (preferred) ---
set "BASH="
for %%P in (
  "%ProgramFiles%\Git\bin\bash.exe"
  "%ProgramFiles%\Git\usr\bin\bash.exe"
  "%ProgramW6432%\Git\bin\bash.exe"
  "%ProgramW6432%\Git\usr\bin\bash.exe"
  "%LocalAppData%\Programs\Git\bin\bash.exe"
  "%LocalAppData%\Programs\Git\usr\bin\bash.exe"
) do (
  if not defined BASH if exist "%%~P" set "BASH=%%~P"
)

REM --- Detect WSL fallback ---
set "WSL=0"
where wsl.exe >nul 2>nul && set "WSL=1"

REM --- Command inside bash: run menu if present; keep interactive ---
set "BASH_CMD=cd \"%REPO_DIR%\"; if [ -f %COMMANDING_SH% ]; then exec bash -i %COMMANDING_SH%; else exec bash -i; fi"

REM =========================
REM 1) Git Bash found
REM =========================
if defined BASH (
  if "%WT%"=="1" (
    wt -w 0 new-tab --title "%REPO_NAME%" -d "%REPO_DIR%" -- "%BASH%" -lc "%BASH_CMD%"
    exit /b 0
  ) else (
    start "" /D "%REPO_DIR%" "%BASH%" -lc "%BASH_CMD%"
    exit /b 0
  )
)

REM =========================
REM 2) WSL fallback
REM =========================
if "%WSL%"=="1" (
  if "%WT%"=="1" (
    wt -w 0 new-tab --title "%REPO_NAME%" wsl.exe -- bash -lc "cd \"$(wslpath -a '%REPO_DIR%')\"; %BASH_CMD%"
    exit /b 0
  ) else (
    start "" wsl.exe -- bash -lc "cd \"$(wslpath -a '%REPO_DIR%')\"; %BASH_CMD%"
    exit /b 0
  )
)

echo ERROR: No terminal found.
echo Install Git for Windows (preferred) or enable WSL.
pause
exit /b 1
