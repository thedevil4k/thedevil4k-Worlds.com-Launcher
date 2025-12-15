![Python](https://img.shields.io/badge/language-Python-yellow.svg)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)

# thedevil4k Worlds.com Launcher
## Introduction

**thedevil4k Worlds.com Launcher** is an advanced configuration utility for the Worlds.com game client. This program provides a graphical user interface (GUI) to centrally and easily manage multiple game configurations that would otherwise require manual editing of `.ini` files.

The launcher is capable of detecting the game version (legacy with `run.exe` or modern with `WorldsPlayer.exe`) and intelligently applies all settings.

## Key Features

### Server Management
* **Server Selection**: Easily switch between different community servers (e.g., LibreWorlds, Official, Worlio).
* **Advanced Update Options**: Configure the update servers (`upgradeServer` and `scriptServer`).
* **Integrated Server Editor**:
    * **Add New Server**: An intuitive form to add new server configurations.
    * Information is saved to the `worldsserverselection.json` file for full customization.
* **External Configuration**: The server list is managed via a `worldsserverselection.json` file, which is created automatically if it doesn't exist.

### Configuration Tools (TOOLS)
A dedicated column with toggles to quickly enable or disable various `worlds.ini` options, each with a visual status indicator (green/red):

* `MULTIRUN`: Allows running multiple instances of the game.
* `CHATBOX`: Toggles the classic chatbox on or off.
* `SHAPER`: Enables or disables the "Shaper".
* `PERMIT ANY AVATARS`: Controls the `permitAnyAvatar` variable.
* `ALLOW OBSCENITIES`: Controls the `allowObscenities` variable.
* **Max Players View**: A numeric field to adjust the `avatars=` value (from 1 to 256).

### Additional Utilities
* **Cache Cleaner**: A button to safely delete all contents of the `cachedir` folder.
* **Default File Creator**: Buttons to generate generic `worlds.ini` and `override.ini` files.
* **Smart Detection**:
    * Automatically detects the active server configuration on startup.
    * Detects the game version (`run.exe` vs. `WorldsPlayer.exe`).
    * Displays the status of the configuration files (`worlds.ini`, `override.ini`) in the interface.

## Screenshots
<img width="1449" height="684" alt="image" src="https://github.com/user-attachments/assets/cc8c9171-e530-4b12-afbc-6e3faa23c143" />

## Technologies Used

* **Python**: Core programming language.
* **Tkinter**: Library for the graphical user interface.
* **Pillow**: For image handling.
* **PyInstaller**: To create the final executable.

## Installation and Usage

1.  **Download** the latest version from the [Releases page](https://github.com/thedevil4k/thedevil4k-Worlds.com-Launcher/releases).
2.  **Place** the `thedevil4k Launcher.exe` file in your main Worlds.com installation folder, alongside `worlds.ini`, `override.ini`, and the game executable (`run.exe` or `WorldsPlayer.exe`).
3.  **Run** `thedevil4k Launcher.exe`.
    * **Note**: The program requires **administrator privileges** to be able to launch the game executable.
4.  On the first run, if `worldsserverselection.json` is not found, it will be created automatically with a default configuration.
5.  Use the controls to adjust your settings and press **PLAY**.

## 🚀 Compiling from Source with PyInstaller

If you want to compile the launcher from the source code yourself, you will need **PyInstaller**.

### Prerequisites

Before compiling, make sure you have the necessary tools installed. You can install the required packages using pip:

```bash
pip install pyinstaller Pillow

pyinstaller --noconfirm --onefile --windowed --uac-admin --icon="worldsserverselection.ico" --add-data="serverselectionbackground2.png;." --add-data="worldsserverselection.ico;." --add-data="worldsserverselection.json;." --add-data="themes;themes" --add-data="screenshots;screenshots" --add-data="files.txt;." --add-data="theme_icon.ico;." --collect-all customtkinter launcher.py

## License

This project is licensed under the GPLv3 License. You can fork and improve that.

* **Project Direction & Design**: thedevil4k
* **Code Generation & Engineering**: Gemini
