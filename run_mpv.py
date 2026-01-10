import os
import json
import subprocess
import threading
import time
import sys

# Определяем пути относительно файла скрипта
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, "configs", "config.json")
SOCKET_PATH = "/tmp/mpv-socket"

def load_config():
    if not os.path.isfile(CONFIG_PATH):
        return {"volume": 70, "shuffle": True, "loop": True, "prefetch": True, "gapless": True, "playlist_url": ""}
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def send_notification():
    """Мониторим треки через сокет"""
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
                    subprocess.run(["notify-send", "-i", "audio-speakers", "🎵 Now Playing", current_title])
                    last_title = current_title
        except: pass
        time.sleep(3)

def run_stuff():
    conf = load_config()
    
    if not conf.get('playlist_url'):
        print("Шо, ссылки нет? Зайди в playlistconfig и сохрани URL сначала!")
        return

    mpv_cmd = [
        "mpv", "--no-video", f"--input-ipc-server={SOCKET_PATH}",
        f"--volume={conf.get('volume', 70)}",
        f"--ytdl-format={conf.get('ytdl_format', 'bestaudio')}",
        "--ytdl-raw-options=yes-playlist=", "--term-osd-bar=yes"
    ]
    
    if conf.get('shuffle'): mpv_cmd.append("--shuffle")
    if conf.get('loop'): mpv_cmd.append("--loop-playlist=inf")
    if conf.get('prefetch'): mpv_cmd.append("--prefetch-playlist=yes")
    if conf.get('gapless'): mpv_cmd.append("--gapless-audio=yes")
    if conf.get('loudnorm'): mpv_cmd.append("--af=loudnorm")
    mpv_cmd.append(conf.get('playlist_url'))

    threading.Thread(target=send_notification, daemon=True).start()

    # Склеиваем команду для tmux
    mpv_str = " ".join(f"'{c}'" if " " in c or "http" in c else c for c in mpv_cmd)
    
    # tmux: cava сверху (80%), mpv снизу (20%)
    tmux_cmd = f"tmux new-session -d -s playlist_session 'cava' \; split-window -v -p 20 \"{mpv_str}\" \; select-pane -t 1 \; attach-session -t playlist_session"
    
    try:
        subprocess.run(tmux_cmd, shell=True)
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    run_stuff()
