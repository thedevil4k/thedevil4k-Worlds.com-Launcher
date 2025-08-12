import tkinter as tk
from tkinter import messagebox, ttk
import os
import sys
import subprocess
import json
import shutil
from PIL import Image, ImageTk

# --- Determina la ruta base para archivos externos ---
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# --- FUNCIÓN ESPECIAL PARA ARCHIVOS INTERNOS (EMPAQUETADOS) ---
def resource_path(relative_path):
    """ Obtiene la ruta absoluta a un recurso, funciona para desarrollo y para PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- 1. CONFIGURACIÓN DE ARCHIVOS ---
NOMBRE_ARCHIVO_INI = 'worlds.ini'
NOMBRE_ARCHIVO_OVERRIDE = 'override.ini'
NOMBRE_EJECUTABLE = 'run.exe'
NOMBRE_EJECUTABLE_FALLBACK = 'WorldsPlayer.exe'
NOMBRE_ICONO = 'worldsserverselection.ico'
NOMBRE_IMAGEN_FONDO = 'serverselectionbackground.jpg'
NOMBRE_CONFIG_SERVIDORES = 'worldsserverselection.json'

# --- 2. FUNCIONES DE LÓGICA ---
def create_default_override_ini():
    ruta_override_ini = os.path.join(application_path, NOMBRE_ARCHIVO_OVERRIDE)
    if os.path.isfile(ruta_override_ini):
        respuesta = messagebox.askyesno("Confirm Overwrite", 
                                        f"An '{NOMBRE_ARCHIVO_OVERRIDE}' file already exists. Are you sure you want to overwrite it with a default version?")
        if not respuesta:
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
        with open(ruta_override_ini, 'w') as f:
            f.write(default_content)
        messagebox.showinfo("Success", f"Default '{NOMBRE_ARCHIVO_OVERRIDE}' has been created.")
        refresh_all_indicators()
    except Exception as e:
        messagebox.showerror("Error", f"Could not create '{NOMBRE_ARCHIVO_OVERRIDE}'.\nError: {e}")

def create_default_worlds_ini():
    ruta_worlds_ini = os.path.join(application_path, NOMBRE_ARCHIVO_INI)
    if os.path.isfile(ruta_worlds_ini):
        respuesta = messagebox.askyesno("Confirm Overwrite", 
                                        f"A '{NOMBRE_ARCHIVO_INI}' file already exists. Are you sure you want to overwrite it with a default version?")
        if not respuesta:
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
        with open(ruta_worlds_ini, 'w') as f:
            f.write(default_content)
        messagebox.showinfo("Success", f"Default '{NOMBRE_ARCHIVO_INI}' has been created.")
        refresh_all_indicators()
    except Exception as e:
        messagebox.showerror("Error", f"Could not create '{NOMBRE_ARCHIVO_INI}'.\nError: {e}")

def check_setting_status(setting_name, default_active=False):
    try:
        ruta_worlds_ini = os.path.join(application_path, NOMBRE_ARCHIVO_INI)
        with open(ruta_worlds_ini, 'r') as f:
            for linea in f:
                linea_limpia = linea.strip().lower()
                if linea_limpia.startswith(f"{setting_name.lower()}="):
                    if setting_name.lower() == 'disableshaper':
                        return linea_limpia.endswith("=0")
                    return linea_limpia.endswith("=1")
        return default_active
    except FileNotFoundError:
        return default_active

def toggle_setting_action(setting_name, setting_name_in_file, default_active=False):
    try:
        ruta_worlds_ini = os.path.join(application_path, NOMBRE_ARCHIVO_INI)
        is_active = check_setting_status(setting_name, default_active)
        if setting_name.lower() == 'disableshaper':
            nueva_linea = f"{setting_name_in_file}=1\n" if is_active else f"{setting_name_in_file}=0\n"
        else:
            nueva_linea = f"{setting_name_in_file}=0\n" if is_active else f"{setting_name_in_file}=1\n"
        try:
            with open(ruta_worlds_ini, 'r') as f:
                lineas = f.readlines()
        except FileNotFoundError:
            messagebox.showerror("File Not Found", f"'{NOMBRE_ARCHIVO_INI}' could not be found.")
            return
        gamma_index, setting_index = -1, -1
        for i, linea in enumerate(lineas):
            linea_limpia = linea.strip().lower()
            if linea_limpia == "[gamma]":
                gamma_index = i
            elif linea_limpia.startswith(f"{setting_name.lower()}="):
                setting_index = i
        if setting_index != -1:
            lineas[setting_index] = nueva_linea
        else:
            if gamma_index != -1:
                lineas.insert(gamma_index + 1, nueva_linea)
            else:
                lineas.insert(0, "[Gamma]\n")
                lineas.insert(1, nueva_linea)
        with open(ruta_worlds_ini, 'w') as f:
            f.writelines(lineas)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while modifying worlds.ini:\n{e}")

def get_avatars_value():
    try:
        ruta_worlds_ini = os.path.join(application_path, NOMBRE_ARCHIVO_INI)
        with open(ruta_worlds_ini, 'r') as f:
            for linea in f:
                linea_limpia = linea.strip().lower()
                if linea_limpia.startswith("avatars="):
                    valor = linea_limpia.split('=')[1]
                    return int(valor)
        return 16
    except (FileNotFoundError, ValueError):
        return 16

def set_avatars_value(nuevo_valor):
    try:
        ruta_worlds_ini = os.path.join(application_path, NOMBRE_ARCHIVO_INI)
        nueva_linea = f"avatars={nuevo_valor}\n"
        try:
            with open(ruta_worlds_ini, 'r') as f:
                lineas = f.readlines()
        except FileNotFoundError:
            messagebox.showerror("File Not Found", f"'{NOMBRE_ARCHIVO_INI}' could not be found.")
            return
        gamma_index, setting_index = -1, -1
        for i, linea in enumerate(lineas):
            linea_limpia = linea.strip().lower()
            if linea_limpia == "[gamma]":
                gamma_index = i
            elif linea_limpia.startswith("avatars="):
                setting_index = i
        if setting_index != -1:
            lineas[setting_index] = nueva_linea
        else:
            if gamma_index != -1:
                lineas.insert(gamma_index + 1, nueva_linea)
            else:
                lineas.insert(0, "[Gamma]\n")
                lineas.insert(1, nueva_linea)
        with open(ruta_worlds_ini, 'w') as f:
            f.writelines(lineas)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while modifying worlds.ini:\n{e}")

def limpiar_cache():
    try:
        cache_dir = os.path.join(application_path, 'cachedir')
        if not os.path.isdir(cache_dir):
            messagebox.showinfo("Cache Clean", "Cache folder ('cachedir') not found. Nothing to do.")
            return
        items_a_borrar = os.listdir(cache_dir)
        if not items_a_borrar:
            messagebox.showinfo("Cache Clean", "Cache folder is already empty.")
            return
        respuesta = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {len(items_a_borrar)} items from the cache folder?")
        if not respuesta:
            return
        for filename in items_a_borrar:
            file_path = os.path.join(cache_dir, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        messagebox.showinfo("Success", f"Successfully cleaned {len(items_a_borrar)} items from the cache.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while cleaning the cache:\n{e}")

def cargar_configuracion_completa():
    try:
        ruta_servidores = os.path.join(application_path, NOMBRE_CONFIG_SERVIDORES)
        if not os.path.isfile(ruta_servidores):
            default_config = {"server_selection": {"LibreWorlds": {"address": "[test.libreworlds.org:32147]","world_server": "WorldServer=worldserver://test.libreworlds.org:32147"},"Official": {"address": "[test.3dcd.com:6650]","world_server": "WorldServer=worldserver://http://us1.worlds.net/3DCDup"},"Worlio": {"address": "[worlio.com:6650]","world_server": "WorldServer=worldserver://worlio.com:6650/"}},"updating_server": {"Nothing": {},"Remove": {},"LibreWorlds": {"upgrade_server": "upgradeServer=http://upgrade.libreworlds.org/3DCDup","script_server": "scriptServer=http://script.libreworlds.org"},"Official": {"upgrade_server": "upgradeServer=http://us1.worlds.net/3DCDup","script_server": None},"Worlio": {"upgrade_server": "UpgradeServer=http://files.worlio.com/DCDup/","script_server": "ScriptServer=http://files.worlio.com/cgi-bin/"},"Jett": {"upgrade_server": "upgradeServer=http://jett.dacii.net/3DCDup/","script_server": "ScriptServer=http://jett.dacii.net/cgi-bin/"}}}
            with open(ruta_servidores, 'w') as f:
                json.dump(default_config, f, indent=4)
        with open(ruta_servidores, 'r') as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Critical Error", f"Could not create or read '{NOMBRE_CONFIG_SERVIDORES}'.\nError: {e}")
        return None

def detectar_servidor_actual(configuraciones):
    try:
        ruta_worlds_ini = os.path.join(application_path, NOMBRE_ARCHIVO_INI)
        ruta_override_ini = os.path.join(application_path, NOMBRE_ARCHIVO_OVERRIDE)
        with open(ruta_worlds_ini, 'r') as f:
            contenido_worlds = f.read()
        with open(ruta_override_ini, 'r') as f:
            contenido_override = f.read()
        for nombre_servidor, datos_servidor in configuraciones.items():
            if "address" in datos_servidor and "world_server" in datos_servidor:
                linea_address = datos_servidor["address"]
                linea_worldserver = datos_servidor["world_server"]
                if linea_address.strip() in contenido_worlds and linea_worldserver.strip() in contenido_override:
                    return nombre_servidor
    except Exception:
        return None
    return None

def modificar_y_ejecutar(opcion_server, opcion_updating, config_server, config_updating):
    try:
        if not os.path.isfile(os.path.join(application_path, NOMBRE_ARCHIVO_INI)) or not os.path.isfile(os.path.join(application_path, NOMBRE_ARCHIVO_OVERRIDE)):
            messagebox.showerror("File Not Found", f"Could not find '{NOMBRE_ARCHIVO_INI}' or '{NOMBRE_ARCHIVO_OVERRIDE}'. They must be in the same folder as the launcher.")
            return
        ruta_run_exe = os.path.join(application_path, NOMBRE_EJECUTABLE)
        game_version = 'new'
        if os.path.isfile(ruta_run_exe):
            game_version = 'old'
        config_s = config_server[opcion_server]
        nuevo_address = config_s["address"]
        nuevo_world_server = config_s["world_server"]
        ruta_override_ini = os.path.join(application_path, NOMBRE_ARCHIVO_OVERRIDE)
        with open(ruta_override_ini, 'r') as f:
            lineas_override = f.readlines()
        runtime_index, worldserver_index = -1, -1
        for i, linea in enumerate(lineas_override):
            linea_limpia = linea.strip().lower()
            if linea_limpia == "[runtime]":
                runtime_index = i
            elif linea_limpia.startswith("worldserver="):
                worldserver_index = i
        if worldserver_index != -1:
            lineas_override[worldserver_index] = nuevo_world_server + '\n'
        elif runtime_index != -1:
            lineas_override.insert(runtime_index + 1, nuevo_world_server + '\n')
        else:
            lineas_override.append("\n[Runtime]\n")
            lineas_override.append(nuevo_world_server + '\n')
        with open(ruta_override_ini, 'w') as f:
            f.writelines(lineas_override)
        ruta_worlds_ini = os.path.join(application_path, NOMBRE_ARCHIVO_INI)
        with open(ruta_worlds_ini, 'r') as f:
            lineas_worlds = f.readlines()
        lineas_a_reemplazar_addr = [config["address"].strip().lower() for config in config_server.values()]
        nuevas_lineas_worlds = []
        seccion_a_borrar = False
        for linea in lineas_worlds:
            linea_limpia = linea.strip()
            if linea_limpia.startswith('[') and linea_limpia.endswith(']'):
                seccion_a_borrar = linea_limpia.lower() in lineas_a_reemplazar_addr
            if not seccion_a_borrar:
                nuevas_lineas_worlds.append(linea)
        if game_version == 'old':
            try:
                start_index = [l.strip().lower() for l in nuevas_lineas_worlds].index('[installedworlds]')
                end_index = start_index + 1
                while end_index < len(nuevas_lineas_worlds) and not nuevas_lineas_worlds[end_index].strip().startswith('['):
                    end_index += 1
                nuevas_lineas_worlds.insert(end_index, '\n' + nuevo_address + '\n')
            except ValueError:
                nuevas_lineas_worlds.append('\n' + nuevo_address + '\n')
        if opcion_updating and opcion_updating != "Nothing":
            if opcion_updating == "Remove":
                nuevas_lineas_worlds = [linea for linea in nuevas_lineas_worlds if not linea.strip().lower().startswith(("upgradeserver=", "scriptserver="))]
            else:
                config_u = config_updating[opcion_updating]
                nuevo_upgrade_server = config_u.get("upgrade_server")
                nuevo_script_server = config_u.get("script_server")
                found_upgrade, found_script = False, False
                lineas_finales = []
                for linea in nuevas_lineas_worlds:
                    linea_lower = linea.strip().lower()
                    if linea_lower.startswith("upgradeserver="):
                        if nuevo_upgrade_server: lineas_finales.append(nuevo_upgrade_server + '\n')
                        found_upgrade = True
                    elif linea_lower.startswith("scriptserver="):
                        if nuevo_script_server: lineas_finales.append(nuevo_script_server + '\n')
                        found_script = True
                    else:
                        lineas_finales.append(linea)
                nuevas_lineas_worlds = lineas_finales
                if not found_upgrade and nuevo_upgrade_server: nuevas_lineas_worlds.append(nuevo_upgrade_server + '\n')
                if not found_script and nuevo_script_server: nuevas_lineas_worlds.append(nuevo_script_server + '\n')
        with open(ruta_worlds_ini, 'w') as f:
            f.writelines(nuevas_lineas_worlds)
        ruta_worldsplayer_exe = os.path.join(application_path, NOMBRE_EJECUTABLE_FALLBACK)
        if os.path.isfile(ruta_run_exe):
            subprocess.run([ruta_run_exe])
        elif os.path.isfile(ruta_worldsplayer_exe):
            subprocess.run([ruta_worldsplayer_exe])
        else:
            messagebox.showerror("Executable Not Found", f"Could not find '{NOMBRE_EJECUTABLE}' or '{NOMBRE_EJECUTABLE_FALLBACK}'.\nPlease ensure one of them is in the program folder.")
            return
        ventana.quit()
    except Exception as e:
        messagebox.showerror("Unexpected Error", f"An unexpected error has occurred:\n{e}")

# --- 3. INICIO DEL PROGRAMA Y GUI ---
class ToolButton:
    def __init__(self, parent, text, setting_name, setting_name_in_file, file_exists_status, default_active=False, font_size=11):
        self.setting_name = setting_name
        self.setting_name_in_file = setting_name_in_file
        self.default_active = default_active
        self.file_exists = file_exists_status
        frame = tk.Frame(parent, bg='black')
        frame.pack(pady=5, fill='x', padx=10)
        self.canvas = tk.Canvas(frame, width=20, height=20, bg='black', bd=0, highlightthickness=0)
        self.canvas.pack(side='left', padx=(0, 5))
        self.indicator = self.canvas.create_oval(5, 5, 15, 15, fill='red')
        button = tk.Button(frame, text=text, font=('Arial', font_size, 'bold'), bg='#333333', fg='white', 
                           activebackground='#444444', activeforeground='white', bd=0, command=self.on_click)
        button.pack(side='left', expand=True, fill='x', ipady=8)
        self.update_indicator()
    def update_indicator(self):
        if not self.file_exists:
            color = 'red'
        else:
            color = 'green' if check_setting_status(self.setting_name, self.default_active) else 'red'
        self.canvas.itemconfig(self.indicator, fill=color)
    def on_click(self):
        if not self.file_exists:
            return
        toggle_setting_action(self.setting_name, self.setting_name_in_file, self.default_active)
        self.update_indicator()

class ScrollableFrame(tk.Frame):
    """Un frame con una barra de scroll vertical que responde a la rueda del ratón."""
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg='black', highlightthickness=0, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='black')
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollable_frame.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
    def _on_mousewheel(self, event):
        widget_under_cursor = self.winfo_containing(event.x_root, event.y_root)
        if widget_under_cursor and (widget_under_cursor == self.canvas or self.scrollable_frame in widget_under_cursor.winfo_parents() or widget_under_cursor == self.scrollable_frame):
             self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
if __name__ == "__main__":
    worlds_ini_exists = os.path.isfile(os.path.join(application_path, NOMBRE_ARCHIVO_INI))
    override_ini_exists = os.path.isfile(os.path.join(application_path, NOMBRE_ARCHIVO_OVERRIDE))
    config_completa = cargar_configuracion_completa()
    if config_completa:
        SERVER_SELECTION_CONFIG = config_completa.get("server_selection", {})
        UPDATING_SERVER_CONFIG = config_completa.get("updating_server", {})
        
        ventana = tk.Tk()
        ventana.title("thedevil4k Launcher")
        ventana.geometry("1455x664")
        ventana.resizable(False, False)
        
        tool_buttons = []
        
        try:
            ruta_icono = resource_path(NOMBRE_ICONO)
            ventana.iconbitmap(ruta_icono)
            ruta_fondo = resource_path(NOMBRE_IMAGEN_FONDO)
            imagen_pil = Image.open(ruta_fondo)
            imagen_pil = imagen_pil.resize((1455, 664), Image.Resampling.LANCZOS)
            imagen_fondo_obj = ImageTk.PhotoImage(imagen_pil)
            label_fondo = tk.Label(ventana, image=imagen_fondo_obj)
            label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading assets: {e}")
        
        # <--- INICIO: AJUSTE DE TAMAÑO Y POSICIÓN DEL CONTENEDOR PRINCIPAL ---
        contenedor_widgets = tk.Frame(ventana, bg='black')
        contenedor_widgets.place(x=600, y=150, width=840, height=450)
        # <--- FIN: AJUSTE ---
        
        contenedor_widgets.grid_columnconfigure(0, weight=2)
        # <--- INICIO: AJUSTE DE PROPORCIÓN DE COLUMNAS ---
        contenedor_widgets.grid_columnconfigure(1, weight=4) # Damos más peso a la columna derecha
        # <--- FIN: AJUSTE ---
        contenedor_widgets.grid_rowconfigure(0, weight=1)

        tools_container = ScrollableFrame(contenedor_widgets, bg='black')
        tools_container.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        frame_tools = tools_container.scrollable_frame
        
        label_tools_title = tk.Label(frame_tools, text="TOOLS", font=('Arial', 18, 'bold'), bg='black', fg='white')
        label_tools_title.pack(pady=5)
        
        def refresh_all_indicators():
            global worlds_ini_exists, override_ini_exists
            worlds_ini_exists = os.path.isfile(os.path.join(application_path, NOMBRE_ARCHIVO_INI))
            override_ini_exists = os.path.isfile(os.path.join(application_path, NOMBRE_ARCHIVO_OVERRIDE))
            canvas_worlds.itemconfig(punto_worlds, fill='green' if worlds_ini_exists else 'red')
            canvas_override.itemconfig(punto_override, fill='green' if override_ini_exists else 'red')
            for tool in tool_buttons:
                tool.file_exists = worlds_ini_exists
                tool.update_indicator()
            if worlds_ini_exists:
                entry_avatars.config(state='normal')
                avatar_value_var.set(str(get_avatars_value()))
            else:
                entry_avatars.config(state='disabled')
                avatar_value_var.set("N/A")
        
        frame_file_management = tk.Frame(frame_tools, bg='black')
        frame_file_management.pack(pady=5, fill='x', padx=10)
        boton_new_worlds_ini = tk.Button(frame_file_management, text="NEW WORLDS.INI", font=('Arial', 9, 'bold'), bg='#005A9C', fg='white', activebackground='#003F6E', activeforeground='white', bd=0, command=create_default_worlds_ini)
        boton_new_worlds_ini.pack(side='left', expand=True, padx=(0,5), ipady=5)
        boton_new_override_ini = tk.Button(frame_file_management, text="NEW OVERRIDE.INI", font=('Arial', 9, 'bold'), bg='#005A9C', fg='white', activebackground='#003F6E', activeforeground='white', bd=0, command=create_default_override_ini)
        boton_new_override_ini.pack(side='right', expand=True, padx=(5,0), ipady=5)
        
        boton_add_server = tk.Button(frame_tools, text="ADD SERVER", font=('Arial', 9, 'bold'), bg='#006400', fg='white', activebackground='#004d00', activeforeground='white', bd=0, command=lambda: open_add_server_window())
        boton_add_server.pack(pady=5, ipady=5, fill='x', padx=10)

        boton_limpiar_cache = tk.Button(frame_tools, text="CLEAN CACHE", font=('Arial', 9, 'bold'), bg='#5A0000', fg='white', activebackground='#8B0000', activeforeground='white', bd=0, command=limpiar_cache)
        boton_limpiar_cache.pack(pady=5, ipady=5, fill='x', padx=10)
        
        tool_buttons.append(ToolButton(frame_tools, "MULTIRUN", "multirun", "multirun", worlds_ini_exists))
        tool_buttons.append(ToolButton(frame_tools, "CHATBOX", "classicchatbox", "classicchatbox", worlds_ini_exists))
        tool_buttons.append(ToolButton(frame_tools, "SHAPER", "disableshaper", "disableshaper", worlds_ini_exists, default_active=True))
        tool_buttons.append(ToolButton(frame_tools, "PERMIT ANY AVATARS", "permitanyavatar", "permitAnyAvatar", worlds_ini_exists, font_size=10))
        tool_buttons.append(ToolButton(frame_tools, "ALLOW OBSCENITIES", "allowobscenities", "allowObscenities", worlds_ini_exists, font_size=10))
        
        frame_max_players = tk.Frame(frame_tools, bg='black')
        frame_max_players.pack(pady=5, fill='x', padx=10)
        avatar_value_var = tk.StringVar()
        def on_set_avatars_click():
            if not worlds_ini_exists: return
            try:
                valor = int(avatar_value_var.get())
                if 1 <= valor <= 256:
                    set_avatars_value(valor)
                    avatar_value_var.set(str(get_avatars_value()))
                    messagebox.showinfo("Success", "Max players view value updated successfully.")
                else:
                    messagebox.showerror("Invalid Value", "Please enter a number between 1 and 256.")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number.")
        entry_avatars = tk.Entry(frame_max_players, textvariable=avatar_value_var, width=5, font=('Arial', 11))
        entry_avatars.pack(side='left', padx=(0, 5))
        boton_set_avatars = tk.Button(frame_max_players, text="SET MAX PLAYERS", font=('Arial', 10, 'bold'), bg='#333333', fg='white', activebackground='#444444', activeforeground='white', bd=0, command=on_set_avatars_click)
        boton_set_avatars.pack(side='left', expand=True, fill='x', ipady=8)
        
        frame_selecciones = tk.Frame(contenedor_widgets, bg='black')
        frame_selecciones.grid(row=0, column=1, sticky='nsew', padx=(20, 0))
        frame_selecciones.grid_rowconfigure(0, weight=1)
        
        frame_columnas_servidores = tk.Frame(frame_selecciones, bg='black')
        frame_columnas_servidores.pack(fill='both', expand=True)
        frame_columnas_servidores.grid_columnconfigure(0, weight=1)
        frame_columnas_servidores.grid_columnconfigure(1, weight=1)
        frame_columnas_servidores.grid_rowconfigure(0, weight=1)

        opcion_server = tk.StringVar()
        opcion_updating = tk.StringVar(value="Nothing")
        advanced_view_active = tk.BooleanVar(value=False)
        
        servidor_detectado = detectar_servidor_actual(SERVER_SELECTION_CONFIG)
        opcion_server.set(servidor_detectado or next(iter(SERVER_SELECTION_CONFIG)))
        
        frame_server_selection = ScrollableFrame(frame_columnas_servidores)
        frame_updating_server = ScrollableFrame(frame_columnas_servidores)
        
        def refresh_server_lists():
            global SERVER_SELECTION_CONFIG, UPDATING_SERVER_CONFIG
            
            for widget in frame_server_selection.scrollable_frame.winfo_children():
                widget.destroy()
            for widget in frame_updating_server.scrollable_frame.winfo_children():
                widget.destroy()

            new_config = cargar_configuracion_completa()
            if new_config:
                SERVER_SELECTION_CONFIG = new_config.get("server_selection", {})
                UPDATING_SERVER_CONFIG = new_config.get("updating_server", {})
                
                label_server_title = tk.Label(frame_server_selection.scrollable_frame, text="Server Selection", font=('Arial', 16, 'bold'), bg='black', fg='white')
                label_server_title.pack()
                for nombre in SERVER_SELECTION_CONFIG:
                    tk.Radiobutton(frame_server_selection.scrollable_frame, text=nombre, variable=opcion_server, value=nombre, font=('Arial', 14), bg='black', fg='white', activebackground='black', activeforeground='white', selectcolor='black').pack(anchor='w', pady=3)
                
                label_updating_title = tk.Label(frame_updating_server.scrollable_frame, text="Updating Server", font=('Arial', 16, 'bold'), bg='black', fg='white')
                label_updating_title.pack()
                for nombre in UPDATING_SERVER_CONFIG:
                    tk.Radiobutton(frame_updating_server.scrollable_frame, text=nombre, variable=opcion_updating, value=nombre, font=('Arial', 14), bg='black', fg='white', activebackground='black', activeforeground='white', selectcolor='black').pack(anchor='w', pady=3)

        refresh_server_lists()

        frame_botones_accion = tk.Frame(frame_selecciones, bg='black')
        frame_botones_accion.pack(side='bottom', fill='x', pady=10)
        boton_ejecutar = tk.Button(frame_botones_accion, text="PLAY", font=('Arial', 15, 'bold'), bg='#333333', fg='white', activebackground='#444444', activeforeground='white', bd=0, command=lambda: modificar_y_ejecutar(opcion_server.get(), opcion_updating.get(), SERVER_SELECTION_CONFIG, UPDATING_SERVER_CONFIG))
        boton_ejecutar.pack(side='top', expand=True, ipady=8, fill='x', padx=50)
        
        frame_indicadores_archivos = tk.Frame(frame_botones_accion, bg='black')
        frame_indicadores_archivos.pack(side='top', pady=10)
        frame_worlds_status = tk.Frame(frame_indicadores_archivos, bg='black')
        frame_worlds_status.pack(side='left', padx=10)
        canvas_worlds = tk.Canvas(frame_worlds_status, width=20, height=15, bg='black', bd=0, highlightthickness=0)
        canvas_worlds.pack(side='left')
        punto_worlds = canvas_worlds.create_oval(5, 5, 12, 12, fill='red')
        label_worlds = tk.Label(frame_worlds_status, text="worlds.ini", font=('Arial', 8), bg='black', fg='gray')
        label_worlds.pack(side='left')
        frame_override_status = tk.Frame(frame_indicadores_archivos, bg='black')
        frame_override_status.pack(side='left', padx=10)
        canvas_override = tk.Canvas(frame_override_status, width=20, height=15, bg='black', bd=0, highlightthickness=0)
        canvas_override.pack(side='left')
        punto_override = canvas_override.create_oval(5, 5, 12, 12, fill='red')
        label_override = tk.Label(frame_override_status, text="override.ini", font=('Arial', 8), bg='black', fg='gray')
        label_override.pack(side='left')

        def update_file_status_indicators():
            canvas_worlds.itemconfig(punto_worlds, fill='green' if worlds_ini_exists else 'red')
            canvas_override.itemconfig(punto_override, fill='green' if override_ini_exists else 'red')
        
        def toggle_advanced_view():
            if advanced_view_active.get(): 
                frame_updating_server.grid_forget()
                frame_server_selection.grid(row=0, column=0, columnspan=2, sticky='nsew')
                boton_toggle.config(text="[ Advanced ]")
                advanced_view_active.set(False)
            else: 
                frame_server_selection.grid(row=0, column=0, columnspan=1, sticky='nsew', padx=5)
                frame_updating_server.grid(row=0, column=1, columnspan=1, sticky='nsew', padx=5)
                boton_toggle.config(text="[ Basic ]")
                advanced_view_active.set(True)
        
        boton_toggle = tk.Button(frame_botones_accion, text="[ Advanced ]", font=('Arial', 9), bg='black', fg='gray', activebackground='black', activeforeground='white', bd=0, command=toggle_advanced_view)
        boton_toggle.pack(side='bottom', pady=5)
        
        frame_server_selection.grid(row=0, column=0, columnspan=2, sticky='nsew')
        
        def open_add_server_window():
            add_window = tk.Toplevel(ventana)
            add_window.title("Add New Server")
            add_window.geometry("600x250")
            add_window.config(bg="#222222")
            add_window.resizable(False, False)
            add_window.transient(ventana)
            add_window.grab_set()
            try:
                ruta_icono_add = resource_path(NOMBRE_ICONO)
                add_window.iconbitmap(ruta_icono_add)
            except Exception:
                pass
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
            for label_text, placeholder in placeholders.items():
                frame = tk.Frame(add_window, bg='#222222')
                frame.pack(fill='x', padx=15, pady=5)
                label = tk.Label(frame, text=label_text + ":", bg='#222222', fg='white', width=22, anchor='w')
                label.pack(side='left')
                entry = tk.Entry(frame, width=50)
                entry.pack(side='left', expand=True, fill='x')
                entry.insert(0, placeholder)
                entry.config(fg='grey')
                def on_focus_in(event, p=placeholder):
                    if event.widget.get() == p:
                        event.widget.delete(0, "end")
                        event.widget.config(fg='black')
                def on_focus_out(event, p=placeholder):
                    if not event.widget.get():
                        event.widget.insert(0, p)
                        event.widget.config(fg='grey')
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
                config = cargar_configuracion_completa()
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
                    ruta_servidores = os.path.join(application_path, NOMBRE_CONFIG_SERVIDORES)
                    with open(ruta_servidores, 'w') as f:
                        json.dump(config, f, indent=4)
                    messagebox.showinfo("Success", f"Server '{server_name}' added successfully.", parent=add_window)
                    add_window.destroy()
                    refresh_server_lists()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save configuration file.\n{e}", parent=add_window)
            button_frame = tk.Frame(add_window, bg='#222222')
            button_frame.pack(pady=10)
            save_button = tk.Button(button_frame, text="Save Server", command=save_new_server, bg='#005A9C', fg='white')
            save_button.pack(side='left', padx=10)
            cancel_button = tk.Button(button_frame, text="Cancel", command=add_window.destroy)
            cancel_button.pack(side='left', padx=10)
        
        refresh_all_indicators()
        
        ventana.mainloop()