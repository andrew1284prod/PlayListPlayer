import os
import sys
import json
import re
import math
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QLineEdit, QSlider, QCheckBox, QPushButton, 
                             QComboBox, QGridLayout, QHBoxLayout, QColorDialog, QDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QLinearGradient, QColor, QPalette, QBrush

# Относительные пути
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(ROOT_DIR, "configs")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
CUSTOM_PATH = os.path.join(CONFIG_DIR, "custom.json")

os.makedirs(CONFIG_DIR, exist_ok=True)

STRINGS = {
    "ru": {
        "title": "Playlist Player Settings",
        "url_label": "Ссылка на плейлист YouTube",
        "quality_label": "Качество аудио",
        "vol_label": "Громкость",
        "shuffle": "Перемешать",
        "loop": " Повтор",
        "prefetch": "Предзагрузка",
        "gapless": "Без пауз",
        "loudnorm": "Нормализация",
        "save": "СОХРАНИТЬ КОНФИГ ✨",
        "saved_msg": "УСПЕШНО СОХРАНЕНО! ✅",
        "custom_btn": "ДИЗАЙН 🎨"
    },
    "en": {
        "title": "Playlist Player Settings",
        "url_label": "YouTube Playlist Link",
        "quality_label": "Audio Quality",
        "vol_label": "Volume",
        "shuffle": "Shuffle",
        "loop": "Loop Playlist",
        "prefetch": "Prefetch",
        "gapless": "Gapless Audio",
        "loudnorm": "Loudnorm",
        "save": "SAVE CONFIG ✨",
        "saved_msg": "CONFIG SAVED! ✅",
        "custom_btn": "DESIGN 🎨"
    }
}

