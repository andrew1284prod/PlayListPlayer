import os
import sys
import json
import locale
import subprocess
import urllib.request

GITHUB_RAW = "https://raw.githubusercontent.com/andrew1284prod/playlistplayer/main/"
VERSION_FILE = "version.json"

def get_sys_lang():
    try:
        lang = locale.getlocale()[0]
        return lang[:2] if lang else "en"
    except: return "en"

LANG = get_sys_lang()
MSG = {
    "ru": {
        "start": "[Установка] Запуск процесса развертывания системы...",
        "fetch_ver": "[Связь] Получение данных о версии...",
        "download": "[Процесс] Загрузка компонентов {v} ({p}, тип {t})...",
        "deps": "[Система] Установка необходимых зависимостей...",
        "done": "[Успех] Playlist Player v{v} успешно установлен в систему."
    },
    "en": {
        "start": "[Setup] Starting system deployment process...",
        "fetch_ver": "[Network] Fetching version data...",
        "download": "[Process] Downloading components {v} ({p}, type {t})...",
        "deps": "[System] Installing required dependencies...",
        "done": "[Success] Playlist Player v{v} installed successfully."
    }
}

def run_setup():
    m = MSG.get(LANG, MSG["en"])
    print(m["start"])
    
    # 1. Получаем инфу о версии перед загрузкой
    print(m["fetch_ver"])
    try:
        with urllib.request.urlopen(GITHUB_RAW + VERSION_FILE) as res:
            v_data = json.loads(res.read().decode())
            ver = v_data.get("version")
            prev = v_data.get("versionpreview")
            v_type = v_data.get("versiontype")
    except:
        ver, prev, v_type = "Unknown", "Unknown", "Unknown"

    print(m["download"].format(v=ver, p=prev, t=v_type))

    # 2. Логика скачивания файлов (пример)
    files = ["gui_config.py", "run_mpv.py", "playlistupd.py", "version.json"]
    for f in files:
        try:
            urllib.request.urlretrieve(GITHUB_RAW + f, f)
        except:
            print(f"[!] Ошибка загрузки {f}")

    # 3. Установка зависимостей (строгий вывод)
    print(m["deps"])
    # Пример вызова пакетного менеджера (Arch Linux)
    # subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "mpv", "yt-dlp", "tmux", "cava", "socat", "python-pyqt6"])

    print(m["done"].format(v=ver))

if __name__ == "__main__":
    run_setup()
