pyinstaller ^
 --noconfirm ^
 --onefile ^
 --windowed ^
 --uac-admin ^
 --icon="worldsserverselection.ico" ^
 --add-data="serverselectionbackground2.png;." ^
 --add-data="worldsserverselection.ico;." ^
 --add-data="worldsserverselection.json;." ^
 --add-data="themes;themes" ^
 --add-data="screenshots;screenshots" ^
 --add-data="files.txt;." ^
 --add-data="theme_icon.ico;." ^
 --collect-all customtkinter ^
 launcher.py
