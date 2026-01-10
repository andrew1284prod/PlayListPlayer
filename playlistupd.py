import urllib.request
import json
import os
import locale

GITHUB_RAW = "https://raw.githubusercontent.com/andrew1284prod/playlistplayer/main"
INSTALL_DIR = os.path.dirname(os.path.abspath(__file__))
FILES = ["run_mpv.py", "gui_config.py", "version.json", "playlistupd.py"]

# Переводы для апдейтера
UPD_LANGS = {
    "ru": {"upd": "Обнова!", "latest": "У тебя всё свежее, бро 🤙", "err": "Ошибка сети"},
    "uk": {"upd": "О, оновлення!", "latest": "У тебе все свіже, бро 🤙", "err": "Помилка мережі"},
    "en": {"upd": "New update available!", "latest": "You are up to date, bro 🤙", "err": "Network error"}
}
sys_lang = locale.getdefaultlocale()[0][:2] if locale.getdefaultlocale()[0] else "en"
UT = UPD_LANGS.get(sys_lang, UPD_LANGS["en"])

def update():
    try:
        with urllib.request.urlopen(f"{GITHUB_RAW}/version.json") as url:
            remote = json.loads(url.read().decode())
        
        path = os.path.join(INSTALL_DIR, "version.json")
        local = {"version": "0.0"}
        if os.path.exists(path):
            with open(path, "r") as f: local = json.load(f)

        if remote["version"] != local["version"]:
            print(f"{UT['upd']} {local['version']} -> {remote['version']}")
            for file in FILES:
                urllib.request.urlretrieve(f"{GITHUB_RAW}/{file}", os.path.join(INSTALL_DIR, file))
            print("OK! ✅")
        else:
            print(UT["latest"])
    except:
        print(UT["err"])

if __name__ == "__main__":
    update()
