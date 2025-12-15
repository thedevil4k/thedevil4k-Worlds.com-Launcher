import customtkinter as ctk
from theme_selector_module import ThemeSelectorWindow
import tkinter as tk
from tkinter import messagebox
import os
import sys
import subprocess
import json
import shutil
from PIL import Image, ImageTk

# --- CustomTkinter Setup ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# --- Determine the base path for external files ---
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# --- SPECIAL FUNCTION FOR INTERNAL (PACKAGED) FILES ---
def resource_path(relative_path):
    """ Get the absolute path to a resource, works for development and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- 1. FILE CONFIGURATION ---
INI_FILE_NAME = 'worlds.ini'
OVERRIDE_FILE_NAME = 'override.ini'
EXECUTABLE_NAME = 'run.exe'
FALLBACK_EXECUTABLE_NAME = 'WorldsPlayer.exe'
ICON_NAME = 'worldsserverselection.ico'
BACKGROUND_IMAGE_NAME = 'serverselectionbackground2.png'
SERVER_CONFIG_FILE = 'worldsserverselection.json'

# --- 2. LOGIC FUNCTIONS ---
def create_default_override_ini():
    override_path = os.path.join(application_path, OVERRIDE_FILE_NAME)
    if os.path.isfile(override_path):
        response = messagebox.askyesno("Confirm Overwrite",
                                       f"An '{OVERRIDE_FILE_NAME}' file already exists. Are you sure you want to overwrite it with a default version?")
        if not response:
            return
    default_content = """[Install]
displayName=worlds

[Runtime]
WorldServer=worldserver://test.libreworlds.org:32147
noimpchange=1
infoOverride=http://us1.worlds.net/3DCDup
Register=regdown.pl
ProductName= thedevil4k Launcher
splashxover=140
splashyover=140
uiBackgroundRed=10
uiBackgroundGreen=10
uiBackgroundBlue=10

[Packages]
Package0=GroundZero.exe
Args0=
Title0=Ground Zero [Recommended]
Uninstall0=
PackageIsWorld0=1
"""
    try:
        with open(override_path, 'w') as f:
            f.write(default_content)
        messagebox.showinfo("Success", f"Default '{OVERRIDE_FILE_NAME}' has been created.")
        refresh_all_indicators()
    except Exception as e:
        messagebox.showerror("Error", f"Could not create '{OVERRIDE_FILE_NAME}'.\nError: {e}")

def create_default_worlds_ini():
    worlds_path = os.path.join(application_path, INI_FILE_NAME)
    if os.path.isfile(worlds_path):
        response = messagebox.askyesno("Confirm Overwrite",
                                       f"A '{INI_FILE_NAME}' file already exists. Are you sure you want to overwrite it with a default version?")
        if not response:
            return
    default_content = """[Gamma]
allowObscenities=1
CheckUpgrade=0
multirun=1
classicchatbox=1
disableshaper=0
permitAnyAvatar=1
usenetworkavatars=1
upgradeServer=http://upgrade.libreworlds.org/3DCDup
LogFile=Gamma.Log
Product_Name=WorldsPlayer
MIDIONSTART=0
RunUpgrade=
LastUpgradeCheck=20158
RestartAt=home:GroundZero/GroundZero.world#Reception<>@1228.0,2465.0,150.0,157.0,0.0,0.0,-1.0
ShaperLayout1920X1080=0 1 2 3 22 63 0
ShaperWindow1920X1080=676 328 568 424 2
LASTCHATNAME=VIP 
VIP=2
VIPAVATAR=avatar:bud.0ET3acT6aaT5aaT2aaT4acT9abPT1acGbagSEEE0T2acQ1T2adQ2T3adBcQ0bLT3aaMT1acOaRT4aaUT2aaVaIa0aJa0aKT5abQ0T4abQ1T5adQ2T4adWa0aXa0aYT7abQ0T6acQ1T7adQ2T6adZT1adNaGbingHT5cmaleaQ0DgT8cmaleaT7T6Q1fQ2f.rwg
CAM_MODE=1
CAM_SPEED=4
avatars=256
UserQueriedMusic=1
ShaperLayout1366X768=2 1 0 3 19 79 1
ShaperWindow1366X768=399 172 568 424 0
ShaperLayout1536X864=2 1 0 3 14 75 0
ShaperWindow1536X864=-8 -8 1552 840 0
AUTOPLAYCD=0
DISABLEIE=0
[InstalledWorlds]
MaxInstalledWorlds=49

