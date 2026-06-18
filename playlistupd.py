Отличная идея для расширения функционала! Добавление перезаписи алиасов прямо в обновлятор (`playlistupd.py`) делает его полноценным сервисным инструментом.

Поскольку в самом скрипте обновлятора изначально **не было** кода для работы с алиасами (он был только в установщиках и GUI), я полностью интегрировал этот механизм в логику обновления.

### Что добавлено и изменено:

1. **Безопасная перезапись:** Скрипт теперь полностью вычищает старый блок алиасов плеера (`# PlaylistPlayer` или `# PlaylistPlayer Aliases`) из `.bashrc`/`.zshrc` перед записью новых. Это защищает конфиг от дублирования.
2. **Фикс пробелов:** Пути бережно заворачиваются в одинарные кавычки внутри двойных (как мы и делали ранее).
3. **Финальный интерактивный опрос:** Скрипт выполнит проверку файлов, очистит `/tmp`, а затем спросит: *«Хотите обновить алиасы?»*. Если ответить «Да», он предложит кастомный вариант или быстро пропишет дефолтные (`plp`, `plpcfg`, `plpupd`).
4. **Замена `except:` на `except Exception:**` для соблюдения хорошего тона в Python.

### Полный код `playlistupd.py` с новыми возможностями:

```python
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
    except Exception: 
        return "en"

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
        "error_local": "[Ошибка] Локальный файл версии не найден. Будет выполнена полная проверка.",
        "ask_alias": "\n[Конфиг] Хотите обновить/пересоздать алиасы? (y/n): ",
        "ask_custom": "[Конфиг] Поставить кастомные имена для алиасов? (y/n): ",
        "alias_player": "Введите команду для запуска ПЛЕЕРА (по умолчанию plp): ",
        "alias_config": "Введите команду для запуска КОНФИГУРАТОРА (по умолчанию plpcfg): ",
        "alias_update": "Введите команду для запуска ОБНОВЛЕНИЯ (по умолчанию plpupd): ",
        "alias_done": "[Успех] Алиасы успешно обновлены в {}!"
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
        "error_local": "[Error] Local version file not found. Full check initiated.",
        "ask_alias": "\n[Config] Do you want to update/recreate aliases? (y/n): ",
        "ask_custom": "[Config] Use custom names for aliases? (y/n): ",
        "alias_player": "Enter alias for PLAYER (default: plp): ",
        "alias_config": "Enter alias for CONFIGURATOR (default: plpcfg): ",
        "alias_update": "Enter alias for UPDATE (default: plpupd): ",
        "alias_done": "[Success] Aliases successfully updated in {}!"
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

def update_shell_aliases(m):
    """Очищает старые и прописывает новые (дефолтные или кастомные) алиасы"""
    shell_path = os.environ.get("SHELL", "")
    rc_file = os.path.expanduser("~/.zshrc" if "zsh" in shell_path else "~/.bashrc")
    
    if not os.path.exists(rc_file):
        return

    # Имена по умолчанию
    name_plp = "plp"
    name_cfg = "plpcfg"
    name_upd = "plpupd"

    if ask_user(m["ask_custom"]):
        custom_plp = input(m["alias_player"]).strip()
        custom_cfg = input(m["alias_config"]).strip()
        custom_upd = input(m["alias_update"]).strip()
        
        if custom_plp: name_plp = custom_plp
        if custom_cfg: name_cfg = custom_cfg
        if custom_upd: name_upd = custom_upd

    # Чистим старые записи PlaylistPlayer, чтобы не плодить дубликаты
    with open(rc_file, "r") as f:
        lines = f.readlines()

    clean_lines = []
    skip = False
    for line in lines:
        # Если находим маркер начала нашего блока — включаем пропуск строк
        if "# PlaylistPlayer" in line:
            skip = True
            continue
        # Если пропуск включен, но пошли другие строки (или пустая строка после блока алиасов)
        if skip and not line.startswith("alias ") and line.strip() != "":
            skip = False
        if not skip:
            clean_lines.append(line)

    # Собираем свежие алиасы с правильным экранированием путей
    alias_data = (
        f'\n# PlaylistPlayer\n'
        f'alias {name_plp}="python3 \'{os.path.join(ROOT_DIR, "run_mpv.py")}\'"\n'
        f'alias {name_cfg}="python3 \'{os.path.join(ROOT_DIR, "gui_config.py")}\'"\n'
        f'alias {name_upd}="python3 \'{os.path.join(ROOT_DIR, "playlistupd.py")}\'"\n'
    )

    # Записываем обратно чистый конфиг терминала + новый блок алиасов
    with open(rc_file, "w") as f:
        f.writelines(clean_lines)
        f.write(alias_data)
        
    print(m["alias_done"].format(os.path.basename(rc_file)))

def run_update():
    m = MSG.get(LANG, MSG["en"])
    print(m["ver_check"])
    
    remote_v = "unknown"
    local_v = "unknown"
    should_deep_check = False

    # 1. Получаем удаленную версию
    try:
        with urllib.request.urlopen(GITHUB_RAW_URL + VERSION_FILE, timeout=7) as response:
            remote_data = json.loads(response.read().decode())
            remote_v = str(remote_data.get("version", "0.0"))
    except Exception as e:
        print(m["error_net"].format(e))
        if not ask_user(m["ver_match"].format("?")): 
            should_deep_check = False
        else:
            should_deep_check = True

    # 2. Получаем локальную версию
    if os.path.exists(LOCAL_VERSION_PATH):
        try:
            with open(LOCAL_VERSION_PATH, 'r') as f:
                local_data = json.load(f)
                local_v = str(local_data.get("version", "0.0"))
        except Exception: 
            pass
    else:
        print(m["error_local"])
        should_deep_check = True

    # 3. Логика сравнения (если не ушли в форсированную проверку из-за ошибок)
    if not should_deep_check:
        if remote_v == local_v and remote_v != "unknown":
            should_deep_check = ask_user(m["ver_match"].format(local_v))
        else:
            should_deep_check = ask_user(m["new_ver"].format(remote_v, local_v))

    # 4. Проверка через /tmp (RAM), только если нужно
    if should_deep_check:
        print(m["start"])
        if os.path.exists(TMP_DIR): 
            shutil.rmtree(TMP_DIR)
        os.makedirs(TMP_DIR)

        try:
            for filename in FILES_TO_CHECK:
                local_path = os.path.join(ROOT_DIR, filename)
                tmp_path = os.path.join(TMP_DIR, filename)
                
                try:
                    urllib.request.urlretrieve(GITHUB_RAW_URL + filename, tmp_path)
                except Exception:
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

    # 5. Секция управления алиасами в самом конце выполнения скрипта
    if ask_user(m["ask_alias"]):
        update_shell_aliases(m)

if __name__ == "__main__":
    run_update()

```
