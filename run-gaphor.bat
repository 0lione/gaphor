rem Startup script for Gaphor on Windows
rem
rem You should check if the directory where the win32 libraries are
rem found is correct, as well as the place where Python is installed.
rem
rem

rem This is where you installed the Gaphor-win32-libs package.

set GAPHOR_WIN32_LIBS=gaphor-win32-libs

rem Where is Python installed?

set PYTHONHOME=c:\Python23

rem Should have to change these:

set PATH=%GAPHOR_WIN32_LIBS%\bin;%PYTHONHOME%;%PATH%

set PYTHONPATH=%GAPHOR_WIN32_LIBS%\lib\python23

python setup.py run %1 %2 %3 %4
