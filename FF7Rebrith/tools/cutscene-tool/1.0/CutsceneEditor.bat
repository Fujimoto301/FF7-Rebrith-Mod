@echo off
setlocal enabledelayedexpansion
title FF7 Rebirth - Cutscene Editor
REM ===================================================================
REM  Starts the cutscene editor, running setup first if it has never run.
REM
REM  There are no paths in this file. Everything the tool needs is either
REM  found next to it, or recorded in config.json by firstrun.py. If a drive
REM  letter changes, delete config.json and run this again.
REM
REM  Needs Python 3.10-3.14. Nothing else; no Node, no server, no compiler.
REM
REM  Machines often have several Pythons and the newest is not always the one
REM  with pip, so rather than trusting "py -3" this looks for an interpreter
REM  that already has what we need, then for one that can install it, and only
REM  then gives up.
REM ===================================================================

set "TOOLDIR=%~dp0"
set "CONFIG=%TOOLDIR%config.json"
set "REQS=%TOOLDIR%requirements.txt"

REM  Newest first. PySide6 publishes an abi3 wheel for 3.10 through 3.14.
set "CANDIDATES=3.13 3.12 3.11 3.14 3.10"

set "PY="
set "NEEDPIP="

REM ---- 1. an interpreter that already has the toolkit ----------------
for %%V in (%CANDIDATES%) do (
  if not defined PY (
    py -%%V -c "import PySide6, numpy" >nul 2>&1 && set "PY=py -%%V"
  )
)
if not defined PY py -3 -c "import PySide6, numpy" >nul 2>&1 && set "PY=py -3"
if not defined PY python -c "import PySide6, numpy" >nul 2>&1 && set "PY=python"
if defined PY goto :checkdeps

REM ---- 2. one that has pip, so it can install them -------------------
for %%V in (%CANDIDATES%) do (
  if not defined PY (
    py -%%V -m pip --version >nul 2>&1 && set "PY=py -%%V"
  )
)
if not defined PY py -3 -m pip --version >nul 2>&1 && set "PY=py -3"
if not defined PY python -m pip --version >nul 2>&1 && set "PY=python"
if defined PY goto :install

REM ---- 3. any Python at all; pip can usually be bootstrapped ---------
for %%V in (%CANDIDATES%) do (
  if not defined PY (
    py -%%V --version >nul 2>&1 && set "PY=py -%%V"
  )
)
if not defined PY py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY python --version >nul 2>&1 && set "PY=python"
if not defined PY goto :nopython
set "NEEDPIP=1"
goto :install

REM ===================================================================
:nopython
echo.
echo   No Python found.
echo   Install 3.10 or newer from https://www.python.org/downloads/
echo   and tick "Add python.exe to PATH".
echo.
pause & exit /b 1

REM ===================================================================
:checkdeps
REM  The toolkit is there, but the asset-reading libraries may not be.
REM  Note the import names, not the pip names: pycryptodome imports as Crypto
REM  and pyUsmap as Usmap, so probing the pip name would always "fail" and
REM  reinstall on every launch.
!PY! -c "import Crypto, lz4, Usmap, PIL" >nul 2>&1
if errorlevel 1 goto :install
goto :ready

REM ===================================================================
:install
echo.
for /f "delims=" %%A in ('!PY! -c "import sys;print(sys.version.split()[0])" 2^>nul') do set "PYVER=%%A"
echo   Using Python !PYVER!  ^(!PY!^)
echo.
echo   Some Python packages are missing. They are listed in
echo   requirements.txt - PySide6 for the window, numpy for audio mixing,
echo   and four small libraries for reading the game's assets.
echo.
echo   About 100 MB from PyPI, all open source.
echo.
set "ANSWER=y"
set /p "ANSWER=  Install them now? [Y/n] "
if /i "!ANSWER!"=="n" goto :declined

if defined NEEDPIP (
  echo.
  echo   That Python has no pip. Bootstrapping it with ensurepip...
  !PY! -m ensurepip --upgrade --default-pip
  !PY! -m pip --version >nul 2>&1
  if errorlevel 1 goto :nopip
)

echo.
!PY! -m pip install --upgrade pip
!PY! -m pip install -r "%REQS%"
if errorlevel 1 goto :installfailed

!PY! -c "import PySide6, numpy, Crypto, lz4, Usmap, PIL" >nul 2>&1
if errorlevel 1 goto :installfailed
echo.
echo   Installed.
goto :ready

REM ===================================================================
:declined
echo.
echo   Nothing installed, so the editor cannot start.
echo.
pause & exit /b 1

REM ===================================================================
:nopip
echo.
echo   pip could not be bootstrapped for !PY! ^(Python !PYVER!^).
echo.
echo   Two ways out, either is fine:
echo     - Re-run the Python installer, choose Modify, and tick "pip".
echo     - Or install another Python 3.10-3.14 from python.org with pip
echo       included; this script prefers whichever one already works.
echo.
pause & exit /b 1

REM ===================================================================
:installfailed
echo.
echo   The install did not finish on Python !PYVER!.
echo.
echo   If pip said "no matching distribution", that Python is outside the
echo   range PySide6 publishes wheels for ^(3.10 to 3.14^). Installing
echo   Python 3.13 alongside it is the quickest fix - this script prefers
echo   whichever interpreter already works, so nothing else changes.
echo.
pause & exit /b 1

REM ===================================================================
:ready
REM  No config.json means setup has never completed. Run it, then carry on
REM  into the editor in the same session so it is one double-click, not two.
if not exist "%CONFIG%" (
  echo.
  echo   First run - setting up.
  echo.
  pushd "%TOOLDIR%"
  !PY! firstrun.py %*
  set "RC=!ERRORLEVEL!"
  popd
  if not "!RC!"=="0" (
    echo.
    echo   Setup did not finish. Nothing was saved, so running this again
    echo   starts over cleanly.
    echo.
    pause & exit /b !RC!
  )
  echo.
  echo   Setup finished. Starting the editor...
  echo.
)

pushd "%TOOLDIR%"
!PY! -m editor_qt %*
set "RC=!ERRORLEVEL!"
popd

if not "!RC!"=="0" (
  echo.
  echo  The editor exited with code !RC!.
  pause
)
endlocal
