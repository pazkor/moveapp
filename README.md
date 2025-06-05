
MoveApp
MoveApp is a lightweight Python tray application for Windows that reminds you to stand up and walk, and to sit with proper posture at regular intervals.

Features
Customizable reminders for walking and sitting straight

Minimal and non-intrusive tray icon

Settings window to update reminder intervals (1–60 minutes)

Optional autostart with Windows

Clean, single-file design with no background terminal window

Requirements
Windows 10/11

Python 3.8 or higher

Install dependencies via pip:

bash
Copy
Edit
pip install pystray pillow plyer pywin32
Setup Instructions
Clone this repository or download the ZIP:

bash
Copy
Edit
git clone https://github.com/yourusername/moveapp.git
cd moveapp
Install required dependencies:

bash
Copy
Edit
pip install pystray pillow plyer pywin32
Make sure these two image files are in the same folder:

trayicon.png (icon for the tray)

bannerlogo.png (displayed at startup)

Run the app:

Double-click v2.pyw (runs silently, no terminal window), or:

From terminal:

bash
Copy
Edit
python v2.pyw
Optional: Autostart with Windows
Right-click the tray icon and select “Run at startup”.
A shortcut will be created in your Startup folder automatically.

Customization
Click the tray icon → Settings

Choose the time intervals (in minutes) for each reminder

Changes take effect immediately after saving

Packaging Tip
To distribute without requiring Python installed:

Use PyInstaller:

bash
Copy
Edit
pyinstaller --noconsole --onefile v2.pyw
Package it along with the icon and banner images.

Notes
Notifications depend on Windows’ built-in notification system.
If you don’t see them, ensure notifications are enabled in your system settings.

This app stores settings locally in settings.json.

License
MIT License
