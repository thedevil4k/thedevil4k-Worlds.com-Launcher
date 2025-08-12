thedevil4k Worlds.com Launcher
Introduction
thedevil4k Worlds.com Launcher is an advanced configuration utility for the Worlds.com game client. This program provides a graphical user interface (GUI) to easily and centrally manage multiple game settings that would otherwise require manual editing of .ini files.

The launcher is capable of detecting the game version (legacy with run.exe or modern with WorldsPlayer.exe) and intelligently applies configurations, respecting the file structure of worlds.ini and override.ini.

Key Features
Server Management
Server Selection: Allows switching between different community servers (e.g., LibreWorlds, Official, Worlio) by modifying the worlds.ini and override.ini files.

Advanced Updating Server Options: In a collapsible panel, allows configuring the update servers (upgradeServer and scriptServer), with options to make no changes (Nothing) or to remove the lines entirely (Remove).

Integrated Server Editor:

Add New Server: A button opens a form to add new server configurations directly from the launcher.

The information is saved to the worldsserverselection.json file, allowing for full customization.

External Configuration: The entire server list is managed via a worldsserverselection.json file, which the launcher can create automatically if it is missing.

Configuration Tools (TOOLS)
A dedicated column with toggles to quickly enable or disable various worlds.ini options, each with a visual status indicator (green/red):

MULTIRUN: Allows running multiple instances of the game.

CHATBOX: Toggles the classic chatbox.

SHAPER: Toggles the "Shaper" (inverted logic: green if disableshaper=0).

PERMIT ANY AVATARS: Controls the permitAnyAvatar setting.

ALLOW OBSCENITIES: Controls the allowObscenities setting.

Max Players View: A numeric input field to adjust the avatars= value (from 1 to 256).

Additional Utilities
Clean Cache: A button to safely delete all contents of the cachedir folder.

Create Default Files: Buttons to generate generic worlds.ini and override.ini files if the user has deleted or corrupted their own.

Intelligent Detection:

Automatically detects the active server configuration on startup.

Detects the game version (run.exe vs. WorldsPlayer.exe) and adjusts the file writing logic accordingly.

Displays the status of key files (worlds.ini, override.ini) in the interface.

User Interface
Custom GUI with a background image and application icon.

Organized, column-based layout with scrollbars that respond to the mouse wheel.

Robust interface that always starts, using visual indicators to report missing files instead of a startup error.

How to Use
Download the thedevil4k Launcher.exe file.

Place the .exe in your main Worlds.com installation folder, alongside worlds.ini, override.ini, and the game executable (run.exe or WorldsPlayer.exe).

Run thedevil4k Launcher.exe.

Note: The program requires administrator privileges to be able to launch the game executable. Windows will ask for permission with a UAC prompt.

On the first run, if worldsserverselection.json is not found, it will be created automatically with a default configuration.

Use the controls to adjust your settings and press PLAY.

Building from Source
If you wish to modify the program and compile your own version, you will need the following:

Requirements
Python (version 3.8+ recommended).

The following Python libraries, which you can install with pip:

Bash

pip install Pillow pyinstaller
Build Command
Navigate with a terminal to the folder containing launcher.py and the asset files, and run the following command:

Bash

pyinstaller --onefile --windowed --uac-admin --add-data "serverselectionbackground.jpg;." --add-data "worldsserverselection.ico;." launcher.py
The final .exe will be located in the dist folder.

Credits
Project Direction & Design: thedevil4k

Code Generation & Engineering: Gemini Pro