[test.libreworlds.org:32147]
handshakeID=1119430730
"""
    try:
        with open(worlds_path, 'w') as f:
            f.write(default_content)
        messagebox.showinfo("Success", f"Default '{INI_FILE_NAME}' has been created.")
        refresh_all_indicators()
    except Exception as e:
        messagebox.showerror("Error", f"Could not create '{INI_FILE_NAME}'.\nError: {e}")

def check_setting_status(setting_name, default_active=False):
    try:
        worlds_path = os.path.join(application_path, INI_FILE_NAME)
        with open(worlds_path, 'r') as f:
            for line in f:
                clean_line = line.strip().lower()
                if clean_line.startswith(f"{setting_name.lower()}="):
                    if setting_name.lower() == 'disableshaper':
                        return clean_line.endswith("=0")
                    return clean_line.endswith("=1")
        return default_active
    except FileNotFoundError:
        return default_active

def toggle_setting_action(setting_name, setting_name_in_file, default_active=False):
    try:
        worlds_path = os.path.join(application_path, INI_FILE_NAME)
        is_active = check_setting_status(setting_name, default_active)
        if setting_name.lower() == 'disableshaper':
            new_line = f"{setting_name_in_file}=1\n" if is_active else f"{setting_name_in_file}=0\n"
        else:
            new_line = f"{setting_name_in_file}=0\n" if is_active else f"{setting_name_in_file}=1\n"
        try:
            with open(worlds_path, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            messagebox.showerror("File Not Found", f"'{INI_FILE_NAME}' could not be found.")
            return
        gamma_index, setting_index = -1, -1
        for i, line in enumerate(lines):
            clean_line = line.strip().lower()
            if clean_line == "[gamma]":
                gamma_index = i
            elif clean_line.startswith(f"{setting_name.lower()}="):
                setting_index = i
        if setting_index != -1:
            lines[setting_index] = new_line
        else:
            if gamma_index != -1:
                lines.insert(gamma_index + 1, new_line)
            else:
                lines.insert(0, "[Gamma]\n")
                lines.insert(1, new_line)
        with open(worlds_path, 'w') as f:
            f.writelines(lines)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while modifying worlds.ini:\n{e}")

def get_avatars_value():
    try:
        worlds_path = os.path.join(application_path, INI_FILE_NAME)
        with open(worlds_path, 'r') as f:
            for line in f:
                clean_line = line.strip().lower()
                if clean_line.startswith("avatars="):
                    value = clean_line.split('=')[1]
                    return int(value)
        return 16
    except (FileNotFoundError, ValueError):
        return 16

def set_avatars_value(new_value):
    try:
        worlds_path = os.path.join(application_path, INI_FILE_NAME)
        new_line = f"avatars={new_value}\n"
        try:
            with open(worlds_path, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            messagebox.showerror("File Not Found", f"'{INI_FILE_NAME}' could not be found.")
            return
        gamma_index, setting_index = -1, -1
        for i, line in enumerate(lines):
            clean_line = line.strip().lower()
            if clean_line == "[gamma]":
                gamma_index = i
            elif clean_line.startswith("avatars="):
                setting_index = i
        if setting_index != -1:
            lines[setting_index] = new_line
        else:
            if gamma_index != -1:
                lines.insert(gamma_index + 1, new_line)
            else:
                lines.insert(0, "[Gamma]\n")
                lines.insert(1, new_line)
        with open(worlds_path, 'w') as f:
            f.writelines(lines)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while modifying worlds.ini:\n{e}")

def clean_cache():
    try:
        cache_dir = os.path.join(application_path, 'cachedir')
        if not os.path.isdir(cache_dir):
            messagebox.showinfo("Cache Clean", "Cache folder ('cachedir') not found. Nothing to do.")
            return
        items_to_delete = os.listdir(cache_dir)
        if not items_to_delete:
            messagebox.showinfo("Cache Clean", "Cache folder is already empty.")
            return
        response = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {len(items_to_delete)} items from the cache folder?")
        if not response:
            return
        for filename in items_to_delete:
            file_path = os.path.join(cache_dir, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        messagebox.showinfo("Success", f"Successfully cleaned {len(items_to_delete)} items from the cache.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while cleaning the cache:\n{e}")

def load_full_config():
    try:
        server_config_path = os.path.join(application_path, SERVER_CONFIG_FILE)
        if not os.path.isfile(server_config_path):
            default_config = {"server_selection": {"LibreWorlds": {"address": "[test.libreworlds.org:32147]","world_server": "WorldServer=worldserver://test.libreworlds.org:32147"},"Official": {"address": "[test.3dcd.com:6650]","world_server": "WorldServer=worldserver://http://us1.worlds.net/3DCDup"},"Worlio": {"address": "[worlio.com:6650]","world_server": "WorldServer=worldserver://worlio.com:6650/"}},"updating_server": {"Nothing": {},"Remove": {},"LibreWorlds": {"upgrade_server": "upgradeServer=http://upgrade.libreworlds.org/3DCDup","script_server": "scriptServer=http://script.libreworlds.org"},"Official": {"upgrade_server": "upgradeServer=http://us1.worlds.net/3DCDup","script_server": None},"Worlio": {"upgrade_server": "UpgradeServer=http://files.worlio.com/DCDup/","script_server": "ScriptServer=http://files.worlio.com/cgi-bin/"},"Jett": {"upgrade_server": "upgradeServer=http://jett.dacii.net/3DCDup/","script_server": "ScriptServer=http://jett.dacii.net/cgi-bin/"}}}
            with open(server_config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
        with open(server_config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Critical Error", f"Could not create or read '{SERVER_CONFIG_FILE}'.\nError: {e}")
        return None

def detect_current_server(configurations):
    try:
        worlds_path = os.path.join(application_path, INI_FILE_NAME)
        override_path = os.path.join(application_path, OVERRIDE_FILE_NAME)
        with open(worlds_path, 'r') as f:
            worlds_content = f.read()
        with open(override_path, 'r') as f:
            override_content = f.read()
        for server_name, server_data in configurations.items():
            if "address" in server_data and "world_server" in server_data:
                address_line = server_data["address"]
                worldserver_line = server_data["world_server"]
                if address_line.strip() in worlds_content and worldserver_line.strip() in override_content:
                    return server_name
    except Exception:
        return None
    return None

def apply_changes_and_launch(server_option, updating_option, server_config_map, updating_config_map):
    try:
        if not os.path.isfile(os.path.join(application_path, INI_FILE_NAME)) or not os.path.isfile(os.path.join(application_path, OVERRIDE_FILE_NAME)):
            messagebox.showerror("File Not Found", f"Could not find '{INI_FILE_NAME}' or '{OVERRIDE_FILE_NAME}'. They must be in the same folder as the launcher.")
            return
        run_exe_path = os.path.join(application_path, EXECUTABLE_NAME)
        game_version = 'new'
        if os.path.isfile(run_exe_path):
            game_version = 'old'
        selected_server_config = server_config_map[server_option]
        new_address = selected_server_config["address"]
        new_world_server = selected_server_config["world_server"]
        override_path = os.path.join(application_path, OVERRIDE_FILE_NAME)
        with open(override_path, 'r') as f:
            override_lines = f.readlines()
        runtime_index, worldserver_index = -1, -1
        for i, line in enumerate(override_lines):
            clean_line = line.strip().lower()
            if clean_line == "[runtime]":
                runtime_index = i
            elif clean_line.startswith("worldserver="):
                worldserver_index = i
        if worldserver_index != -1:
            override_lines[worldserver_index] = new_world_server + '\n'
        elif runtime_index != -1:
            override_lines.insert(runtime_index + 1, new_world_server + '\n')
        else:
            override_lines.append("\n[Runtime]\n")
            override_lines.append(new_world_server + '\n')
        with open(override_path, 'w') as f:
            f.writelines(override_lines)
        worlds_path = os.path.join(application_path, INI_FILE_NAME)
        with open(worlds_path, 'r') as f:
            worlds_lines = f.readlines()
        address_lines_to_replace = [config["address"].strip().lower() for config in server_config_map.values()]
        new_worlds_lines = []
        section_to_delete = False
        for line in worlds_lines:
            clean_line = line.strip()
            if clean_line.startswith('[') and clean_line.endswith(']'):
                section_to_delete = clean_line.lower() in address_lines_to_replace
            if not section_to_delete:
                new_worlds_lines.append(line)
        if game_version == 'old':
            try:
                start_index = [l.strip().lower() for l in new_worlds_lines].index('[installedworlds]')
                end_index = start_index + 1
                while end_index < len(new_worlds_lines) and not new_worlds_lines[end_index].strip().startswith('['):
                    end_index += 1
                new_worlds_lines.insert(end_index, '\n' + new_address + '\n')
            except ValueError:
                new_worlds_lines.append('\n' + new_address + '\n')
        if updating_option and updating_option != "Nothing":
            if updating_option == "Remove":
                new_worlds_lines = [line for line in new_worlds_lines if not line.strip().lower().startswith(("upgradeserver=", "scriptserver="))]
            else:
                selected_updating_config = updating_config_map[updating_option]
                new_upgrade_server = selected_updating_config.get("upgrade_server")
                new_script_server = selected_updating_config.get("script_server")
                found_upgrade, found_script = False, False
                final_lines = []
                for line in new_worlds_lines:
                    line_lower = line.strip().lower()
                    if line_lower.startswith("upgradeserver="):
                        if new_upgrade_server: final_lines.append(new_upgrade_server + '\n')
                        found_upgrade = True
                    elif line_lower.startswith("scriptserver="):
                        if new_script_server: final_lines.append(new_script_server + '\n')
                        found_script = True
                    else:
                        final_lines.append(line)
                new_worlds_lines = final_lines
                if not found_upgrade and new_upgrade_server: new_worlds_lines.append(new_upgrade_server + '\n')
                if not found_script and new_script_server: new_worlds_lines.append(new_script_server + '\n')
        with open(worlds_path, 'w') as f:
            f.writelines(new_worlds_lines)
        worldsplayer_exe_path = os.path.join(application_path, FALLBACK_EXECUTABLE_NAME)
        if os.path.isfile(run_exe_path):
            subprocess.run([run_exe_path])
        elif os.path.isfile(worldsplayer_exe_path):
            subprocess.run([worldsplayer_exe_path])
        else:
            messagebox.showerror("Executable Not Found", f"Could not find '{EXECUTABLE_NAME}' or '{FALLBACK_EXECUTABLE_NAME}'.\nPlease ensure one of them is in the program folder.")
            return
        window.quit()
    except Exception as e:
        messagebox.showerror("Unexpected Error", f"An unexpected error has occurred:\n{e}")

# --- 3. PROGRAM START AND GUI ---
class ToolButton(ctk.CTkFrame):
    def __init__(self, parent, text, setting_name, setting_name_in_file, file_exists_status, default_active=False, font_size=12):
        super().__init__(parent, fg_color="transparent")
        self.setting_name = setting_name
        self.setting_name_in_file = setting_name_in_file
        self.file_exists = file_exists_status
        self.default_active = default_active

        # Status Indicator (Red/Green Dot)
        self.indicator_frame = ctk.CTkFrame(self, width=15, height=15, corner_radius=15)
        self.indicator_frame.pack(side='left', padx=(5, 10))
        
        self.btn = ctk.CTkButton(self, text=text, font=('Roboto Medium', font_size),
                                 fg_color='#333333', hover_color='#444444',
                                 command=self.on_click)
        self.btn.pack(side='left', expand=True, fill='x', ipady=6)
        
        self.update_indicator()

    def update_indicator(self):
        if not self.file_exists:
            color = 'red'
        else:
            color = 'green' if check_setting_status(self.setting_name, self.default_active) else 'red'
        self.indicator_frame.configure(fg_color=color)

    def on_click(self):
        if not self.file_exists:
            return
        toggle_setting_action(self.setting_name, self.setting_name_in_file, self.default_active)
        self.update_indicator()

if __name__ == "__main__":
    worlds_ini_exists = os.path.isfile(os.path.join(application_path, INI_FILE_NAME))
    override_ini_exists = os.path.isfile(os.path.join(application_path, OVERRIDE_FILE_NAME))
    full_config = load_full_config()
    
    if full_config:
        SERVER_SELECTION_CONFIG = full_config.get("server_selection", {})
        UPDATING_SERVER_CONFIG = full_config.get("updating_server", {})

        window = ctk.CTk()
        window.title("thedevil4k Launcher")
        window.geometry("1455x664")
        window.resizable(False, False)

        tool_buttons = []

        try:
            icon_path = resource_path(ICON_NAME)
            window.iconbitmap(icon_path)
            
            # Application Background Image
            background_path = resource_path(BACKGROUND_IMAGE_NAME)
            pil_image = Image.open(background_path)
            pil_image = pil_image.resize((1455, 664), Image.Resampling.LANCZOS)
            background_image_obj = ImageTk.PhotoImage(pil_image)
            
            background_label = tk.Label(window, image=background_image_obj, bg="black")
            background_label.place(x=0, y=0, relwidth=1, relheight=1)
            # Ensure background stays behind everything
            background_label.lower()
        except Exception as e:
            print(f"Error loading assets: {e}")
            background_label = None

        # Main Central Container
        main_container = ctk.CTkFrame(window, width=900, height=520, corner_radius=10, fg_color="#1a1a1a")
        # Placing it manually as per original logic to standardise layout
        main_container.place(x=530, y=100)
        main_container.grid_propagate(False)

        main_container.grid_columnconfigure(0, weight=2)
        main_container.grid_columnconfigure(1, weight=4) # Give more weight to the right column
        main_container.grid_rowconfigure(0, weight=1)

        # Tools Section (Left)
        frame_tools = ctk.CTkScrollableFrame(main_container, label_text="TOOLS", label_font=('Roboto Medium', 18))
        frame_tools.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        def refresh_all_indicators():
            global worlds_ini_exists, override_ini_exists
            worlds_ini_exists = os.path.isfile(os.path.join(application_path, INI_FILE_NAME))
            override_ini_exists = os.path.isfile(os.path.join(application_path, OVERRIDE_FILE_NAME))
            
            # File Status Colors
            col_worlds = 'green' if worlds_ini_exists else 'red'
            col_override = 'green' if override_ini_exists else 'red'
            
            if 'worlds_dot_frame' in globals():
                worlds_dot_frame.configure(fg_color=col_worlds)
            if 'override_dot_frame' in globals():
                override_dot_frame.configure(fg_color=col_override)
                
            for tool in tool_buttons:
                tool.file_exists = worlds_ini_exists
                tool.update_indicator()
                
            if worlds_ini_exists:
                entry_avatars.configure(state='normal')
                avatar_value_var.set(str(get_avatars_value()))
            else:
                entry_avatars.configure(state='disabled')
                avatar_value_var.set("N/A")

        # File Management Buttons
        frame_file_management = ctk.CTkFrame(frame_tools, fg_color="transparent")
        frame_file_management.pack(pady=5, fill='x', padx=5)
        
        btn_new_worlds_ini = ctk.CTkButton(frame_file_management, text="NEW WORLDS.INI", font=('Roboto Medium', 9, 'bold'), 
                                           fg_color='#005A9C', hover_color='#003F6E', 
                                           command=create_default_worlds_ini)
        btn_new_worlds_ini.pack(side='left', expand=True, padx=(0,5))
        
        btn_new_override_ini = ctk.CTkButton(frame_file_management, text="NEW OVERRIDE.INI", font=('Roboto Medium', 9, 'bold'), 
                                             fg_color='#005A9C', hover_color='#003F6E', 
                                             command=create_default_override_ini)
        btn_new_override_ini.pack(side='right', expand=True, padx=(5,0))

        # Add Server & Clean Cache
        btn_add_server = ctk.CTkButton(frame_tools, text="ADD SERVER", font=('Roboto Medium', 9, 'bold'), 
                                       fg_color='#006400', hover_color='#004d00', 
                                       command=lambda: open_add_server_window())
        btn_add_server.pack(pady=5, fill='x', padx=5)

        btn_theme_selector = ctk.CTkButton(frame_tools, text="THEME SELECTOR", font=('Roboto Medium', 9, 'bold'), 
                                           fg_color='#800080', hover_color='#4B0082', 
                                           command=lambda: open_theme_selector())
        btn_theme_selector.pack(pady=5, fill='x', padx=5)

        btn_clean_cache = ctk.CTkButton(frame_tools, text="CLEAN CACHE", font=('Roboto Medium', 9, 'bold'), 
                                        fg_color='#5A0000', hover_color='#8B0000', 
                                        command=clean_cache)
        btn_clean_cache.pack(pady=5, fill='x', padx=5)

        # Tool Buttons
        btn_multirun = ToolButton(frame_tools, "MULTIRUN", "multirun", "multirun", worlds_ini_exists)
        btn_multirun.pack(pady=5, fill='x', padx=5)
        tool_buttons.append(btn_multirun)

        btn_chatbox = ToolButton(frame_tools, "CHATBOX", "classicchatbox", "classicchatbox", worlds_ini_exists)
        btn_chatbox.pack(pady=5, fill='x', padx=5)
        tool_buttons.append(btn_chatbox)

        btn_shaper = ToolButton(frame_tools, "SHAPER", "disableshaper", "disableshaper", worlds_ini_exists, default_active=True)
        btn_shaper.pack(pady=5, fill='x', padx=5)
        tool_buttons.append(btn_shaper)

        btn_avatars = ToolButton(frame_tools, "PERMIT ANY AVATARS", "permitanyavatar", "permitAnyAvatar", worlds_ini_exists, font_size=10)
        btn_avatars.pack(pady=5, fill='x', padx=5)
        tool_buttons.append(btn_avatars)

        btn_obscenities = ToolButton(frame_tools, "ALLOW OBSCENITIES", "allowobscenities", "allowObscenities", worlds_ini_exists, font_size=10)
        btn_obscenities.pack(pady=5, fill='x', padx=5)
        tool_buttons.append(btn_obscenities)

        # Max Players
        frame_max_players = ctk.CTkFrame(frame_tools, fg_color="transparent")
        frame_max_players.pack(pady=10, fill='x', padx=5)
        
        avatar_value_var = tk.StringVar()
        
        def on_set_avatars_click():
            if not worlds_ini_exists: return
            try:
                value = int(avatar_value_var.get())
                if 1 <= value <= 256:
                    set_avatars_value(value)
                    avatar_value_var.set(str(get_avatars_value()))
                    messagebox.showinfo("Success", "Max players view value updated successfully.")
                else:
                    messagebox.showerror("Invalid Value", "Please enter a number between 1 and 256.")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number.")
                
        entry_avatars = ctk.CTkEntry(frame_max_players, textvariable=avatar_value_var, width=50, font=('Roboto Medium', 11))
        entry_avatars.pack(side='left', padx=(0, 5))
        
        btn_set_avatars = ctk.CTkButton(frame_max_players, text="SET MAX PLAYERS", font=('Roboto Medium', 10, 'bold'), 
                                        fg_color='#333333', hover_color='#444444', 
                                        command=on_set_avatars_click)
        btn_set_avatars.pack(side='left', expand=True, fill='x')

        # Server Selection Section (Right)
        selection_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        selection_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        selection_frame.grid_rowconfigure(0, weight=1)
        selection_frame.grid_columnconfigure(0, weight=1)

        # Container for server lists
        server_columns_frame = ctk.CTkFrame(selection_frame, fg_color="transparent")
        server_columns_frame.grid(row=0, column=0, sticky='nsew')
        server_columns_frame.grid_columnconfigure(0, weight=1)
        server_columns_frame.grid_columnconfigure(1, weight=1)
        server_columns_frame.grid_rowconfigure(0, weight=1)

        server_option = tk.StringVar()
        updating_option = tk.StringVar(value="Nothing")
        advanced_view_active = tk.BooleanVar(value=False)

        detected_server = detect_current_server(SERVER_SELECTION_CONFIG)
        server_option.set(detected_server or next(iter(SERVER_SELECTION_CONFIG)))

        # Server List Frames
        frame_server_selection = ctk.CTkScrollableFrame(server_columns_frame, label_text="Server Selection", label_font=('Roboto Medium', 16, 'bold'))
        frame_updating_server = ctk.CTkScrollableFrame(server_columns_frame, label_text="Updating Server", label_font=('Roboto Medium', 16, 'bold'))

        def refresh_server_lists():
            global SERVER_SELECTION_CONFIG, UPDATING_SERVER_CONFIG

            # Clear existing
            for widget in frame_server_selection.winfo_children():
                widget.destroy()
            for widget in frame_updating_server.winfo_children():
                widget.destroy()

            new_config = load_full_config()
            if new_config:
                SERVER_SELECTION_CONFIG = new_config.get("server_selection", {})
                UPDATING_SERVER_CONFIG = new_config.get("updating_server", {})

                for name in SERVER_SELECTION_CONFIG:
                    ctk.CTkRadioButton(frame_server_selection, text=name, variable=server_option, value=name, font=('Roboto Medium', 14)).pack(anchor='w', pady=3)

                for name in UPDATING_SERVER_CONFIG:
                    ctk.CTkRadioButton(frame_updating_server, text=name, variable=updating_option, value=name, font=('Roboto Medium', 14)).pack(anchor='w', pady=3)

        refresh_server_lists()

        # Action Buttons (Play / Advanced / Status)
        action_buttons_frame = ctk.CTkFrame(selection_frame, fg_color="transparent")
        action_buttons_frame.grid(row=1, column=0, sticky='ew', pady=10)
        
        launch_button = ctk.CTkButton(action_buttons_frame, text="PLAY", font=('Roboto Medium', 15, 'bold'), 
                                      fg_color='#333333', hover_color='#444444', height=40,
                                      command=lambda: apply_changes_and_launch(server_option.get(), updating_option.get(), SERVER_SELECTION_CONFIG, UPDATING_SERVER_CONFIG))
        launch_button.pack(side='top', expand=True, fill='x', padx=50)

        # File Status Indicators
        file_indicators_frame = ctk.CTkFrame(action_buttons_frame, fg_color="transparent")
        file_indicators_frame.pack(side='top', pady=10)
        
        # Worlds.ini status
        frame_worlds_status = ctk.CTkFrame(file_indicators_frame, fg_color="transparent")
        frame_worlds_status.pack(side='left', padx=10)
        worlds_dot_frame = ctk.CTkFrame(frame_worlds_status, width=12, height=12, corner_radius=10, fg_color='red')
        worlds_dot_frame.pack(side='left', padx=(0,5))
        label_worlds = ctk.CTkLabel(frame_worlds_status, text="worlds.ini", font=('Roboto Medium', 10), text_color='gray')
        label_worlds.pack(side='left')
        
        # Override.ini status
        frame_override_status = ctk.CTkFrame(file_indicators_frame, fg_color="transparent")
        frame_override_status.pack(side='left', padx=10)
        override_dot_frame = ctk.CTkFrame(frame_override_status, width=12, height=12, corner_radius=10, fg_color='red')
        override_dot_frame.pack(side='left', padx=(0,5))
        label_override = ctk.CTkLabel(frame_override_status, text="override.ini", font=('Roboto Medium', 10), text_color='gray')
        label_override.pack(side='left')

        def toggle_advanced_view():
            if advanced_view_active.get():
                frame_updating_server.grid_forget()
                frame_server_selection.grid(row=0, column=0, columnspan=2, sticky='nsew')
                toggle_button.configure(text="[ Advanced ]")
                advanced_view_active.set(False)
            else:
                frame_server_selection.grid(row=0, column=0, columnspan=1, sticky='nsew', padx=5)
                frame_updating_server.grid(row=0, column=1, columnspan=1, sticky='nsew', padx=5)
                toggle_button.configure(text="[ Basic ]")
                advanced_view_active.set(True)

        toggle_button = ctk.CTkButton(action_buttons_frame, text="[ Advanced ]", font=('Roboto Medium', 9), 
                                      fg_color='transparent', text_color='gray', hover_color='#1a1a1a', 
                                      command=toggle_advanced_view)
        toggle_button.pack(side='bottom', pady=5)

        # Initial layout state
        frame_server_selection.grid(row=0, column=0, columnspan=2, sticky='nsew')

        # Add Server Dialog
        def open_theme_selector():
             ThemeSelectorWindow(window)

        def open_add_server_window():
            add_window = ctk.CTkToplevel(window)
            add_window.title("Add New Server")
            add_window.geometry("600x350")
            add_window.resizable(False, False)
            add_window.transient(window)
            add_window.grab_set()
            
            # Force icon to appear by scheduling it slightly after window creation
            add_window.after(200, lambda: add_window.iconbitmap(resource_path(ICON_NAME)))
                
            entries = {}
            def get_placeholders():
                lw_server = SERVER_SELECTION_CONFIG.get("LibreWorlds", {})
                lw_updating = UPDATING_SERVER_CONFIG.get("LibreWorlds", {})
                return {
                    "Server Name": "My Custom Server",
                    "Address Line": lw_server.get("address", "[example.com:12345]"),
                    "WorldServer Line": lw_server.get("world_server", "WorldServer=worldserver://example.com:12345"),
                    "UpgradeServer (Optional)": lw_updating.get("upgrade_server", "upgradeServer=http://example.com/update"),
                    "ScriptServer (Optional)": lw_updating.get("script_server", "scriptServer=http://example.com/scripts")
                }
            placeholders = get_placeholders()
            
            form_frame = ctk.CTkFrame(add_window, fg_color="transparent")
            form_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            for label_text, placeholder in placeholders.items():
                row_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
                row_frame.pack(fill='x', pady=5)
                
                label = ctk.CTkLabel(row_frame, text=label_text + ":", width=180, anchor='w')
                label.pack(side='left')
                
                entry = ctk.CTkEntry(row_frame, width=300)
                entry.pack(side='left', expand=True, fill='x')
                entry.insert(0, placeholder)
                entry.configure(text_color='gray')
                
                def on_focus_in(event, p=placeholder, w=entry):
                    if w.get() == p:
                        w.delete(0, "end")
                        w.configure(text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"])
                def on_focus_out(event, p=placeholder, w=entry):
                    if not w.get():
                        w.insert(0, p)
                        w.configure(text_color='gray')
                        
                entry.bind("<FocusIn>", on_focus_in)
                entry.bind("<FocusOut>", on_focus_out)
                entries[label_text] = entry
                
            def save_new_server():
                server_name = entries["Server Name"].get().strip()
                address = entries["Address Line"].get().strip()
                world_server = entries["WorldServer Line"].get().strip()
                upgrade_server = entries["UpgradeServer (Optional)"].get().strip()
                script_server = entries["ScriptServer (Optional)"].get().strip()
                
                if server_name in [placeholders["Server Name"], ""] or address in [placeholders["Address Line"], ""] or world_server in [placeholders["WorldServer Line"], ""]:
                    messagebox.showerror("Error", "Server Name, Address, and WorldServer fields are mandatory.", parent=add_window)
                    return
                    
                config = load_full_config()
                if not config: return
                
                config["server_selection"][server_name] = {"address": address, "world_server": world_server}
                updating_data = {}
                if upgrade_server not in [placeholders["UpgradeServer (Optional)"], ""]:
                    updating_data["upgrade_server"] = upgrade_server
                else:
                    updating_data["upgrade_server"] = None
                if script_server not in [placeholders["ScriptServer (Optional)"], ""]:
                    updating_data["script_server"] = script_server
                else:
                    updating_data["script_server"] = None
                    
                config["updating_server"][server_name] = updating_data
                
                try:
                    server_config_path = os.path.join(application_path, SERVER_CONFIG_FILE)
                    with open(server_config_path, 'w') as f:
                        json.dump(config, f, indent=4)
                    messagebox.showinfo("Success", f"Server '{server_name}' added successfully.", parent=add_window)
                    add_window.destroy()
                    refresh_server_lists()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save configuration file.\n{e}", parent=add_window)

            button_frame = ctk.CTkFrame(add_window, fg_color="transparent")
            button_frame.pack(pady=10)
            
            save_button = ctk.CTkButton(button_frame, text="Save Server", command=save_new_server)
            save_button.pack(side='left', padx=10)
            
            cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=add_window.destroy, fg_color="transparent", border_width=1)
            cancel_button.pack(side='left', padx=10)

        refresh_all_indicators()
        window.mainloop()