class ModernConfigApp(QWidget):
    def __init__(self):
        super().__init__()
        self.lang = "ru"
        self.color1 = QColor("#1e1e2e")
        self.color2 = QColor("#5865f2")
        self.anim_speed = 0
        self.anim_step = 0.0
        
        self.setWindowTitle("Playlist Player Config")
        self.setFixedSize(500, 660)
        
        self.load_custom_config()
        self.init_ui()
        self.load_settings()
        self.update_ui_text()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_bg)
        if self.anim_speed > 0:
            self.timer.start(16)

    def load_custom_config(self):
        if os.path.exists(CUSTOM_PATH):
            try:
                with open(CUSTOM_PATH, 'r') as f:
                    c = json.load(f)
                    self.color1 = QColor(c.get("color1", "#1e1e2e"))
                    self.color2 = QColor(c.get("color2", "#5865f2"))
                    self.anim_speed = c.get("speed", 0)
            except: pass

    def save_custom_config(self):
        conf = {"color1": self.color1.name(), "color2": self.color2.name(), "speed": self.anim_speed}
        with open(CUSTOM_PATH, 'w') as f:
            json.dump(conf, f, indent=4)

    def animate_bg(self):
        self.anim_step += self.anim_speed / 500
        if self.anim_step > 1.0: self.anim_step = 0
        factor = (math.sin(self.anim_step * 2 * math.pi) + 1) / 2
        grad = QLinearGradient(0, 0, 500, 680)
        grad.setColorAt(0, self.color1)
        grad.setColorAt(factor, self.color2)
        grad.setColorAt(1, self.color1)
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(grad))
        self.setPalette(palette)

    def init_ui(self):
        self.setAutoFillBackground(True)
        self.main_layout = QVBoxLayout()
        # Отступы: слева, сверху, справа, снизу (снизу чуть меньше для подписи)
        self.main_layout.setContentsMargins(35, 20, 35, 10)
        self.main_layout.setSpacing(10)

        # Верхняя панель: Выбор языка и кнопка Дизайна
        top_bar = QHBoxLayout()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Русский", "English"])
        self.lang_combo.currentIndexChanged.connect(self.change_lang)
        self.lang_combo.setStyleSheet("background: rgba(255,255,255,0.1); color: white; border-radius: 5px; padding: 5px;")
        
        self.custom_btn = QPushButton()
        self.custom_btn.clicked.connect(self.show_design_dialog)
        self.custom_btn.setStyleSheet("background: rgba(255,255,255,0.2); color: white; border-radius: 5px; padding: 5px 15px; font-weight: bold;")
        
        top_bar.addWidget(self.lang_combo)
        top_bar.addStretch()
        top_bar.addWidget(self.custom_btn)
        self.main_layout.addLayout(top_bar)

        # Заголовок проги
        self.title_label = QLabel("Playlist Player")
        self.title_label.setStyleSheet("font-size: 26px; font-weight: bold; color: white; margin: 15px 0;")
        self.main_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Поле ввода URL
        self.l_url = QLabel()
        self.main_layout.addWidget(self.l_url)
        self.url_input = QLineEdit()
        self.url_input.setStyleSheet("background: rgba(0,0,0,0.4); border-radius: 8px; padding: 12px; color: white; border: 1px solid #5865f2;")
        self.main_layout.addWidget(self.url_input)

        # Выбор качества
        self.l_qual = QLabel()
        self.main_layout.addWidget(self.l_qual)
        self.quality_combo = QComboBox()
        self.quality_map = {"Best": "bestaudio", "Balanced": "bestaudio[abr<=192]", "Potato": "worstaudio"}
        self.quality_combo.addItems(self.quality_map.keys())
        self.quality_combo.setStyleSheet("background: rgba(0,0,0,0.3); color: white; padding: 8px; border-radius: 5px;")
        self.main_layout.addWidget(self.quality_combo)

        # Ползунок громкости
        self.vol_text = QLabel()
        self.main_layout.addWidget(self.vol_text)
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.valueChanged.connect(self.update_vol_label)
        self.main_layout.addWidget(self.vol_slider)

        # Сетка чекбоксов (Перемешать, Повтор и т.д.)
        grid = QGridLayout()
        self.shuffle_cb = QCheckBox(); self.loop_cb = QCheckBox()
        self.prefetch_cb = QCheckBox(); self.gapless_cb = QCheckBox(); self.norm_cb = QCheckBox()
        self.cbs = [self.shuffle_cb, self.loop_cb, self.prefetch_cb, self.gapless_cb, self.norm_cb]
        for i, cb in enumerate(self.cbs):
            cb.setStyleSheet("color: white; font-size: 14px;")
            grid.addWidget(cb, i // 2, i % 2)
        self.main_layout.addLayout(grid)

        # Кнопка сохранения
        self.save_btn = QPushButton()
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setStyleSheet("background: #2ecc71; color: white; font-weight: bold; padding: 18px; border-radius: 12px; margin-top: 20px;")
        self.main_layout.addWidget(self.save_btn)

        # Пружина, чтобы прижать футер к самому низу окна
        self.main_layout.addStretch()

        # Футер с твоей ссылкой
        self.footer = QLabel('<a href="https://github.com/andrew1284prod/playlistplayer" style="color: rgba(255, 255, 255, 0.4); text-decoration: none;">By andrew1284prod</a>')
        self.footer.setOpenExternalLinks(True) # Открывает браузер по клику
        self.footer.setStyleSheet("font-size: 20px; font-style: italic; margin-top: 10px;")
        self.main_layout.addWidget(self.footer, alignment=Qt.AlignmentFlag.AlignLeft)

        self.setLayout(self.main_layout)

    def show_design_dialog(self):
        d = QDialog(self)
        d.setWindowTitle("Design")
        d.setFixedSize(300, 250)
        d.setStyleSheet("background: #232323; color: white;")
        layout = QVBoxLayout()
        btn_c1 = QPushButton(f"Цвет 1: {self.color1.name()}"); btn_c1.clicked.connect(lambda: self.pick_color(1, btn_c1))
        btn_c2 = QPushButton(f"Цвет 2: {self.color2.name()}"); btn_c2.clicked.connect(lambda: self.pick_color(2, btn_c2))
        lbl_speed = QLabel(f"Скорость: {self.anim_speed}")
        sl_speed = QSlider(Qt.Orientation.Horizontal); sl_speed.setRange(0, 50); sl_speed.setValue(self.anim_speed)
        sl_speed.valueChanged.connect(lambda v: self.set_anim_speed(v, lbl_speed))
        btn_ok = QPushButton("ОК"); btn_ok.clicked.connect(d.accept)
        for w in [btn_c1, btn_c2, lbl_speed, sl_speed, btn_ok]: layout.addWidget(w)
        d.setLayout(layout); d.exec()

    def pick_color(self, n, btn):
        color = QColorDialog.getColor()
        if color.isValid():
            if n == 1: self.color1 = color
            else: self.color2 = color
            btn.setText(f"Цвет {n}: {color.name()}"); self.save_custom_config()

    def set_anim_speed(self, v, label):
        self.anim_speed = v; label.setText(f"Скорость: {v}")
        if v > 0: self.timer.start(16) if not self.timer.isActive() else None
        else: self.timer.stop()
        self.save_custom_config()

    def update_vol_label(self, v): self.vol_text.setText(f"{STRINGS[self.lang]['vol_label']}: {v}%")

    def update_ui_text(self):
        s = STRINGS[self.lang]
        self.l_url.setText(s["url_label"]); self.l_qual.setText(s["quality_label"])
        self.update_vol_label(self.vol_slider.value())
        self.shuffle_cb.setText(s["shuffle"]); self.loop_cb.setText(s["loop"])
        self.prefetch_cb.setText(s["prefetch"]); self.gapless_cb.setText(s["gapless"])
        self.norm_cb.setText(s["loudnorm"]); self.save_btn.setText(s["save"]); self.custom_btn.setText(s["custom_btn"])

    def change_lang(self, index): self.lang = "ru" if index == 0 else "en"; self.update_ui_text()

    def load_settings(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as f:
                    d = json.load(f); self.lang = d.get("lang", "ru")
                    self.lang_combo.setCurrentIndex(0 if self.lang == "ru" else 1)
                    self.url_input.setText(d.get("playlist_url", ""))
                    self.vol_slider.setValue(d.get("volume", 70))
                    for cb, key in zip(self.cbs, ["shuffle", "loop", "prefetch", "gapless", "loudnorm"]):
                        cb.setChecked(d.get(key, True))
            except: pass

    def save_settings(self):
        match = re.search(r"list=([A-Za-z0-9_-]+)", self.url_input.text())
        url = f"https://www.youtube.com/playlist?list={match.group(1)}" if match else self.url_input.text()
        conf = {
            "lang": self.lang, "playlist_url": url, "volume": self.vol_slider.value(),
            "ytdl_format": self.quality_map[self.quality_combo.currentText()],
            "shuffle": self.shuffle_cb.isChecked(), "loop": self.loop_cb.isChecked(),
            "prefetch": self.prefetch_cb.isChecked(), "gapless": self.gapless_cb.isChecked(), "loudnorm": self.norm_cb.isChecked()
        }
        with open(CONFIG_PATH, 'w') as f: json.dump(conf, f, indent=4)
        self.save_btn.setText(STRINGS[self.lang]["saved_msg"])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernConfigApp(); window.show()
    sys.exit(app.exec())
