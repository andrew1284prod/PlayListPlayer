import os
import sys
import json
import locale
import subprocess
import shutil
import urllib.request

def get_sys_lang():
    try:
        lang = locale.getlocale()[0]
        return lang[:2] if lang else "en"
    except: return "en"

LANG = get_sys_lang()
MSG = {
    "ru": {
        "start": "[Установка] Инициализация Playlist Player...",
        "check_pkg": "[Система] Проверка необходимых пакетов...",
        "pkg_missing": "[Внимание] Отсутствуют пакеты: {}. Установить? (y/n): ",
        "dir_select": "[Интерфейс] Выберите директорию для установки в открывшемся окне...",
        "installing": "[Процесс] Копирование файлов и настройка окружения...",
        "downloading": "[Сеть] Файл {} не найден. Скачиваю из репозитория...",
        "alias": "[Конфиг] Настройка алиасов в {}...",
        "done": "[Успех] Установка завершена! Перезапустите терминал.",
        "error": "[Ошибка] Произошел сбой: {}"
    },
    "en": {
        "start": "[Setup] Initializing Playlist Player...",
        "check_pkg": "[System] Checking dependencies...",
        "pkg_missing": "[Warning] Missing packages: {}. Install? (y/n): ",
        "dir_select": "[UI] Select installation directory in the dialog window...",
        "installing": "[Process] Copying files and configuring environment...",
        "downloading": "[Network] File {} not found. Downloading from repository...",
        "alias": "[Config] Setting up aliases in {}...",
        "done": "[Success] Setup complete! Please restart your terminal.",
        "error": "[Error] Something went wrong: {}"
    }
}

REQUIRED_PACKAGES = ["mpv", "yt-dlp", "tmux", "cava", "socat", "python-pyqt6", "zenity", "tk"]
REPO_URL = "https://raw.githubusercontent.com/andrew1284prod/PlayListPlayer/main/"

def ensure_files(current_dir, files):
    """Проверяет наличие файлов, если нет - качает из main"""
    m = MSG[LANG]
    for f in files:
        target = os.path.join(current_dir, f)
        if not os.path.exists(target):
            print(m["downloading"].format(f))
            try:
                url = REPO_URL + f
                urllib.request.urlretrieve(url, target)
            except Exception as e:
                print(f"Ошибка при скачивании {f}: {e}")
                sys.exit(1)

def check_and_install_deps():
    m = MSG[LANG]
    missing = []
    for pkg in REQUIRED_PACKAGES:
        check = subprocess.run(["pacman", "-Qq", pkg], capture_output=True, text=True)
        if check.returncode != 0:
            missing.append(pkg)
    
    if missing:
        ans = input(m["pkg_missing"].format(", ".join(missing))).lower()
        if ans in ['y', 'yes', 'д', 'да']:
            subprocess.run(["sudo", "pacman", "-S", "--needed", "--noconfirm"] + missing)
        else:
            print("[!] Установка прервана: отсутствуют зависимости.")
            sys.exit(1)

def select_directory_native():
    if shutil.which("zenity"):
        try:
            return subprocess.check_output(["zenity", "--file-selection", "--directory", "--title=Путь установки"], text=True).strip()
        except: return None
    return input("Введите путь вручную: ").strip()

def run_setup():
    m = MSG[LANG]
    print(m["start"])

    # 1. Проверка пакетов
    print(m["check_pkg"])
    check_and_install_deps()

    # 2. Выбор папки
    print(m["dir_select"])
    target_path = select_directory_native()
    if not target_path: return

    # 3. Установка
    try:
        print(m["installing"])
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        files = ["gui_config.py", "run_mpv.py", "playlistupd.py", "version.json"]
        
        # САМЫЙ ВАЖНЫЙ МОМЕНТ: Проверяем/качаем файлы перед копированием
        ensure_files(current_dir, files)
        
        for f in files:
            shutil.copy2(os.path.join(current_dir, f), os.path.join(target_path, f))

        # 4. Алиасы
        shell_path = os.environ.get("SHELL", "")
        rc_file = os.path.expanduser("~/.zshrc" if "zsh" in shell_path else "~/.bashrc")
        
        if os.path.exists(rc_file):
            print(m["alias"].format(rc_file))
            alias_data = (
                f'\n# PlaylistPlayer\n'
                f'alias playlist="python3 {os.path.join(target_path, "run_mpv.py")}"\n'
                f'alias playlistconfig="python3 {os.path.join(target_path, "gui_config.py")}"\n'
                f'alias playlistupd="python3 {os.path.join(target_path, "playlistupd.py")}"\n'
            )
            with open(rc_file, "r") as f:
                content = f.read()
                if 'alias playlist="' not in content:
                    with open(rc_file, "a") as fa:
                        fa.write(alias_data)

        print("-" * 40)
        print(m["done"])
    except Exception as e:
        print(m["error"].format(e))

if __name__ == "__main__":
    run_setup()
