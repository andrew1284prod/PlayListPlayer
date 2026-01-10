import os
import shutil
import urllib.request
import hashlib
import locale
import json

# Конфигурация путей
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = "/tmp/playlist_update_check"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/andrew1284prod/playlistplayer/main/"
VERSION_FILE = "version.json" # Файл с версией на GitHub (например, {"version": "1.2"})

# Список файлов для глубокой проверки
FILES_TO_CHECK = ["gui_config.py", "run_mpv.py", "playlistupd.py"]

def get_sys_lang():
    try:
        lang = locale.getlocale()[0]
        return lang[:2] if lang else "en"
    except: return "en"

LANG = get_sys_lang()
MSG = {
    "ru": {
        "ver_check": "[Информация] Проверка версии...",
        "ver_match": "[Информация] У вас установлена актуальная версия. Провести глубокую проверку файлов? (y/n): ",
        "new_ver": "[Обновление] Доступна новая версия! Установить? (y/n): ",
        "start": "[Информация] Начало проверки целостности компонентов...",
        "updating": "[Обновление] Файл {} изменен. Переустановка...",
        "no_change": "[Информация] Файл {} в порядке.",
        "cleanup": "[Система] Очистка временных файлов...",
        "done": "[Успех] Все компоненты проверены и актуализированы.",
        "error": "[Ошибка] Не удалось получить данные: {}",
        "cancel": "[Отмена] Операция отменена пользователем."
    },
    "en": {
        "ver_check": "[Info] Checking version...",
        "ver_match": "[Info] Your version is up to date. Perform deep integrity check? (y/n): ",
        "new_ver": "[Update] New version available! Install? (y/n): ",
        "start": "[Info] Starting component integrity check...",
        "updating": "[Update] File {} changed. Reinstalling...",
        "no_change": "[Info] File {} is up to date.",
        "cleanup": "[System] Cleaning up temporary files...",
        "done": "[Success] All components checked and updated.",
        "error": "[Error] Failed to fetch data: {}",
        "cancel": "[Cancel] Operation cancelled by user."
    }
}

def get_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def ask_user(text):
    ans = input(text).lower()
    return ans in ['y', 'yes', 'д', 'да']

def run_update():
    m = MSG.get(LANG, MSG["en"])
    print(m["ver_check"])
    
    # 1. Сначала проверяем версию
    try:
        with urllib.request.urlopen(GITHUB_RAW_URL + VERSION_FILE) as response:
            remote_version_data = json.loads(response.read().decode())
            remote_version = remote_version_data.get("version", "1.0")
            
        # Локальная версия (можно хранить в файле или в коде)
        local_version = "1.0" # Пример

        if remote_version == local_version:
            if not ask_user(m["ver_match"]):
                return
        else:
            if not ask_user(m["new_ver"]):
                return
    except Exception as e:
        print(m["error"].format(e))
        if not ask_user(m["ver_match"]): return

    # 2. Глубокая проверка файлов
    print(m["start"])
    if os.path.exists(TMP_DIR): shutil.rmtree(TMP_DIR)
    os.makedirs(TMP_DIR)

    try:
        for filename in FILES_TO_CHECK:
            local_path = os.path.join(ROOT_DIR, filename)
            tmp_path = os.path.join(TMP_DIR, filename)
            
            try:
                urllib.request.urlretrieve(GITHUB_RAW_URL + filename, tmp_path)
            except: continue

            if os.path.exists(local_path):
                if get_file_hash(local_path) != get_file_hash(tmp_path):
                    print(m["updating"].format(filename))
                    shutil.copy2(tmp_path, local_path)
                else:
                    print(m["no_change"].format(filename))
            else:
                shutil.copy2(tmp_path, local_path)
    finally:
        print(m["cleanup"])
        shutil.rmtree(TMP_DIR)
        print(m["done"])

if __name__ == "__main__":
    run_update()
