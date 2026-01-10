import sys
import os
import subprocess
import json
import urllib.request
import locale
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QFileDialog, QMessageBox, QHBoxLayout)
from PyQt6.QtGui import QLinearGradient, QColor, QPalette, QBrush
from PyQt6.QtCore import Qt

# ССЫЛКИ НА ТВОЙ ГИТ
GITHUB_RAW = "https://raw.githubusercontent.com/USER/REPO/main"
FILES_TO_DOWNLOAD = ["run_mpv.py", "gui_config.py", "version.json", "playlistupd.py"]

# Словарик с переводами для инсталлера
LANGS = {
    "ru": {
        "title": "УСТАНОВКА MPV PLAYER Z",
        "path": "Путь:",
        "btn_folder": "ВЫБРАТЬ ПАПКУ 📁",
        "btn_install": "УСТАНОВИТЬ С ГИТХАБА 🚀",
        "success": "Готово!",
        "success_msg": "Всё скачалось и настроилось! ✅\nПримени конфиги: source ~/.bashrc",
        "error": "Трабл",
        "installing": "Ставим зависимости... 🛠️"
    },
    "uk": {
        "title": "ВСТАНОВЛЕННЯ MPV PLAYER Z",
        "path": "Шлях:",
        "btn_folder": "ОБРАТИ ПАПКУ 📁",
        "btn_install": "ВСТАНОВИТИ З ГІТХАБА 🚀",
        "success": "Готово!",
        "success_msg": "Все завантажено та налаштовано! ✅\nЗастосуй конфіги: source ~/.bashrc",
        "error": "Помилка",
        "installing": "Встановлюємо залежності... 🛠️"
    },
    "en": {
        "title": "MPV PLAYER Z INSTALLER",
        "path": "Path:",
        "btn_folder": "SELECT FOLDER 📁",
        "btn_install": "INSTALL FROM GITHUB 🚀",
        "success": "Done!",
        "success_msg": "Everything downloaded and configured! ✅\nApply configs: source ~/.bashrc",
        "error": "Error",
        "installing": "Installing dependencies... 🛠️"
    }
}

# Определяем язык системы
sys_lang = locale.getdefaultlocale()[0][:2] if locale.getdefaultlocale()[0] else "en"
T = LANGS.get(sys_lang, LANGS["en"])

def install_packages():
    deps_pacman = ["mpv", "yt-dlp", "tmux", "cava", "socat", "python-pyqt6"]
    deps_apt = ["mpv", "yt-dlp", "tmux", "cava", "socat", "python3-pyqt6"]

    if subprocess.run(["which", "pacman"], capture_output=True).returncode == 0:
        subprocess.run(["sudo", "pacman", "-S", "--noconfirm"] + deps_pacman)
    elif subprocess.run(["which", "apt"], capture_output=True).returncode == 0:
        subprocess.run(["sudo", "apt", "update"])
        subprocess.run(["sudo", "apt", "install", "-y"] + deps_apt)

class InstallerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MPV Playlist Installer")
        self.setFixedSize(500, 350)
        self.install_path = os.path.expanduser("~/mpvplaylist")
        self.init_ui()

    def init_ui(self):
        gradient = QLinearGradient(0, 0, 0, 350)
        gradient.setColorAt(0.0, QColor(30, 30, 46))
        gradient.setColorAt(1.0, QColor(88, 101, 242))
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        layout = QVBoxLayout()
        
        title = QLabel(T["title"])
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.path_label = QLabel(f"{T['path']} {self.install_path}")
        self.path_label.setStyleSheet("color: #ccc; font-size: 13px;")
        layout.addWidget(self.path_label)

        btn_select = QPushButton(T["btn_folder"])
        btn_select.setStyleSheet("background: rgba(255,255,255,0.1); color: white; padding: 10px; border-radius: 5px;")
        btn_select.clicked.connect(self.select_folder)
        layout.addWidget(btn_select)

        btn_install = QPushButton(T["btn_install"])
        btn_install.setStyleSheet("background: #2ecc71; color: white; font-weight: bold; padding: 15px; border-radius: 8px;")
        btn_install.clicked.connect(self.run_installation)
        layout.addWidget(btn_install)

        linux_only = QLabel("For linux only")
        linux_only.setStyleSheet("color: rgba(255,255,255,0.3); font-size: 10px;")
        layout.addWidget(linux_only, alignment=Qt.AlignmentFlag.AlignLeft)

        self.setLayout(layout)

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, T["btn_folder"])
        if path:
            self.install_path = path
            self.path_label.setText(f"{T['path']} {self.install_path}")

    def run_installation(self):
        try:
            print(T["installing"])
            install_packages()
            os.makedirs(self.install_path, exist_ok=True)
            
            for file in FILES_TO_DOWNLOAD:
                url = f"{GITHUB_RAW}/{file}"
                urllib.request.urlretrieve(url, os.path.join(self.install_path, file))

            py_path = sys.executable
            aliases = {
                "playlist": f"{py_path} {self.install_path}/run_mpv.py",
                "playlistconfig": f"{py_path} {self.install_path}/gui_config.py",
                "playlistupd": f"{py_path} {self.install_path}/playlistupd.py"
            }
            
            for shell_cfg in [".bashrc", ".zshrc"]:
                path = os.path.expanduser(f"~/{shell_cfg}")
                if os.path.exists(path):
                    with open(path, "a") as f:
                        f.write("\n# MPV Playlist Z Aliases\n")
                        for name, cmd in aliases.items():
                            f.write(f"alias {name}='{cmd}'\n")

            QMessageBox.information(self, T["success"], T["success_msg"])
            self.close()
        except Exception as e:
            QMessageBox.critical(self, T["error"], f"Error: {e}")

if __name__ == "__main__":
    try:
        from PyQt6 import QtWidgets
    except ImportError:
        install_packages()
        
    app = QApplication(sys.argv)
    inst = InstallerApp(); inst.show()
    sys.exit(app.exec())
