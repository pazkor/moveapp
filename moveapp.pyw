# -*- coding: utf-8 -*-
import os
import sys
import time
import json
import threading
import tempfile
import tkinter as tk
from tkinter import ttk
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageTk, ImageDraw, ImageOps
import psutil  # NEW

LOCK_FILE = os.path.join(tempfile.gettempdir(), 'move_app.lock')

stop_event = threading.Event()


def check_already_running():
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, 'r') as f:
                old_pid = int(f.read())
            if psutil.pid_exists(old_pid):
                sys.exit(0)
            else:
                os.remove(LOCK_FILE)
        except:
            os.remove(LOCK_FILE)

    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))
    import atexit
    atexit.register(lambda: os.remove(LOCK_FILE) if os.path.exists(LOCK_FILE) else None)


check_already_running()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, "trayicon.png")
BANNER_PATH = os.path.join(BASE_DIR, "bannerlogo.png")
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")

APP_NAME = "MoveApp"
STARTUP_FOLDER = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
SHORTCUT_PATH = os.path.join(STARTUP_FOLDER, f"{APP_NAME}.lnk")

default_settings = {
    "walk_interval": 25,
    "posture_interval": 40
}

def load_settings():
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return default_settings.copy()

def save_settings(data):
    try:
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

settings = load_settings()


def show_notification(title, message):
    try:
        from plyer import notification
        notification.notify(title=title, message=message, timeout=10)
    except:
        pass

def remind_both():
    walk_timer = 0
    posture_timer = 0
    while not stop_event.wait(1):
        walk_timer += 1
        posture_timer += 1
        if walk_timer >= settings["walk_interval"] * 60:
            show_notification("🚶‍♂️ Time for a short walk", "Get up and take a quick walk!")
            walk_timer = 0
        if posture_timer >= settings["posture_interval"] * 60:
            show_notification("🪑 Sit up straight!", "Keep good posture for your back.")
            posture_timer = 0

def show_startup_overlay():
    if not os.path.exists(BANNER_PATH):
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, "Missing: bannerlogo.png", "Error", 0x10)
        return

    def close_after_delay():
        time.sleep(2.5)
        root.destroy()

    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.9)
    root.configure(background='white')

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    width, height = 400, 200
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")

    try:
        image = Image.open(BANNER_PATH)
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        label = tk.Label(root, image=photo, bg='white')
        label.image = photo
        label.pack()
    except:
        pass

    threading.Thread(target=close_after_delay, daemon=True).start()
    root.mainloop()

def open_settings_window(icon=None, item=None):
    def save_and_close():
        try:
            settings["walk_interval"] = int(walk_spinbox.get())
            settings["posture_interval"] = int(posture_spinbox.get())
            save_settings(settings)
            stop_event.set()
            time.sleep(0.1)
            stop_event.clear()
            run_reminders()
            show_notification("MoveApp", "Settings saved successfully.")
            window.destroy()
        except:
            pass

    window = tk.Tk()
    window.title("MoveApp Settings")
    window.geometry("400x300")
    window.resizable(False, False)
    window.attributes("-topmost", True)

    ttk.Label(window, text="Reminder interval for walking (minutes):").pack(pady=(30, 5))
    walk_spinbox = ttk.Spinbox(window, from_=1, to=60, width=5, justify='center')
    walk_spinbox.set(settings["walk_interval"])
    walk_spinbox.pack()

    ttk.Label(window, text="Reminder interval for posture (minutes):").pack(pady=(30, 5))
    posture_spinbox = ttk.Spinbox(window, from_=1, to=60, width=5, justify='center')
    posture_spinbox.set(settings["posture_interval"])
    posture_spinbox.pack()

    ttk.Button(window, text="Save and Close", command=save_and_close).pack(pady=30)
    window.mainloop()

def run_reminders():
    threading.Thread(target=remind_both, daemon=True).start()

def create_image():
    if not os.path.exists(ICON_PATH):
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, "Missing: trayicon.png", "Error", 0x10)
        sys.exit(1)
    return Image.open(ICON_PATH)

def quit_program(icon, item):
    stop_event.set()
    icon.stop()

def is_autostart_enabled(item=None):
    return os.path.exists(SHORTCUT_PATH)

def toggle_autostart(icon, item):
    if is_autostart_enabled():
        try:
            os.remove(SHORTCUT_PATH)
            item.checked = False
            show_notification("MoveApp", "Autostart disabled")
        except:
            pass
    else:
        create_shortcut()
        item.checked = True
        show_notification("MoveApp", "Will start automatically with Windows")

def create_shortcut():
    try:
        import pythoncom
        from win32com.client import Dispatch
        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(SHORTCUT_PATH)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{__file__}"'
        shortcut.WorkingDirectory = BASE_DIR
        shortcut.IconLocation = ICON_PATH
        shortcut.save()
    except:
        pass

def build_menu():
    return Menu(
        MenuItem("Settings", open_settings_window),
        MenuItem("Run at startup", toggle_autostart, checked=is_autostart_enabled),
        MenuItem("Quit", quit_program)
    )

threading.Thread(target=show_startup_overlay, daemon=True).start()
run_reminders()
icon = Icon(APP_NAME, create_image(), menu=build_menu())
icon.run()
