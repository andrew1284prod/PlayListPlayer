# PlaylistPlayer (Linux CLI)


**ENG**

**PlaylistPlayer** is a lightweight terminal player for playing YouTube playlists.
No browsers, no heavy GUIs, and no background bloat. Just pure audio, visualization, the terminal, and your depression.
By the way, I removed all emojis from this ReadMe so you could truly feel the depression of my vibe-code after I abandoned this project for 6 months.

## Tech Stack

* **MPV** — the audio playback core.
* **YT-DLP** — the engine for fetching streams.
* **CAVA** — a cross-platform audio visualizer.
* **TMUX** — terminal layout management.
* **PyQt6** — a modern settings interface.


**RU**

**PlaylistPlayer** — это легковесный терминальный плеер для воспроизведения плейлистов YouTube. 
Никаких браузеров, тяжелых GUI и лишнего мусора в фоне. Только чистый звук, визуализация, терминал и ваша депрессия.
Я кстати убрал все эмодзи с этого ReadMe, чтобы вы чувствовали депрессию моего вайбкода после того, как я забил на этот проект на 6 месяцев.

## Технологический стек
* **MPV** — ядро воспроизведения аудио.
* **YT-DLP** — движок для получения потоков.
* **CAVA** — кроссплатформенный аудио-визуализатор.
* **TMUX** — управление раскладкой терминала.
* **PyQt6** — современный интерфейс настроек.

---

## Установка / Installation
Arch/Arch based systems (native, pacman):
```bash
git clone --branch installators --single-branch https://github.com/andrew1284prod/PlayListPlayer.git && cd PlayListPlayer && python setup.py && rm -rf PlayListPlayer
```
Ubuntu/Debian based systems (native, apt) :
```bash
git clone --branch installators --single-branch https://github.com/andrew1284prod/PlayListPlayer.git && cd PlayListPlayer && python apt_setup.py && rm -rf PlayListPlayer
```
Fedora based systems (native, dnf) :
```bash
git clone --branch installators --single-branch https://github.com/andrew1284prod/PlayListPlayer.git && cd PlayListPlayer && python3 dnf_setup.py && rm -rf PlayListPlayer
```
