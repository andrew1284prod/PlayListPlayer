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
VERSION_FILE = "version.json"

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
        "ver_check": "[Информация] Сверка версий с репозиторием...",
        "ver_match": "[Информация] Версии совпадают. Запустить глубокую проверку файлов? (y/n): ",
        "new_ver": "[Обновление] Найдена новая версия. Начать установку? (y/n): ",
        "start": "[Информация] Запуск процесса верификации хеш-сумм...",
        "updating": "[Обновление] Обнаружено различие в {}. Перезапись...",
        "no_change": "[Информация] Компонент {} идентичен оригиналу.",
        "cleanup": "[Система] Удаление временных данных из RAM...",
        "done": "[Успех] Проверка завершена успешно.",
        "error": "[Ошибка] Сбой сетевого соединения или доступа к файлам: {}"
    },
    "en": {
        "ver_check": "[Info] Checking version compatibility...",
        "ver_match": "[Info] Versions match. Run deep file integrity check? (y/n): ",
        "new_ver": "[Update] New version detected. Proceed with installation? (y/n): ",
        "start": "[Info] Starting hash verification process...",
        "updating": "[Update] Difference found in {}. Overwriting...",
        "no_change": "[Info] Component {} is valid.",
        "cleanup": "[System] Clearing temporary data from RAM...",
        "done": "[Success] Verification complete.",
        "error": "[Error] Connection or file access failure: {}"
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
    
    # Пытаемся получить версию с GitHub
    try:
        with urllib.request.urlopen(GITHUB_RAW_URL + VERSION_FILE, timeout=5) as response:
            remote_version_data = json.loads(response.read().decode())
            remote_version = str(remote_version_data.get("version", "1.0"))
    except Exception as e:
        print(m["error"].format(e))
        # Если не смогли проверить версию, предлагаем сразу глубокую проверку
        if not ask_user(m["ver_match"]): return
        remote_version = "unknown"

    # Локальная версия (можно хранить в коде или в configs/config.json)
    # Для простоты считаем текущую 1.0. Если хочешь автоматику — нужно создать local_version.json
    local_version = "1.0" 

    if remote_version == local_version:
        if not ask_user(m["ver_match"]):
            return
    else:
        if not ask_user(m["new_ver"]):
            return

    # Глубокая проверка
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
                print(f"[!] Не удалось проверить {filename}")
                continue

            if os.path.exists(local_path):
                # Сверяем по байтам (SHA256)
                if get_file_hash(local_path) != get_file_hash(tmp_path):
                    print(m["updating"].format(filename))
                    shutil.copy2(tmp_path, local_path)
                else:
                    print(m["no_change"].format(filename))
            else:
                # Если файла вообще нет — качаем
                shutil.copy2(tmp_path, local_path)
    finally:
        print(m["cleanup"])
        shutil.rmtree(TMP_DIR)
        print(m["done"])

if __name__ == "__main__":
    run_update()
