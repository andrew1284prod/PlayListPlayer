import os
import json
import subprocess
import threading
import time
import locale

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, "configs", "config.json")
SOCKET_PATH = "/tmp/mpv-socket"

def get_sys_lang():
    try:
        lang = locale.getlocale()[0][:2]
        return lang if lang in ["ru", "en"] else "en"
    except: return "en"

LANG = get_sys_lang()
MSG = {
    "ru": {
        "err_url": "[Ошибка] Ссылка не найдена. Запустите playlistconfig.",
        "playing": "Играет",
        "start": "[Система] Запуск сессии (Управление: Клавиатура -> MPV)..."
    },
    "en": {
        "err_url": "[Error] URL not found. Run playlistconfig.",
        "playing": "Playing",
        "start": "[System] Starting session (Focus: MPV Controls)..."
    }
}

def load_config():
    if not os.path.isfile(CONFIG_PATH):
        return {"volume": 70, "shuffle": True, "loop": True, "playlist_url": ""}
    with open(CONFIG_PATH, 'r') as f: return json.load(f)

def send_notification():
    conf = load_config()
    if not conf.get('allow_notifications', True): # Если выключено — ливаем
        return

    time.sleep(5)
    last_title = ""
    while True:
        try:
            if os.path.exists(SOCKET_PATH):
                cmd = f'echo \'{{"command": ["get_property", "media-title"]}}\' | socat - {SOCKET_PATH}'
                res = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
                data = json.loads(res)
                current_title = data.get("data", "")
                if current_title and current_title != last_title:
                    subprocess.run(["notify-send", "-i", "audio-speakers", "Playlist Player", f"{MSG[LANG]['playing']}: {current_title}"])
                    last_title = current_title
        except: pass
        time.sleep(3)
        
def run_stuff():
    conf = load_config()
    if not conf.get('playlist_url'):
        print(MSG[LANG]["err_url"])
        return

    print(MSG[LANG]["start"])

    # Аргументы MPV
    mpv_args = [
        "mpv",
        "--no-video",
        f"--input-ipc-server={SOCKET_PATH}",
        f"--volume={conf.get('volume', 70)}",
        f"--ytdl-format={conf.get('ytdl_format', 'bestaudio')}",
        "--term-osd-bar=yes"
    ]

    if conf.get('shuffle'): mpv_args.append("--shuffle")
    if conf.get('loop'): mpv_args.append("--loop-playlist=inf")
    if conf.get('prefetch'): mpv_args.append("--prefetch-playlist=yes")
    if conf.get('gapless'): mpv_args.append("--gapless-audio=yes")
    if conf.get('loudnorm'): mpv_args.append("--af=loudnorm")
    
    mpv_args.append(f"\"{conf.get('playlist_url')}\"")
    mpv_cmd_str = " ".join(mpv_args)

    threading.Thread(target=send_notification, daemon=True).start()

    # Сборка команды TMUX:
    # 1. Создаем сессию с CAVA (панель 0)
    # 2. Сплитим окно для MPV (панель 1)
    # 3. ВАЖНО: Выбираем панель 1 (select-pane -t 1), чтобы хоткеи летели в MPV
    tmux_cmd = [
        "tmux", "new-session", "-d", "-s", "playlist_session", "cava", ";",
        "split-window", "-v", "-p", "35", mpv_cmd_str, ";",
        "select-pane", "-t", "1", ";", 
        "attach-session", "-t", "playlist_session"
    ]

    try:
        # Убиваем старую сессию, если она зависла
        subprocess.run(["tmux", "kill-session", "-t", "playlist_session"], capture_output=True)
        subprocess.run(tmux_cmd)
    except Exception as e:
        print(f"[Критическая ошибка]: {e}")

if __name__ == "__main__":
    run_stuff()
