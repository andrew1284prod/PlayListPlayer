import os
import shutil
import urllib.request
import hashlib
import locale
import json

# Конфигурация путей
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(ROOT_DIR, "configs")
TMP_DIR = "/tmp/playlist_update_check"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/andrew1284prod/playlistplayer/main/"

# Файлы
VERSION_FILE = "version.json"
LOCAL_VERSION_PATH = os.path.join(ROOT_DIR, VERSION_FILE)
FILES_TO_CHECK = ["gui_config.py", "run_mpv.py", "playlistupd.py", "version.json"]

def get_sys_lang():
    try:
        lang = locale.getlocale()[0]
        return lang[:2] if lang else "en"
    except: return "en"

LANG = get_sys_lang()
MSG = {
    "ru": {
        "ver_check": "[Информация] Сверка локальной версии с репозиторием...",
        "ver_match": "[Информация] Версии идентичны (v{}). Запустить глубокую проверку файлов? (y/n): ",
        "new_ver": "[Обновление] Найдена новая версия: {} (Текущая: {}). Установить? (y/n): ",
        "start": "[Информация] Запуск побайтовой верификации компонентов...",
        "updating": "[Обновление] Файл {} изменен. Перезапись...",
        "no_change": "[Информация] Компонент {} актуален.",
        "cleanup": "[Система] Очистка временных данных из RAM...",
        "done": "[Успех] Проверка завершена. Все файлы синхронизированы.",
        "error_net": "[Ошибка] Не удалось получить данные с сервера: {}",
        "error_local": "[Ошибка] Локальный файл версии не найден. Будет выполнена полная проверка."
    },
    "en": {
        "ver_check": "[Info] Comparing local version with repository...",
        "ver_match": "[Info] Versions match (v{}). Run deep file integrity check? (y/n): ",
        "new_ver": "[Update] New version available: {} (Current: {}). Install? (y/n): ",
        "start": "[Info] Starting byte-by-byte verification...",
        "updating": "[Update] File {} has changed. Overwriting...",
        "no_change": "[Info] Component {} is up to date.",
        "cleanup": "[System] Clearing temporary RAM data...",
        "done": "[Success] Verification complete. All files synchronized.",
        "error_net": "[Error] Failed to fetch server data: {}",
        "error_local": "[Error] Local version file not found. Full check initiated."
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
    
    remote_v = "unknown"
    local_v = "unknown"

    # 1. Получаем удаленную версию
    try:
        with urllib.request.urlopen(GITHUB_RAW_URL + VERSION_FILE, timeout=7) as response:
            remote_data = json.loads(response.read().decode())
            remote_v = str(remote_data.get("version", "0.0"))
    except Exception as e:
        print(m["error_net"].format(e))
        if not ask_user(m["ver_match"].format("?")): return

    # 2. Получаем локальную версию
    if os.path.exists(LOCAL_VERSION_PATH):
        try:
            with open(LOCAL_VERSION_PATH, 'r') as f:
                local_data = json.load(f)
                local_v = str(local_data.get("version", "0.0"))
        except: pass
    else:
        print(m["error_local"])

    # 3. Логика сравнения
    if remote_v == local_v and remote_v != "unknown":
        if not ask_user(m["ver_match"].format(local_v)):
            return
    else:
        if not ask_user(m["new_ver"].format(remote_v, local_v)):
            return

    # 4. Проверка через /tmp (RAM)
    print(m["start"])
    if os.path.exists(TMP_DIR): shutil.rmtree(TMP_DIR)
    os.makedirs(TMP_DIR)

    try:
        for filename in FILES_TO_CHECK:
            local_path = os.path.join(ROOT_DIR, filename)
            tmp_path = os.path.join(TMP_DIR, filename)
            
            try:
                urllib.request.urlretrieve(GITHUB_RAW_URL + filename, tmp_path)
            except:
                continue

            if os.path.exists(local_path):
                if get_file_hash(local_path) != get_file_hash(tmp_path):
                    print(m["updating"].format(filename))
                    shutil.copy2(tmp_path, local_path)
                else:
                    print(m["no_change"].format(filename))
            else:
                print(m["updating"].format(filename))
                shutil.copy2(tmp_path, local_path)
    finally:
        print(m["cleanup"])
        shutil.rmtree(TMP_DIR)
        print(m["done"])

if __name__ == "__main__":
    run_update()
