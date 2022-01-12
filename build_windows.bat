@echo off
if not exist build\ (
    mkdir build
)
if exist main.build\ (
    rmdir /s /q main.build
)
if exist main.dist\ (
    rmdir /s /q main.dist\
)
if exist build\Arcade_windows\ (
    rmdir /s /q build\Arcade_windows
)
echo Generating excecutable
python -m nuitka --quiet --standalone --python-flag=no_site --windows-disable-console src\main.py
echo Moving lib and data files
xcopy /E /I /Q libs main.dist
xcopy /E /I /Q src\data main.dist\data
xcopy /E /I /Q src\sounds main.dist\sounds
:: We nuke player saves, if any, by hand.
:: If it turns out we have more than one file to exclude, we'll replace it with xcopy
if exist main.dist\data\save.json (
    del /Q main.dist\data\save.json
)
rename main.dist\main.exe Arcade.exe
move main.dist build\Arcade_windows
echo Done