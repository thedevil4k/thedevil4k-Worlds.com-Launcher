import os
import sys
import shutil
import customtkinter as ctk
from PIL import Image

class ThemeSelectorWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Worlds.com Theme Selector")
        self.geometry("600x500")
        
        # Determine paths
        # internal_path: Where resources (themes, files.txt) are - inside EXE if frozen
        # external_path: Where executable is - where files will be copied to
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller
                self.internal_path = sys._MEIPASS
            else:
                # Nuitka or other
                self.internal_path = os.path.dirname(os.path.abspath(__file__))
            self.external_path = os.path.dirname(sys.executable)
        else:
            self.internal_path = os.path.dirname(os.path.abspath(__file__))
            self.external_path = self.internal_path

        self.themes_dir = os.path.join(self.internal_path, "themes")
        self.files_list_path = os.path.join(self.internal_path, "files.txt")
        # Renamed locally to theme_icon.ico
        self.icon_path = os.path.join(self.internal_path, "theme_icon.ico")
        self.screenshots_dir = os.path.join(self.internal_path, "screenshots")
        
        if os.path.exists(self.icon_path):
            self.iconbitmap(self.icon_path)
        
        # Make modal/transient
        self.transient(parent)
        self.grab_set()

        self.selected_theme = None
        self.theme_buttons = []
        self.theme_images = {} # To keep references to images

        self.create_widgets()
        self.load_themes()

    def create_widgets(self):
        # Title
        self.label_title = ctk.CTkLabel(self, text="Select a Theme", font=("Roboto", 24))
        self.label_title.pack(pady=20)

        # Theme List Container (Scrollable)
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Available Themes")
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Apply Button
        self.btn_apply = ctk.CTkButton(
            self, 
            text="Apply Theme", 
            command=self.apply_theme, 
            state="disabled",
            height=40,
            font=("Roboto", 16)
        )
        self.btn_apply.pack(pady=20)

        # Status Label
        self.label_status = ctk.CTkLabel(self, text="", text_color="gray")
        self.label_status.pack(pady=5)

    def load_themes(self):
        if not os.path.exists(self.themes_dir):
            self.label_status.configure(text=f"Error: 'themes' folder not found at {self.themes_dir}", text_color="red")
            return

        try:
            themes = [d for d in os.listdir(self.themes_dir) if os.path.isdir(os.path.join(self.themes_dir, d))]
            themes.sort()
        except Exception as e:
            self.label_status.configure(text=f"Error reading themes: {e}", text_color="red")
            return

        # Pre-load available screenshots map (lowercased without extension -> full filename)
        screenshot_map = {}
        if os.path.exists(self.screenshots_dir):
            for f in os.listdir(self.screenshots_dir):
                name, ext = os.path.splitext(f)
                screenshot_map[name.lower()] = f

        # Custom mappings (lowercase theme name -> filename)
        custom_map = {
            "hosts hud": "hostHUD.gif",
            "thedevil4k hud 2025": "thedevil4k_hud.gif",
            "cranelaneii": "cranelane2.gif"
        }

        for theme in themes:
            # Check for image
            theme_img = None
            theme_key = theme.lower()
            
            img_filename = None
            
            # Check custom map first, then automatic map
            if theme_key in custom_map:
                img_filename = custom_map[theme_key]
            elif theme_key in screenshot_map:
                img_filename = screenshot_map[theme_key]

            if img_filename:
                img_path = os.path.join(self.screenshots_dir, img_filename)
                try:
                    # Load and resize image for icon
                    pil_img = Image.open(img_path)
                    theme_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(240, 135))
                    # Keep reference
                    self.theme_images[theme] = theme_img
                except Exception as e:
                    print(f"Error loading image for {theme}: {e}")

            # Create a button for each theme
            btn = ctk.CTkButton(
                self.scrollable_frame, 
                text=theme, 
                fg_color="transparent", 
                border_width=1, 
                border_color=("gray70", "gray30"),
                text_color=("gray10", "#DCE4EE"),
                anchor="w",
                image=theme_img,
                compound="left",
                height=150,
                font=("Roboto", 24),
                command=lambda t=theme: self.select_theme(t)
            )
            btn.pack(fill="x", pady=5, padx=5)
            self.theme_buttons.append(btn)

    def select_theme(self, theme_name):
        self.selected_theme = theme_name
        self.label_title.configure(text=f"Selected: {theme_name}")
        self.btn_apply.configure(state="normal")
        
        # Update visual selection
        for btn in self.theme_buttons:
            if btn.cget("text") == theme_name:
                btn.configure(fg_color=("gray75", "#2CC985")) # Green selection color
            else:
                btn.configure(fg_color="transparent")

    def apply_theme(self):
        if not self.selected_theme:
            return

        if not os.path.exists(self.files_list_path):
            self.label_status.configure(text="Error: files.txt not found", text_color="red")
            return

        theme_path = os.path.join(self.themes_dir, self.selected_theme)
        
        try:
            with open(self.files_list_path, 'r') as f:
                # Read lines avoiding empty ones
                files_to_copy = [line.strip() for line in f if line.strip()]

            count = 0
            missing_files = []

            for filename in files_to_copy:
                src_file = os.path.join(theme_path, filename)
                # DESTINATION is the external path (where the exe is)
                dst_file = os.path.join(self.external_path, filename)

                if os.path.exists(src_file):
                    shutil.copy2(src_file, dst_file)
                    count += 1
                else:
                    missing_files.append(filename)

            msg = f"Theme '{self.selected_theme}' applied.\n{count} files copied."
            if missing_files:
                msg += f"\n\nMissing files in theme (skipped):\n" + "\n".join(missing_files[:5])
                if len(missing_files) > 5:
                    msg += "\n..."
            
            self.label_status.configure(text="Theme applied successfully!", text_color="green")
            # We can also close the window or stay open
            # self.destroy() 

        except Exception as e:
            self.label_status.configure(text=f"Error: {str(e)}", text_color="red")
