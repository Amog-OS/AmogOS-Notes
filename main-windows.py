import sys
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from PyQt6 import QtGui
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QScrollArea, QTextEdit,
                             QLineEdit, QMessageBox, QDialog, QDialogButtonBox, QFrame,
                             QToolButton, QGraphicsOpacityEffect, QCheckBox,
                             QGraphicsDropShadowEffect, QGridLayout, QStackedWidget, QComboBox,
                             QColorDialog)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QRect, QEasingCurve, QTimer, QByteArray, QPoint, QMimeData
from PyQt6.QtGui import (QPainter, QLinearGradient, QColor, QFont, QIcon,
                         QPainterPath, QFontMetrics, QPalette, QPixmap, QDrag)

APP_NAME = "AmogOSNotes"
DATA_DIR = Path.home() / f".{APP_NAME.lower()}_data"

try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "buddies").mkdir(parents=True, exist_ok=True)
except OSError as e:
    print(f"Error creating data directory {DATA_DIR} or buddies subdirectory: {e}")
    sys.exit(1)

NOTES_FILE = DATA_DIR / "notes.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
BUDDIES_FOLDER = DATA_DIR / "buddies"

DEFAULT_ACCENT_COLOR = "#FF69B4"
DEFAULT_THEME = "light"
DEFAULT_AMOGUS_JOKES = True
DEFAULT_BUDDY = ""

THEMES = {
    "light": {
        "BACKGROUND_SIDEBAR": "#F5F5F7",
        "BACKGROUND_MAIN": "#FFFFFF",
        "BACKGROUND_CARD": "#FFFFFF",
        "BACKGROUND_CARD_PREVIEW": "#F9F9F9",
        "BACKGROUND_POPUP": "#FDFDFD",
        "TEXT_PRIMARY": "#000000",
        "TEXT_SECONDARY": "#8A8A8E",
        "TEXT_TERTIARY": "#AEAEB2",
        "TEXT_BUTTON_ACCENT": "#FFFFFF",
        "BORDER_LIGHT": "#EAEAEB",
        "BORDER_MEDIUM": "#D1D1D6",
        "SCROLLBAR_BG": "#F5F5F7",
        "SCROLLBAR_HANDLE": "#D1D1D6",
        "SCROLLBAR_HANDLE_HOVER": "#AEAEB2",
        "SHADOW_COLOR": "rgba(0, 0, 0, 25)",
        "HIGHLIGHT_SIDEBAR": "#FFD700"
    },
    "dark": {
        "BACKGROUND_SIDEBAR": "#1E1E1E",
        "BACKGROUND_MAIN": "#121212",
        "BACKGROUND_CARD": "#1C1C1E",
        "BACKGROUND_CARD_PREVIEW": "#28282A",
        "BACKGROUND_POPUP": "#222224",
        "TEXT_PRIMARY": "#FFFFFF",
        "TEXT_SECONDARY": "#8A8A8E",
        "TEXT_TERTIARY": "#636366",
        "TEXT_BUTTON_ACCENT": "#FFFFFF",
        "BORDER_LIGHT": "#38383A",
        "BORDER_MEDIUM": "#4A4A4C",
        "SCROLLBAR_BG": "#1E1E1E",
        "SCROLLBAR_HANDLE": "#4A4A4C",
        "SCROLLBAR_HANDLE_HOVER": "#636366",
        "SHADOW_COLOR": "rgba(0, 0, 0, 0)",
        "HIGHLIGHT_SIDEBAR": ""
    },
    "amoled": {
        "BACKGROUND_SIDEBAR": "#000000",
        "BACKGROUND_MAIN": "#000000",
        "BACKGROUND_CARD": "#0A0A0A",
        "BACKGROUND_CARD_PREVIEW": "#111111",
        "BACKGROUND_POPUP": "#080808",
        "TEXT_PRIMARY": "#E5E5E7",
        "TEXT_SECONDARY": "#8A8A8E",
        "TEXT_TERTIARY": "#5A5A5D",
        "TEXT_BUTTON_ACCENT": "#FFFFFF",
        "BORDER_LIGHT": "#2A2A2C",
        "BORDER_MEDIUM": "#3A3A3C",
        "SCROLLBAR_BG": "#000000",
        "SCROLLBAR_HANDLE": "#3A3A3C",
        "SCROLLBAR_HANDLE_HOVER": "#5A5A5D",
        "SHADOW_COLOR": "rgba(0, 0, 0, 0)",
        "HIGHLIGHT_SIDEBAR": ""
    }
}


current_user_accent_color = DEFAULT_ACCENT_COLOR
current_theme_name = DEFAULT_THEME
current_theme_colors = THEMES[DEFAULT_THEME]
enable_amogus_jokes = DEFAULT_AMOGUS_JOKES
current_buddy = DEFAULT_BUDDY


def get_contrasting_text_color(bg_hex_color):
    color = QColor(bg_hex_color)
    luminance = (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()) / 255
    return "#FFFFFF" if luminance < 0.5 else "#000000"


AMOGUS_JOKES = [
    {"title": "Sus", "content": "There is 1 impostor among us."},
    {"title": "Emergency Meeting", "content": "I saw someone vent in electrical!"},
    {"title": "Red Sus", "content": "Red was following me and acting sus."},
    {"title": "Tasks", "content": "Just finished my tasks in admin. Anyone want to buddy up?"},
    {"title": "Venting", "content": "How do I go into the vent like blue did?"},
    {"title": "Sabotage", "content": "O2 depleting. Fix sabotage!"},
    {"title": "Crewmate", "content": "I was doing my tasks in medbay, I swear!"},
    {"title": "Scan", "content": "I can prove I'm innocent. Watch me scan in medbay."},
    {"title": "Ejected", "content": "Blue was not The Impostor. 1 Impostor remains."},
    {"title": "Cafeteria", "content": "Meeting in cafeteria. Who's sus?"}
]


def get_category_color(category):
    color_map = {
        "Uncategorized": "#FFFFFF",
        "Amogus": "#FF69B4",
        "Work": "#228B22",
        "Personal": "#1E90FF",
        "Important": "#FF8C00"
    }
    return color_map.get(category, "#FFFFFF")

class ModernButton(QPushButton):
    def __init__(self, text, parent=None, icon_path=None, accent=False, is_sidebar_item=False):
        super().__init__(text, parent)
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(18, 18))

        self.setCheckable(True)

        base_style = f"""
            QPushButton {{
                border: none;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                text-align: left;
                color: {current_theme_colors['TEXT_PRIMARY']};
                background-color: transparent;
            }}
            QPushButton:hover {{
                background-color: {current_theme_colors['BORDER_LIGHT']};
            }}
            QPushButton:checked, QPushButton:pressed {{
                background-color: {current_theme_colors['HIGHLIGHT_SIDEBAR']};
                color: {current_theme_colors['TEXT_PRIMARY']};
                font-weight: bold;
            }}
        """

        accent_style = f"""
            QPushButton {{
                background-color: {current_user_accent_color};
                color: {current_theme_colors['TEXT_BUTTON_ACCENT']};
                border-radius: 8px;
                padding: 12px;
                font-size: 15px;
                font-weight: bold;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {QColor(current_user_accent_color).darker(110).name()};
            }}
        """

        self.setStyleSheet(accent_style if accent else base_style)
        if is_sidebar_item:
            self.setFixedHeight(40)

class GradientLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("San Francisco", 20, QFont.Weight.Bold))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(50)
        self.setStyleSheet(f"color: {current_theme_colors['TEXT_PRIMARY']};")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor(current_user_accent_color))
        gradient.setColorAt(1, QColor(current_theme_colors['TEXT_PRIMARY']))

        path = QPainterPath()
        font_metrics = painter.fontMetrics()
        text_width = font_metrics.horizontalAdvance(self.text())
        text_height = font_metrics.height()
        x = (self.width() - text_width) / 2
        y = (self.height() + text_height) / 2 - font_metrics.descent()
        path.addText(x, y, self.font(), self.text())
        painter.fillPath(path, gradient)

class OverlayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.3);")
        self.setGeometry(0, 0, parent.width(), parent.height())
        self.setVisible(False)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0)
        self.setGraphicsEffect(self.opacity_effect)

        self.animation = QPropertyAnimation(self.opacity_effect, QByteArray(b"opacity"))
        self.animation.setDuration(200)

    def showEvent(self, event):
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
        super().showEvent(event)

    def fadeOut(self):
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.hide)
        self.animation.start()

class NotePopup(QFrame):
    def __init__(self, parent, on_save, note_id=None, title="", content="", is_temporary=False):
        super().__init__(parent)
        self.parent = parent
        self.on_save = on_save
        self.note_id = note_id
        self.is_temporary = is_temporary

        self.overlay = OverlayWidget(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.raise_()



        parent_rect = parent.geometry()
        width = 550
        height = 380
        x = parent_rect.width() // 2 - width // 2
        y = parent_rect.height() // 2 - height // 2
        self.setGeometry(x, y, width, height)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)

        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setStartValue(QRect(x, y + 30, width, height))
        self.animation.setEndValue(QRect(x, y, width, height))
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)


        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()
        self.title_edit = QLineEdit(title)
        self.title_edit.setPlaceholderText("Note Title")
        self.title_edit.setFont(QFont("San Francisco", 16, QFont.Weight.Bold))
        header_layout.addWidget(self.title_edit, 1)

        self.close_btn = QToolButton()
        self.close_btn.setText("×")
        self.close_btn.setFont(QFont("Arial", 18))
        self.close_btn.clicked.connect(self.close)
        header_layout.addWidget(self.close_btn)
        layout.addLayout(header_layout)

        self.content_edit = QTextEdit(content)
        self.content_edit.setPlaceholderText("Start typing...")
        self.content_edit.setFont(QFont("San Francisco", 13))
        layout.addWidget(self.content_edit, 1)

        footer_layout = QHBoxLayout()
        footer_layout.addStretch(1)
        self.save_btn = QPushButton("Done")
        self.save_btn.setFont(QFont("San Francisco", 13, QFont.Weight.Medium))
        self.save_btn.clicked.connect(self.save_note)
        footer_layout.addWidget(self.save_btn)
        layout.addLayout(footer_layout)


        self.setVisible(False)

        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {current_theme_colors['BACKGROUND_POPUP']};
                border-radius: 12px;
                border: 1px solid {current_theme_colors['BORDER_MEDIUM']};
            }}
        """)
        self.title_edit.setStyleSheet(f"""
            QLineEdit {{
                font-size: 17px;
                font-weight: bold;
                border: none;
                padding: 5px 0px;
                background-color: transparent;
                color: {current_theme_colors['TEXT_PRIMARY']};
            }}
        """)
        self.close_btn.setStyleSheet(f"""
            QToolButton {{
                color: {current_theme_colors['TEXT_SECONDARY']};
                border: none;
                background-color: transparent;
                padding: 0px 5px;
            }}
            QToolButton:hover {{
                color: {current_user_accent_color};
            }}
        """)
        self.content_edit.setStyleSheet(f"""
            QTextEdit {{
                border: none;
                background-color: transparent;
                color: {current_theme_colors['TEXT_PRIMARY']};
                padding: 5px 0px;
            }}
        """)
        save_btn_text_color = get_contrasting_text_color(current_user_accent_color)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 20px;
                background-color: {current_user_accent_color};
                color: {save_btn_text_color};
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {QColor(current_user_accent_color).darker(110).name()};
            }}
        """)
        if hasattr(self, 'graphicsEffect') and isinstance(self.graphicsEffect(), QGraphicsDropShadowEffect):
            self.graphicsEffect().setColor(QColor(current_theme_colors['SHADOW_COLOR']))

    def show(self):
        self.overlay.resize(self.parent.width(), self.parent.height())
        self.overlay.show()
        super().show()
        self.animation.start()
        self.title_edit.setFocus()

    def close(self):
        self.overlay.fadeOut()
        super().close()

    def save_note(self):
        title = self.title_edit.text()
        content = self.content_edit.toPlainText()
        if not title and not content:
            self.close()
            return
        self.on_save(self.note_id, title, content, self.is_temporary)
        self.close()

class CategoryNotePopup(QFrame):
    def __init__(self, parent, on_save, note_id=None, title="", content="", is_temporary=False, categories=None, initial_category="Uncategorized"):
        super().__init__(parent)
        self.parent = parent
        self.on_save = on_save
        self.note_id = note_id
        self.is_temporary = is_temporary
        self.current_category = initial_category
        self.categories = categories or []

        self.overlay = OverlayWidget(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.raise_()


        parent_rect = parent.geometry()
        width = 550
        height = 420
        x = parent_rect.width() // 2 - width // 2
        y = parent_rect.height() // 2 - height // 2
        self.setGeometry(x, y, width, height)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setStartValue(QRect(x, y + 30, width, height))
        self.animation.setEndValue(QRect(x, y, width, height))
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)


        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()
        self.title_edit = QLineEdit(title)
        self.title_edit.setPlaceholderText("Note Title")
        self.title_edit.setFont(QFont("San Francisco", 16, QFont.Weight.Bold))
        header_layout.addWidget(self.title_edit, 1)

        self.close_btn = QToolButton()
        self.close_btn.setText("×")
        self.close_btn.setFont(QFont("Arial", 18))
        self.close_btn.clicked.connect(self.close)
        header_layout.addWidget(self.close_btn)
        layout.addLayout(header_layout)


        category_layout = QHBoxLayout()
        category_label = QLabel("Category:")
        category_label.setFont(QFont("San Francisco", 12))
        category_layout.addWidget(category_label)

        self.category_combo = QComboBox()
        self.category_combo.addItem("Uncategorized")
        for category in sorted(self.categories):
            if category != "Uncategorized":
                self.category_combo.addItem(category)


        self.category_combo.addItem("+ New Category")


        index = self.category_combo.findText(self.current_category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)

        self.category_combo.currentIndexChanged.connect(self.handle_category_selection)
        category_layout.addWidget(self.category_combo, 1)
        layout.addLayout(category_layout)


        self.temp_checkbox = QCheckBox("Mark as temporary note (auto-deletes after 30 days)")
        self.temp_checkbox.setChecked(is_temporary)
        layout.addWidget(self.temp_checkbox)

        self.content_edit = QTextEdit(content)
        self.content_edit.setPlaceholderText("Start typing...")
        self.content_edit.setFont(QFont("San Francisco", 13))
        layout.addWidget(self.content_edit, 1)

        footer_layout = QHBoxLayout()
        footer_layout.addStretch(1)
        self.save_btn = QPushButton("Done")
        self.save_btn.setFont(QFont("San Francisco", 13, QFont.Weight.Medium))
        self.save_btn.clicked.connect(self.save_note)
        footer_layout.addWidget(self.save_btn)
        layout.addLayout(footer_layout)


        self.setVisible(False)

        self.apply_styles()

    def handle_category_selection(self, index):
        if self.category_combo.itemText(index) == "+ New Category":

            self.show_new_category_dialog()

    def show_new_category_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Create New Category")
        dialog.setFixedWidth(300)

        dialog_layout = QVBoxLayout(dialog)


        label = QLabel("Category Name:")
        dialog_layout.addWidget(label)

        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter category name")
        dialog_layout.addWidget(name_input)



        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)

        create_btn = QPushButton("Create")
        create_btn.setDefault(True)

        def create_category():
            name = name_input.text().strip()
            if not name:
                QMessageBox.warning(dialog, "Invalid Name", "Please enter a category name")
                return


            self.category_combo.insertItem(self.category_combo.count() - 1, name)
            self.category_combo.setCurrentText(name)
            dialog.accept()

        create_btn.clicked.connect(create_category)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(create_btn)
        dialog_layout.addLayout(button_layout)


        def on_reject():

            index = self.category_combo.findText(self.current_category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

        dialog.rejected.connect(on_reject)

        dialog.exec()

    def apply_styles(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {current_theme_colors['BACKGROUND_POPUP']};
                border-radius: 12px;
                border: 1px solid {current_theme_colors['BORDER_MEDIUM']};
            }}
        """)
        self.title_edit.setStyleSheet(f"""
            QLineEdit {{
                font-size: 17px;
                font-weight: bold;
                border: none;
                padding: 5px 0px;
                background-color: transparent;
                color: {current_theme_colors['TEXT_PRIMARY']};
            }}
        """)
        self.close_btn.setStyleSheet(f"""
            QToolButton {{
                color: {current_theme_colors['TEXT_SECONDARY']};
                border: none;
                background-color: transparent;
                padding: 0px 5px;
            }}
            QToolButton:hover {{
                color: {current_user_accent_color};
            }}
        """)
        self.content_edit.setStyleSheet(f"""
            QTextEdit {{
                border: none;
                background-color: transparent;
                color: {current_theme_colors['TEXT_PRIMARY']};
                padding: 5px 0px;
            }}
        """)


        self.category_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {current_theme_colors['BORDER_MEDIUM']};
                border-radius: 4px;
                padding: 5px;
                background-color: {current_theme_colors['BACKGROUND_CARD']};
                color: {current_theme_colors['TEXT_PRIMARY']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {current_theme_colors['BORDER_MEDIUM']};
                background-color: {current_theme_colors['BACKGROUND_CARD']};
                color: {current_theme_colors['TEXT_PRIMARY']};
                selection-background-color: {current_user_accent_color};
                selection-color: {get_contrasting_text_color(current_user_accent_color)};
            }}
        """)


        self.temp_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {current_theme_colors['TEXT_PRIMARY']};
                background-color: transparent;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid {current_theme_colors['BORDER_MEDIUM']};
                border-radius: 3px;
                background-color: {current_theme_colors['BACKGROUND_CARD']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {current_user_accent_color};
                border: 1px solid {current_user_accent_color};
            }}
        """)

        save_btn_text_color = get_contrasting_text_color(current_user_accent_color)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 20px;
                background-color: {current_user_accent_color};
                color: {save_btn_text_color};
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {QColor(current_user_accent_color).darker(110).name()};
            }}
        """)
        if hasattr(self, 'graphicsEffect') and isinstance(self.graphicsEffect(), QGraphicsDropShadowEffect):
            self.graphicsEffect().setColor(QColor(current_theme_colors['SHADOW_COLOR']))

    def show(self):
        self.overlay.resize(self.parent.width(), self.parent.height())
        self.overlay.show()
        super().show()
        self.animation.start()
        self.title_edit.setFocus()

    def close(self):
        self.overlay.fadeOut()
        super().close()

    def save_note(self):
        title = self.title_edit.text()
        content = self.content_edit.toPlainText()
        is_temporary = self.temp_checkbox.isChecked()
        category = self.category_combo.currentText()


        if category == "+ New Category":
            QMessageBox.warning(self, "Invalid Category", "Please select a category or create a new one.")
            return

        if not title and not content:
            self.close()
            return

        self.on_save(self.note_id, title, content, is_temporary, category)
        self.close()

class NoteWidget(QWidget):
    def __init__(self, note_id, title, content_preview, favorite, is_temporary, created_at, updated_at,
                 category="Uncategorized", on_click=None, on_delete=None, on_favorite=None,
                 on_category_change=None, parent=None):
        super().__init__(parent)
        self.note_id = note_id
        self.title_text = title
        self.content_text = content_preview
        self.is_favorite = favorite
        self.is_temporary = is_temporary
        self.created_at_str = created_at
        self.updated_at_str = updated_at
        self.category = category
        self.on_click = on_click
        self.on_delete = on_delete
        self.on_favorite = on_favorite
        self.on_category_change = on_category_change
        self.drag_enabled = False

        self.setMinimumHeight(150)
        self.apply_styles()


        self.setAcceptDrops(False)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 10)
        main_layout.setSpacing(8)

        self.preview_area = QFrame()
        self.preview_area.setMinimumHeight(80)
        self.preview_area.setStyleSheet(f"""
            QFrame {{
                background-color: {current_theme_colors['BACKGROUND_CARD_PREVIEW']};
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom: 1px solid {current_theme_colors['BORDER_LIGHT']};
            }}
        """)
        preview_area_layout = QVBoxLayout(self.preview_area)
        preview_area_layout.setContentsMargins(12, 10, 12, 10)
        preview_text_full = self.content_text.replace("\n", " \n")
        max_chars_preview = 100
        elided_preview = preview_text_full[:max_chars_preview] + ("..." if len(preview_text_full) > max_chars_preview else "")
        preview_label = QLabel(elided_preview if elided_preview else "No content preview")
        preview_label.setFont(QFont("San Francisco", 11))
        preview_label.setStyleSheet(f"color: {current_theme_colors['TEXT_SECONDARY']}; background-color: transparent;")
        preview_label.setWordWrap(True)
        preview_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        preview_area_layout.addWidget(preview_label)
        main_layout.addWidget(self.preview_area, 1)

        title_container = QWidget()
        title_container_layout = QVBoxLayout(title_container)
        title_container_layout.setContentsMargins(12, 5, 12, 0)
        title_label = QLabel(self.title_text if self.title_text else "Untitled")
        title_label.setFont(QFont("San Francisco", 12, QFont.Weight.DemiBold))
        title_label.setStyleSheet(f"color: {current_theme_colors['TEXT_PRIMARY']}; background-color: transparent;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_container_layout.addWidget(title_label)
        main_layout.addWidget(title_container)


        if self.category and self.category != "Uncategorized":
            tag_container = QWidget()
            tag_layout = QHBoxLayout(tag_container)
            tag_layout.setContentsMargins(0, 0, 0, 0)
            tag_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)


            category_color = get_category_color(self.category)
            category_tag = QLabel(f" {self.category} ")
            category_tag.setStyleSheet(f"""
                QLabel {{
                    background-color: {category_color};
                    color: {get_contrasting_text_color(category_color)};
                    border-radius: 10px;
                    padding: 2px 8px;
                    font-size: 10px;
                }}
            """)
            tag_layout.addWidget(category_tag)

            main_layout.addWidget(tag_container)

        self.metadata_layout_widget = QWidget()
        metadata_layout = QHBoxLayout(self.metadata_layout_widget)
        metadata_layout.setContentsMargins(12, 0, 12, 0)
        metadata_layout.setSpacing(6)

        self.timestamp_label = QLabel()
        self.timestamp_label.setFont(QFont("San Francisco", 10))
        self.timestamp_label.setStyleSheet(f"color: {current_theme_colors['TEXT_TERTIARY']}; background-color: transparent;")
        metadata_layout.addWidget(self.timestamp_label)
        metadata_layout.addStretch()

        self.temp_icon_label = QLabel()
        self.temp_icon_label.setFont(QFont("San Francisco", 10))
        self.temp_icon_label.setStyleSheet(f"color: {current_user_accent_color}; background-color: transparent; margin-left: 5px;")
        metadata_layout.addWidget(self.temp_icon_label)


        self.delete_btn = QToolButton()
        self.delete_btn.setText("🗑️")
        self.delete_btn.setToolTip("Move to Recycle Bin")
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.clicked.connect(self._handle_delete)
        self.delete_btn.setStyleSheet(f"""
            QToolButton {{
                color: {current_theme_colors['TEXT_TERTIARY']};
                background-color: transparent;
                border: none;
                padding: 0px;
                font-size: 14px;
            }}
            QToolButton:hover {{
                color: #FF5555;
            }}
        """)
        metadata_layout.addWidget(self.delete_btn)

        self.fav_btn = QToolButton()
        self.fav_btn.setFont(QFont("Arial", 15))
        self.fav_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fav_btn.clicked.connect(self._handle_favorite)
        metadata_layout.addWidget(self.fav_btn)

        main_layout.addWidget(self.metadata_layout_widget)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.update_metadata_display()

    def setDragEnabled(self, enabled):
        """Enable or disable drag functionality"""
        self.drag_enabled = enabled
        self.setAcceptDrops(not enabled)

    def mouseMoveEvent(self, event):
        """Handle drag start when drag is enabled"""
        if not self.drag_enabled:
            super().mouseMoveEvent(event)
            return


        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return


        drag = QDrag(self)
        mime_data = QMimeData()


        mime_data.setText(f"note:{self.note_id}:{self.category}")
        drag.setMimeData(mime_data)


        pixmap = QPixmap(self.size())
        self.render(pixmap)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())


        drag_result = drag.exec(Qt.DropAction.MoveAction)

    def apply_styles(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {current_theme_colors['BACKGROUND_CARD']};
                border-radius: 8px;
                border: 1px solid {current_theme_colors['BORDER_LIGHT']};
            }}
            QWidget:hover {{
                border-color: {current_theme_colors['BORDER_MEDIUM']};
            }}
        """)
        if hasattr(self, 'graphicsEffect') and isinstance(self.graphicsEffect(), QGraphicsDropShadowEffect):
             self.graphicsEffect().setColor(QColor(current_theme_colors['SHADOW_COLOR']))


        if hasattr(self, 'preview_area'):
             self.preview_area.setStyleSheet(f"""
                QFrame {{
                    background-color: {current_theme_colors['BACKGROUND_CARD_PREVIEW']};
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    border-bottom: 1px solid {current_theme_colors['BORDER_LIGHT']};
                }}
            """)

             preview_label = self.preview_area.findChild(QLabel)
             if preview_label:
                 preview_label.setStyleSheet(f"color: {current_theme_colors['TEXT_SECONDARY']}; background-color: transparent;")


        self.update_metadata_display()

    def dragEnterEvent(self, event):
        """Handle when a draggable note enters this widget"""
        if not self.acceptDrops():
            event.ignore()
            return


        if event.mimeData().hasText() and event.mimeData().text().startswith("note:"):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle when a note is dropped on this widget"""
        if not self.acceptDrops():
            event.ignore()
            return


        if event.mimeData().hasText() and event.mimeData().text().startswith("note:"):
            data_parts = event.mimeData().text().split(":")
            if len(data_parts) >= 2:
                dropped_note_id = data_parts[1]


                if self.on_category_change and dropped_note_id != self.note_id:
                    self.on_category_change(dropped_note_id, self.category)
                    event.accept()
                    return

        event.ignore()

    def get_formatted_expiry_countdown(self):
        if not self.is_temporary or not self.created_at_str:
            return ""
        try:
            created_date = datetime.fromisoformat(self.created_at_str)
            expiry_date = created_date + timedelta(days=30)
            now = datetime.now()
            remaining_delta = expiry_date - now

            if remaining_delta.total_seconds() <= 0:
                return "Expired"

            days = remaining_delta.days
            hours, remainder = divmod(remaining_delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            if days > 0:
                return f"⏱{days}d {hours}h"
            elif hours > 0:
                return f"⏱{hours}h {minutes}m"
            elif minutes > 0:
                return f"⏱{minutes}m"
            else:
                return "⏱<1m"
        except ValueError:
            return "⏱Error"

    def update_metadata_display(self):

        try:
            updated_dt = datetime.fromisoformat(self.updated_at_str)
            now = datetime.now()
            if updated_dt.date() == now.date(): timestamp_str = updated_dt.strftime("%I:%M %p").lstrip('0')
            elif (now - updated_dt).days < 1: timestamp_str = "Yesterday"
            elif (now - updated_dt).days < 7: timestamp_str = updated_dt.strftime("%A")
            else: timestamp_str = updated_dt.strftime("%b %d")
        except: timestamp_str = ""
        if hasattr(self, 'timestamp_label'):
            self.timestamp_label.setText(timestamp_str)
            self.timestamp_label.setStyleSheet(f"color: {current_theme_colors['TEXT_TERTIARY']}; background-color: transparent;")


        if hasattr(self, 'fav_btn'):
            highlight_color = current_theme_colors.get('HIGHLIGHT_SIDEBAR') or current_user_accent_color
            self.fav_btn.setText("★" if self.is_favorite else "☆")
            self.fav_btn.setStyleSheet(f"""
                QToolButton {{ color: {highlight_color if self.is_favorite else current_theme_colors['TEXT_TERTIARY']};
                               border: none; background: transparent; padding:0px; }}
                QToolButton:hover {{ color: {highlight_color}; }}
            """)


        if hasattr(self, 'temp_icon_label'):
            if self.is_temporary:
                countdown_text = self.get_formatted_expiry_countdown()
                self.temp_icon_label.setText(countdown_text)
                self.temp_icon_label.setToolTip(f"Temporary note: {countdown_text.replace('⏱', '')}")
                self.temp_icon_label.setStyleSheet(f"color: {current_user_accent_color}; background-color: transparent; margin-left: 5px;")
                self.temp_icon_label.setVisible(True)
            else:
                self.temp_icon_label.setVisible(False)

    def mousePressEvent(self, event):

        target_widget = self.childAt(event.pos())
        if target_widget == self.fav_btn or target_widget == self.delete_btn:

            super().mousePressEvent(event)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.on_click(self.note_id)
        super().mousePressEvent(event)

    def _handle_favorite(self):
        self.is_favorite = not self.is_favorite
        self.update_metadata_display()
        self.on_favorite(self.note_id)

    def _handle_delete(self):
        self.on_delete(self.note_id)

class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(230)



        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)


        self.title_container = QWidget()
        self.title_container.setFixedHeight(55)


        title_layout = QVBoxLayout(self.title_container)
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.setSpacing(0)

        self.title_label = QLabel("AmogOS Notes")
        self.title_label.setFont(QFont("San Francisco", 16, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)


        title_layout.addWidget(self.title_label)
        layout.addWidget(self.title_container)


        self.content_container = QWidget()
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(5)

        self.create_note_btn = QPushButton("Create Note")
        self.create_note_btn.setFixedHeight(40)
        self.create_note_btn.setFont(QFont("San Francisco", 15, QFont.Weight.Bold))
        content_layout.addWidget(self.create_note_btn)
        content_layout.addSpacing(15)

        section_font = QFont("San Francisco", 11, QFont.Weight.Bold)
        section_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.5)

        self.main_notes_label = QLabel("NOTES")
        self.main_notes_label.setFont(section_font)
        content_layout.addWidget(self.main_notes_label)

        self.nav_buttons_widgets = {}
        nav_items_data = [
            {"text": "All Notes", "id": "home", "icon": None},
            {"text": "Favorites", "id": "favorites", "icon": None},
            {"text": "Temporary", "id": "temporary_notes", "icon": None}
        ]
        for item_data in nav_items_data:
            btn = ModernButton(item_data["text"], icon_path=item_data["icon"], is_sidebar_item=True)
            content_layout.addWidget(btn)
            self.nav_buttons_widgets[item_data["id"]] = btn


        content_layout.addSpacing(15)
        self.categories_label = QLabel("CATEGORIES")
        self.categories_label.setFont(section_font)
        content_layout.addWidget(self.categories_label)


        self.categories_container = QWidget()
        self.categories_layout = QVBoxLayout(self.categories_container)
        self.categories_layout.setContentsMargins(0, 0, 0, 0)
        self.categories_layout.setSpacing(2)
        content_layout.addWidget(self.categories_container)


        self.add_category_btn = QPushButton("+ Add Category")
        self.add_category_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_category_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #8A8A8E;
                text-align: left;
                padding: 5px 15px;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #000000;
            }
        """)
        content_layout.addWidget(self.add_category_btn)

        content_layout.addSpacing(15)
        self.other_label = QLabel("OTHER")
        self.other_label.setFont(section_font)
        content_layout.addWidget(self.other_label)

        other_navs = [
             {"text": "Synced Notes", "id": "synced_notes", "icon": None},
             {"text": "Recycle Bin", "id": "recycle_bin", "icon": None},
             {"text": "Settings", "id": "settings", "icon": None}
        ]
        for item_data in other_navs:
            btn = ModernButton(item_data["text"], icon_path=item_data["icon"], is_sidebar_item=True)
            if item_data["id"] not in ["settings", "recycle_bin"]:
                 btn.setEnabled(False)
            content_layout.addWidget(btn)
            self.nav_buttons_widgets[item_data["id"]] = btn

        content_layout.addStretch()
        layout.addWidget(self.content_container)


        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {current_theme_colors['BACKGROUND_SIDEBAR']};
                color: {current_theme_colors['TEXT_PRIMARY']};
            }}
        """)
        self.title_container.setStyleSheet(f"background-color: {current_theme_colors['BACKGROUND_SIDEBAR']}; padding: 0;")
        self.title_label.setStyleSheet(f"color: {current_theme_colors['TEXT_PRIMARY']}; padding-top: 10px;")
        self.main_notes_label.setStyleSheet(f"color: {current_theme_colors['TEXT_SECONDARY']}; padding: 10px 12px 5px 12px; text-transform: uppercase;")
        self.other_label.setStyleSheet(f"color: {current_theme_colors['TEXT_SECONDARY']}; padding: 10px 12px 5px 12px; text-transform: uppercase;")

        self.categories_label.setStyleSheet(f"color: {current_theme_colors['TEXT_SECONDARY']}; padding: 10px 12px 5px 12px; text-transform: uppercase;")

        self.add_category_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {current_theme_colors['TEXT_SECONDARY']};
                text-align: left;
                padding: 5px 15px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                color: {current_theme_colors['TEXT_PRIMARY']};
            }}
        """)
        self.update_create_note_button_style()
        self.update_nav_button_styles()

    def update_nav_button_styles(self):
        for key, btn in self.nav_buttons_widgets.items():
            is_checked = btn.isChecked()
            is_settings = (key == "settings")
            btn.setStyleSheet(self.get_modern_button_style(is_sidebar_item=True, is_checked=is_checked, is_settings_button=is_settings))

    def update_category_buttons(self, categories, active_category=None):
        """Update the category buttons based on the list of categories"""

        for i in reversed(range(self.categories_layout.count())):
            widget = self.categories_layout.itemAt(i).widget()
            if widget:
                self.categories_layout.removeWidget(widget)
                widget.deleteLater()


        if not categories:
            empty_label = QLabel("No categories yet")
            empty_label.setStyleSheet(f"color: {current_theme_colors['TEXT_TERTIARY']}; padding: 5px 15px; font-style: italic;")
            self.categories_layout.addWidget(empty_label)
            return


        self.category_buttons = {}
        for category in categories:
            btn = ModernButton(category, is_sidebar_item=True)
            btn.setObjectName(f"category_{category}")
            btn.setCheckable(True)
            btn.setChecked(category == active_category)
            self.categories_layout.addWidget(btn)
            self.category_buttons[category] = btn


            btn.setStyleSheet(self.get_modern_button_style(is_sidebar_item=True, is_checked=(category == active_category)))


        for btn in self.category_buttons.values():
            btn.setAcceptDrops(True)

    def update_create_note_button_style(self):
        global current_user_accent_color
        primary_color = current_user_accent_color
        secondary_color_q = QColor(primary_color).darker(120)
        secondary_color = secondary_color_q.name()

        primary_hover = QColor(primary_color).lighter(110).name()
        secondary_hover = secondary_color_q.lighter(110).name()


        text_color = get_contrasting_text_color(primary_color)

        self.create_note_btn.setStyleSheet(f"""
            QPushButton {{
                color: {text_color};
                border: none;
                border-radius: 8px;
                padding: 10px;
                text-align: center;
                font-weight: bold;
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 {primary_color}, stop:1 {secondary_color});
            }}
            QPushButton:hover {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 {primary_hover}, stop:1 {secondary_hover});
            }}
        """)

    def get_modern_button_style(self, is_sidebar_item=False, is_checked=False, is_settings_button=False):

        global current_user_accent_color, current_theme_colors, current_theme_name


        if is_settings_button:

            checked_bg_color = current_theme_colors['TEXT_TERTIARY']
        else:

            checked_bg_color = current_user_accent_color


        checked_text_color = get_contrasting_text_color(checked_bg_color)


        hover_bg_color = QColor(current_theme_colors['BACKGROUND_SIDEBAR']).darker(110).name() if current_theme_name != 'light' else '#EAEAEB'

        pressed_bg_color = QColor(current_theme_colors['BACKGROUND_SIDEBAR']).darker(110).name() if current_theme_name != 'light' else '#E0E0E0'


        style = f"""
            QPushButton {{
                border: none;
                border-radius: 6px;
                padding: {'10px 12px' if is_sidebar_item else '12px'};
                font-size: 14px;
                text-align: left;
                color: {current_theme_colors['TEXT_PRIMARY']};
                background-color: transparent;
            }}
            QPushButton:hover {{
                background-color: {hover_bg_color};
            }}
        """


        if is_checked:
            style += f"""
            QPushButton:checked, QPushButton:pressed {{
                background-color: {checked_bg_color};
                color: {checked_text_color};
                font-weight: bold;
            }}
            """

        else:

             style += f"""
             QPushButton:pressed {{
                 background-color: {pressed_bg_color};
             }}
             """

        return style

class SettingsView(QWidget):
    def __init__(self, parent_window, parent=None):
        super().__init__(parent)
        self.parent_window = parent_window


        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)


        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


        self.scrollable_content = QWidget()


        bg_color = current_theme_colors['BACKGROUND_MAIN']
        self.setStyleSheet(f"""

            SettingsView, QWidget, QLabel, QScrollArea, QFrame, QPushButton {{
                background-color: {bg_color};
            }}

            QScrollBar:vertical {{
                background: {current_theme_colors['BACKGROUND_MAIN']};
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {current_theme_colors['SCROLLBAR_HANDLE']};
                min-height: 25px;
                border-radius: 5px;
            }}

            QScrollBar:horizontal {{
                background: {current_theme_colors['BACKGROUND_MAIN']};
                height: 10px;
                margin: 0px;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal {{
                background: {current_theme_colors['SCROLLBAR_HANDLE']};
                min-width: 25px;
                border-radius: 5px;
            }}
        """)

        layout = QVBoxLayout(self.scrollable_content)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)

        self.title = QLabel("Appearance Settings")
        self.title.setFont(QFont("San Francisco", 18, QFont.Weight.Bold))
        self.title.setAutoFillBackground(True)
        title_palette = self.title.palette()
        title_palette.setColor(QPalette.ColorRole.Window, QColor(current_theme_colors['BACKGROUND_MAIN']))
        title_palette.setColor(QPalette.ColorRole.WindowText, QColor(current_theme_colors['TEXT_PRIMARY']))
        self.title.setPalette(title_palette)
        self.title.setStyleSheet(f"""
            background-color: {current_theme_colors['BACKGROUND_MAIN']};
            color: {current_theme_colors['TEXT_PRIMARY']};
            padding-bottom: 10px;
            font-weight: bold;
        """)
        layout.addWidget(self.title)


        self.theme_label = QLabel("Choose Theme:")
        self.theme_label.setFont(QFont("San Francisco", 14))
        self.theme_label.setAutoFillBackground(True)
        theme_label_palette = self.theme_label.palette()
        theme_label_palette.setColor(QPalette.ColorRole.Window, QColor(current_theme_colors['BACKGROUND_MAIN']))
        theme_label_palette.setColor(QPalette.ColorRole.WindowText, QColor(current_theme_colors['TEXT_PRIMARY']))
        self.theme_label.setPalette(theme_label_palette)
        self.theme_label.setStyleSheet(f"""
            background-color: {current_theme_colors['BACKGROUND_MAIN']};
            color: {current_theme_colors['TEXT_PRIMARY']};
            padding-top: 20px;
        """)
        layout.addWidget(self.theme_label)

        self.theme_buttons_layout = QHBoxLayout()
        self.theme_buttons_layout.setSpacing(10)

        theme_options = {
            "light": "Light Mode",
            "dark": "Dark Mode",
            "amoled": "AMOLED Dark"
        }

        self.theme_buttons = {}
        for theme_id, theme_name in theme_options.items():
            btn = QPushButton(theme_name)
            btn.setFixedHeight(40)
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {current_theme_colors['BORDER_LIGHT']};
                    color: {current_theme_colors['TEXT_PRIMARY']};
                    border-radius: 6px;
                    padding: 0 15px;
                    border: 1px solid {current_theme_colors['BORDER_MEDIUM']};
                }}
            """)
            btn.clicked.connect(lambda checked, t=theme_id: self.set_theme(t))
            self.theme_buttons_layout.addWidget(btn)
            self.theme_buttons[theme_id] = btn

        self.theme_buttons_layout.addStretch()
        layout.addLayout(self.theme_buttons_layout)


        self.accent_label = QLabel("Choose Accent Color:")
        self.accent_label.setFont(QFont("San Francisco", 14))
        self.accent_label.setAutoFillBackground(True)
        accent_label_palette = self.accent_label.palette()
        accent_label_palette.setColor(QPalette.ColorRole.Window, QColor(current_theme_colors['BACKGROUND_MAIN']))
        accent_label_palette.setColor(QPalette.ColorRole.WindowText, QColor(current_theme_colors['TEXT_PRIMARY']))
        self.accent_label.setPalette(accent_label_palette)
        self.accent_label.setStyleSheet(f"""
            background-color: {current_theme_colors['BACKGROUND_MAIN']};
            color: {current_theme_colors['TEXT_PRIMARY']};
            padding-top: 20px;
        """)
        layout.addWidget(self.accent_label)

        self.color_buttons_layout = QHBoxLayout()
        self.color_buttons_layout.setSpacing(10)
        self.accent_color_options = [
            ("AmogOS Pink", "#FF69B4"),
            ("Sunset Orange", "#FF8C00"),
            ("Forest Green", "#228B22"),
            ("Ocean Blue", "#1E90FF"),
            ("Royal Purple", "#8A2BE2"),
            ("Graphite Gray", "#696969"),
        ]
        self.accent_buttons = {}
        for name, color_hex in self.accent_color_options:
            btn = QPushButton()
            btn.setFixedSize(40, 40)
            btn.setToolTip(name)

            is_selected = (color_hex == current_user_accent_color)
            border_style = f"3px solid {current_theme_colors['TEXT_PRIMARY']}" if is_selected else f"2px solid {current_theme_colors['BORDER_MEDIUM']}"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_hex};
                    border-radius: 20px;
                    border: {border_style};
                }}
            """)
            btn.clicked.connect(lambda checked, c=color_hex: self.set_accent_color(c))
            self.color_buttons_layout.addWidget(btn)
            self.accent_buttons[color_hex] = btn
        self.color_buttons_layout.addStretch()
        layout.addLayout(self.color_buttons_layout)


        self.behavior_settings_header = QLabel("Behavior Settings:")
        self.behavior_settings_header.setFont(QFont("San Francisco", 14, QFont.Weight.Bold))

        layout.addWidget(self.behavior_settings_header)


        self.jokes_container = QWidget()
        self.jokes_container.setStyleSheet(f"background-color: {current_theme_colors['BACKGROUND_MAIN']};")
        jokes_layout = QVBoxLayout(self.jokes_container)
        jokes_layout.setContentsMargins(0, 5, 0, 5)
        jokes_layout.setSpacing(5)


        self.amogus_toggle = QCheckBox("Enable Among Us Jokes")
        self.amogus_toggle.setChecked(enable_amogus_jokes)
        self.amogus_toggle.setFont(QFont("San Francisco", 13))

        self.amogus_toggle.stateChanged.connect(self.toggle_amogus_jokes)
        jokes_layout.addWidget(self.amogus_toggle)

        self.jokes_description = QLabel("Randomly creates Among Us themed notes at unexpected times")
        self.jokes_description.setFont(QFont("San Francisco", 11))
        self.jokes_description.setStyleSheet(f"color: {current_theme_colors['TEXT_SECONDARY']}; background-color: transparent; margin-left: 20px;")
        jokes_layout.addWidget(self.jokes_description)

        layout.addWidget(self.jokes_container)


        self.buddy_section_header = QLabel("Amogus Buddy:")
        self.buddy_section_header.setFont(QFont("San Francisco", 16, QFont.Weight.Bold))

        layout.addWidget(self.buddy_section_header)


        self.buddy_content_container = QWidget()
        self.buddy_content_container.setStyleSheet(f"background-color: {current_theme_colors['BACKGROUND_MAIN']};")
        buddy_content_layout = QVBoxLayout(self.buddy_content_container)
        buddy_content_layout.setContentsMargins(0, 0, 0, 0)
        buddy_content_layout.setSpacing(10)


        self.buddy_description = QLabel("Choose your buddy that will hang out in the corner of the app")
        self.buddy_description.setFont(QFont("San Francisco", 12))


        if current_theme_name in ["dark", "amoled"]:
            description_color = "#FFFFFF"
        else:
            description_color = current_theme_colors['TEXT_SECONDARY']

        self.buddy_description.setStyleSheet(f"""
            QLabel {{
                color: {description_color};
                background-color: transparent;
                font-weight: normal;
            }}
        """)
        buddy_content_layout.addWidget(self.buddy_description)


        self.buddy_buttons_layout = QHBoxLayout()
        self.buddy_buttons_layout.setSpacing(10)
        self.buddy_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.buddy_buttons = []


        self.buddy_scroll_area = QScrollArea()
        self.buddy_scroll_area.setWidgetResizable(True)
        self.buddy_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.buddy_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.buddy_scroll_area.setMaximumHeight(140)


        self.buddy_buttons_container = QWidget()
        self.buddy_buttons_container.setLayout(self.buddy_buttons_layout)
        self.buddy_buttons_container.setStyleSheet(f"background-color: {current_theme_colors['BACKGROUND_MAIN']};")

        self.buddy_scroll_area.setWidget(self.buddy_buttons_container)
        buddy_content_layout.addWidget(self.buddy_scroll_area)

        layout.addWidget(self.buddy_content_container)


        self.populate_buddy_buttons()

        layout.addStretch()


        self.scroll_area.setWidget(self.scrollable_content)
        self.scrollable_content.setObjectName("scrollContent")


        main_layout.addWidget(self.scroll_area)


        self.setStyleSheet(f"""
            * {{ background-color: {current_theme_colors['BACKGROUND_MAIN']}; }}
            QWidget {{ background-color: {current_theme_colors['BACKGROUND_MAIN']}; }}
            QLabel {{ background-color: {current_theme_colors['BACKGROUND_MAIN']}; }}
            QScrollArea {{
                background-color: {current_theme_colors['BACKGROUND_MAIN']};
                border: none;
            }}
            QScrollBar:vertical {{
                background: {current_theme_colors['BACKGROUND_MAIN']};
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {current_theme_colors['SCROLLBAR_HANDLE']};
                min-height: 25px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {current_theme_colors['SCROLLBAR_HANDLE_HOVER']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)


        self.setAutoFillBackground(True)
        main_palette = self.palette()
        main_palette.setColor(QPalette.ColorRole.Window, QColor(current_theme_colors['BACKGROUND_MAIN']))
        self.setPalette(main_palette)


        self.scrollable_content.setAutoFillBackground(True)
        content_palette = self.scrollable_content.palette()
        content_palette.setColor(QPalette.ColorRole.Window, QColor(current_theme_colors['BACKGROUND_MAIN']))
        self.scrollable_content.setPalette(content_palette)


        self.apply_styles()

    def apply_styles(self):

        base_bg_color = current_theme_colors['BACKGROUND_MAIN']
        self.setStyleSheet(f"""
            SettingsView, QWidget {{
                background-color: {base_bg_color};
                border: none;
            }}
            QLabel {{
                background-color: transparent;
                color: {current_theme_colors['TEXT_PRIMARY']};
            }}
            QScrollArea {{
                background-color: {base_bg_color};
                border: none;
            }}

            QScrollBar:vertical {{
                background: {base_bg_color};
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {current_theme_colors['SCROLLBAR_HANDLE']};
                min-height: 25px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {current_theme_colors['SCROLLBAR_HANDLE_HOVER']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}

            QScrollBar:horizontal {{
                background: {base_bg_color};
                height: 10px;
                margin: 0px;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal {{
                background: {current_theme_colors['SCROLLBAR_HANDLE']};
                min-width: 25px;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {current_theme_colors['SCROLLBAR_HANDLE_HOVER']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """)



        if hasattr(self, 'title'):
            self.title.setStyleSheet(f"color: {current_theme_colors['TEXT_PRIMARY']}; padding-bottom: 10px; font-weight: bold; background-color: transparent;")












        if hasattr(self, 'theme_label'):
            self.theme_label.setStyleSheet(f"color: {current_theme_colors['TEXT_PRIMARY']}; padding-top: 20px; background-color: transparent; font-weight: normal;")


        if hasattr(self, 'accent_label'):
            self.accent_label.setStyleSheet(f"color: {current_theme_colors['TEXT_PRIMARY']}; padding-top: 20px; background-color: transparent; font-weight: normal;")


        if hasattr(self, 'behavior_settings_header'):
            self.behavior_settings_header.setStyleSheet(f"color: {current_theme_colors['TEXT_PRIMARY']}; background-color: transparent; padding-top: 20px; font-weight: bold;")


        if hasattr(self, 'buddy_section_header'):

           header_color = "#FFFFFF" if current_theme_name in ["dark", "amoled"] else current_theme_colors['TEXT_PRIMARY']
           self.buddy_section_header.setStyleSheet(f"color: {header_color}; background-color: transparent; padding-top: 20px; font-weight: bold;")


        if hasattr(self, 'jokes_description'):
            self.jokes_description.setStyleSheet(f"color: {current_theme_colors['TEXT_SECONDARY']}; background-color: transparent; margin-left: 20px;")

        if hasattr(self, 'buddy_description'):

            if current_theme_name in ["dark", "amoled"]:
                description_color = "#FFFFFF"
            else:
                description_color = current_theme_colors['TEXT_SECONDARY']

            self.buddy_description.setStyleSheet(f"""
                QLabel {{
                    color: {description_color};
                    background-color: transparent;
                    font-weight: normal;
                }}
            """)


        header_color = "#FFFFFF" if current_theme_name in ["dark", "amoled"] else current_theme_colors['TEXT_PRIMARY']


        if hasattr(self, 'buddy_section_header'):
            self.buddy_section_header.setStyleSheet(f"color: {header_color}; background-color: transparent; padding-top: 20px; font-weight: bold;")

        if hasattr(self, 'behavior_settings_header'):
            self.behavior_settings_header.setStyleSheet(f"color: {header_color}; background-color: transparent; padding-top: 20px; font-weight: bold;")

        if hasattr(self, 'theme_label'):
            self.theme_label.setStyleSheet(f"color: {header_color}; padding-top: 20px; background-color: transparent; font-weight: normal;")

        if hasattr(self, 'accent_label'):
            self.accent_label.setStyleSheet(f"color: {header_color}; padding-top: 20px; background-color: transparent; font-weight: normal;")

        if hasattr(self, 'title'):
            self.title.setStyleSheet(f"color: {header_color}; padding-bottom: 10px; font-weight: bold; background-color: transparent;")


        if hasattr(self, 'theme_buttons'):
            for theme_id, btn in self.theme_buttons.items():
                btn.setChecked(theme_id == current_theme_name)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {current_theme_colors['BORDER_LIGHT']};
                        color: {current_theme_colors['TEXT_PRIMARY']};
                        border: 1px solid {current_theme_colors['BORDER_MEDIUM']};
                        border-radius: 6px;
                        font-size: 13px;
                        padding: 0 15px;
                        min-height: 35px;
                    }}
                    QPushButton:hover {{
                        background-color: {current_theme_colors['BORDER_MEDIUM']};
                    }}
                    QPushButton:checked {{
                        background-color: {current_user_accent_color};
                        color: {get_contrasting_text_color(current_user_accent_color)};
                        border: 1px solid {current_user_accent_color};
                        font-weight: bold;
                    }}
                """)


        if hasattr(self, 'accent_buttons'):
            for color_hex, btn in self.accent_buttons.items():
                is_selected = (color_hex == current_user_accent_color)
                border_style = f"3px solid {current_theme_colors['TEXT_PRIMARY']}" if is_selected else f"2px solid {current_theme_colors['BORDER_MEDIUM']}"
                hover_border_color = QColor(color_hex).darker(120).name()
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color_hex};
                        border: {border_style};
                        border-radius: 20px;
                    }}
                    QPushButton:hover {{
                        border-color: {hover_border_color if not is_selected else current_theme_colors['TEXT_PRIMARY']};
                    }}
                """)


        if hasattr(self, 'amogus_toggle'):
            self.amogus_toggle.setStyleSheet(f"""
                QCheckBox {{
                    color: {current_theme_colors['TEXT_PRIMARY']};
                    background-color: transparent;
                    spacing: 5px;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 1px solid {current_theme_colors['BORDER_MEDIUM']};
                    border-radius: 3px;
                    background-color: {current_theme_colors['BACKGROUND_CARD']};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {current_user_accent_color};
                    border: 1px solid {current_user_accent_color};

                }}
            """)



        if hasattr(self, 'jokes_container'):
             self.jokes_container.setStyleSheet(f"background-color: {current_theme_colors['BACKGROUND_MAIN']}; border: none;")
        if hasattr(self, 'buddy_content_container'):
             self.buddy_content_container.setStyleSheet(f"background-color: {current_theme_colors['BACKGROUND_MAIN']}; border: none;")
        if hasattr(self, 'buddy_buttons_container'):
            self.buddy_buttons_container.setStyleSheet(f"background-color: {current_theme_colors['BACKGROUND_MAIN']}; border: none;")


        if hasattr(self, 'buddy_buttons'):
            for button in self.buddy_buttons:
                button.setSelected(button.buddy_file == current_buddy)

    def populate_buddy_buttons(self):
        """Create buddy selection buttons with image previews"""

        for button in self.buddy_buttons:
            self.buddy_buttons_layout.removeWidget(button)
            button.deleteLater()
        self.buddy_buttons.clear()


        none_button = BuddySelectionButton("", "None")
        none_button.clicked.connect(lambda: self.select_buddy(""))
        self.buddy_buttons_layout.addWidget(none_button)
        self.buddy_buttons.append(none_button)


        if os.path.exists(BUDDIES_FOLDER) and os.path.isdir(BUDDIES_FOLDER):
            for file in sorted(os.listdir(str(BUDDIES_FOLDER))):
                if file.endswith(('.png', '.jpg', '.jpeg', '.svg', '.gif', '.webp')):
                    name = os.path.splitext(file)[0].replace('_', ' ').title()
                    button = BuddySelectionButton(file, name)
                    button.clicked.connect(lambda checked, f=file: self.select_buddy(f))
                    self.buddy_buttons_layout.addWidget(button)
                    self.buddy_buttons.append(button)


        self.update_buddy_selection()

    def update_buddy_selection(self):
        """Update the selected buddy button based on the current setting"""
        for button in self.buddy_buttons:
            button.setSelected(button.buddy_file == current_buddy)

    def select_buddy(self, buddy_file):
        """Handle buddy selection"""
        self.parent_window.save_settings({"buddy": buddy_file})
        self.parent_window.load_settings_and_apply_theme()
        self.update_buddy_selection()

    def set_theme(self, theme_name):
        print(f"Theme selected: {theme_name}")
        if theme_name in THEMES:
            self.parent_window.save_settings({"theme": theme_name})
            self.parent_window.load_settings_and_apply_theme()

    def set_accent_color(self, color_hex):
        print(f"Accent color selected: {color_hex}")
        self.parent_window.save_settings({"accent_color": color_hex})
        self.parent_window.load_settings_and_apply_theme()

    def toggle_amogus_jokes(self, state):
        global enable_amogus_jokes
        enable_amogus_jokes = (state == Qt.CheckState.Checked.value)
        self.parent_window.save_settings({"amogus_jokes": enable_amogus_jokes})

class MainWindow(QMainWindow):
    def __init__(self):
        global current_user_accent_color
        super().__init__()


        self.setWindowIcon(QIcon("images/Amogus.webp"))


        self.live_countdown_timer = QTimer(self)
        self.amogus_timer = QTimer(self)

        self.setWindowTitle("AmogOS Notes")
        self.setMinimumSize(900, 550)

        self.notes = {}
        self.categories = []
        self.current_filter = "home"
        self.current_category = None
        self.load_notes()
        self.check_expired_notes()

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_widget.setStyleSheet(f"background-color: {current_theme_colors['BACKGROUND_MAIN']};")

        main_hbox_layout = QHBoxLayout(self.main_widget)
        main_hbox_layout.setContentsMargins(0, 0, 0, 0)
        main_hbox_layout.setSpacing(0)


        self.sidebar = Sidebar(self)
        main_hbox_layout.addWidget(self.sidebar)


        self.stacked_content_widget = QStackedWidget()
        self.stacked_content_widget.setStyleSheet(f"border-left: 1px solid {current_theme_colors['BORDER_MEDIUM']};")
        main_hbox_layout.addWidget(self.stacked_content_widget, 1)



        self.notes_page_widget = QWidget()
        notes_page_layout = QVBoxLayout(self.notes_page_widget)
        notes_page_layout.setContentsMargins(20, 15, 20, 15)
        notes_page_layout.setSpacing(10)
        self.section_title = QLabel("All Notes")
        self.section_title.setFont(QFont("San Francisco", 22, QFont.Weight.Bold))
        self.section_title.setStyleSheet(f"color: {current_theme_colors['TEXT_PRIMARY']}; padding-bottom: 0px;")
        notes_page_layout.addWidget(self.section_title)


        self.category_tag_container = QWidget()
        self.category_tag_layout = QHBoxLayout(self.category_tag_container)
        self.category_tag_layout.setContentsMargins(0, 0, 0, 10)
        self.category_tag_layout.setSpacing(5)
        self.category_tag_container.setVisible(False)
        notes_page_layout.addWidget(self.category_tag_container)

        self.temp_notes_explanation_label = QLabel(
            "Notes in this section are temporary and will be automatically deleted after 30 days."
        )
        self.temp_notes_explanation_label.setFont(QFont("San Francisco", 11))
        self.temp_notes_explanation_label.setStyleSheet(f"color: {current_theme_colors['TEXT_SECONDARY']}; padding-bottom: 10px;")
        self.temp_notes_explanation_label.setWordWrap(True)
        self.temp_notes_explanation_label.setVisible(False)
        notes_page_layout.addWidget(self.temp_notes_explanation_label)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{ background-color: transparent; border: none; }}
            QScrollBar:vertical {{ background: {current_theme_colors['BACKGROUND_MAIN']}; width: 10px; margin: 0px; border-radius: 5px; }}
            QScrollBar::handle:vertical {{ background: {current_theme_colors['SCROLLBAR_HANDLE']}; min-height: 25px; border-radius: 5px; }}
            QScrollBar::handle:vertical:hover {{ background: {current_theme_colors['SCROLLBAR_HANDLE_HOVER']}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
        """)
        self.notes_widget_container = QWidget()
        self.notes_widget_container.setStyleSheet("background-color: transparent;")
        self.notes_layout = QGridLayout(self.notes_widget_container)
        self.notes_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.notes_layout.setContentsMargins(0,0,0,0)
        self.notes_layout.setSpacing(15)
        self.scroll_area.setWidget(self.notes_widget_container)
        notes_page_layout.addWidget(self.scroll_area, 1)


        self.settings_view = SettingsView(self)


        self.stacked_content_widget.addWidget(self.notes_page_widget)
        self.stacked_content_widget.addWidget(self.settings_view)



        if hasattr(self.sidebar, 'create_note_btn'):
            self.sidebar.create_note_btn.clicked.connect(self.create_new_note_popup)
        if hasattr(self.sidebar, 'nav_buttons_widgets'):
            nav_map = {
                "home": self.show_all_notes,
                "favorites": self.show_favorite_notes,
                "temporary_notes": self.show_temporary_notes,
                "recycle_bin": self.show_recycle_bin,
                "settings": self.show_settings_view
            }
            for key, func in nav_map.items():
                if key in self.sidebar.nav_buttons_widgets:
                    self.sidebar.nav_buttons_widgets[key].clicked.connect(func)
            if "settings" in self.sidebar.nav_buttons_widgets:
                 self.sidebar.nav_buttons_widgets["settings"].setEnabled(True)


        if hasattr(self.sidebar, 'add_category_btn'):
            self.sidebar.add_category_btn.clicked.connect(self.add_new_category)


        self.active_popup = None


        self.buddy_companion = AmogusCompanion(self.main_widget)


        self.load_settings_and_apply_theme()


        self.update_active_nav_button()
        self.load_categories()
        self.display_filtered_notes()


        self.live_countdown_timer.timeout.connect(self.update_visible_note_countdowns)
        self.live_countdown_timer.start(30000)


        self.amogus_timer.timeout.connect(self.maybe_create_amogus_joke)
        self.set_random_amogus_interval()

        if enable_amogus_jokes:
            self.amogus_timer.start()
            remaining_ms = self.amogus_timer.remainingTime()
            if remaining_ms > 0:
                remaining_seconds = remaining_ms // 1000
                minutes = remaining_seconds // 60
                seconds = remaining_seconds % 60
                if minutes > 0:
                    print(f"Amogus Joke Timer: Next potential joke in approximately {minutes} minute(s) and {seconds} second(s).")
                else:
                    print(f"Amogus Joke Timer: Next potential joke in approximately {seconds} second(s).")
            else:

                print("Amogus Joke Timer: Active, but next joke time is immediate or couldn't be determined.")
        else:
            print("Amogus Joke Timer: Disabled. No random jokes will be created.")

    def load_categories(self):
        """Load categories from notes data"""
        categories = set()
        for note_id, note_data in self.notes.items():
            if not note_data.get("deleted", False):
                category = note_data.get("category")
                if category and category != "Uncategorized":
                    categories.add(category)

        self.categories = sorted(list(categories))


        if hasattr(self.sidebar, 'update_category_buttons'):
            self.sidebar.update_category_buttons(self.categories, self.current_category)


            if hasattr(self.sidebar, 'category_buttons'):
                for category, btn in self.sidebar.category_buttons.items():
                    btn.clicked.connect(lambda checked, cat=category: self.show_category(cat))

    def show_category(self, category):
        """Filter notes by selected category"""
        self.show_notes_view()
        self.current_filter = "category"
        self.current_category = category
        self.section_title.setText(f"Category: {category}")
        self.temp_notes_explanation_label.setVisible(False)


        self.update_category_tag(category)

        self.display_filtered_notes()


        self.update_active_nav_button()
        if hasattr(self.sidebar, 'update_category_buttons'):
            self.sidebar.update_category_buttons(self.categories, self.current_category)


            if hasattr(self.sidebar, 'category_buttons'):
                for cat, btn in self.sidebar.category_buttons.items():
                    btn.clicked.connect(lambda checked, c=cat: self.show_category(c))

    def update_category_tag(self, category=None):
        """Update the category tag display"""

        for i in reversed(range(self.category_tag_layout.count())):
            widget = self.category_tag_layout.itemAt(i).widget()
            if widget:
                self.category_tag_layout.removeWidget(widget)
                widget.deleteLater()

        if category and self.current_filter == "category":

            tag_color = get_category_color(category)
            tag = QLabel(f" {category} ")
            tag.setStyleSheet(f"""
                QLabel {{
                    background-color: {tag_color};
                    color: {get_contrasting_text_color(tag_color)};
                    border-radius: 12px;
                    padding: 4px 10px;
                    font-weight: bold;
                }}
            """)
            self.category_tag_layout.addWidget(tag)


            edit_btn = QPushButton("Edit")
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {current_theme_colors['TEXT_SECONDARY']};
                    border: none;
                    padding: 4px 10px;
                }}
                QPushButton:hover {{
                    color: {current_theme_colors['TEXT_PRIMARY']};
                }}
            """)
            edit_btn.clicked.connect(lambda: self.edit_category(category))
            self.category_tag_layout.addWidget(edit_btn)


            self.category_tag_layout.addStretch()

            self.category_tag_container.setVisible(True)
        else:
            self.category_tag_container.setVisible(False)

    def edit_category(self, category):
        """Show dialog to edit or delete a category"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Category: {category}")
        dialog.setFixedWidth(300)

        dialog_layout = QVBoxLayout(dialog)


        label = QLabel("Category Name:")
        dialog_layout.addWidget(label)

        name_input = QLineEdit(category)
        dialog_layout.addWidget(name_input)


        color_label = QLabel("Category Color:")
        dialog_layout.addWidget(color_label)

        color_btn = QPushButton()
        current_color = get_category_color(category)
        color_btn.setStyleSheet(f"background-color: {current_color}; min-height: 30px;")
        color_btn.clicked.connect(lambda: self.show_color_picker(color_btn))
        dialog_layout.addWidget(color_btn)


        button_layout = QHBoxLayout()
        delete_btn = QPushButton("Delete Category")
        delete_btn.setStyleSheet("background-color: #FF5555; color: white;")
        delete_btn.clicked.connect(lambda: self.delete_category(category, dialog))

        save_btn = QPushButton("Save Changes")
        save_btn.setDefault(True)

        def save_changes():
            new_name = name_input.text().strip()
            if new_name and new_name != category:

                for note_id, note_data in self.notes.items():
                    if note_data.get("category") == category:
                        note_data["category"] = new_name


                if category in self.categories:
                    self.categories.remove(category)
                if new_name not in self.categories:
                    self.categories.append(new_name)
                    self.categories.sort()


                self.save_notes()
                self.load_categories()
                self.show_category(new_name)

            dialog.accept()

        save_btn.clicked.connect(save_changes)

        button_layout.addWidget(delete_btn)
        button_layout.addWidget(save_btn)
        dialog_layout.addLayout(button_layout)

        dialog.exec()

    def show_color_picker(self, button):
        """Show a color picker dialog for category colors"""
        current_color = button.palette().button().color()
        color = QColorDialog.getColor(current_color, self, "Select Category Color")
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}; min-height: 30px;")

    def delete_category(self, category, dialog):
        """Delete a category and reset notes to Uncategorized"""
        reply = QMessageBox.question(
            self,
            "Delete Category",
            f"Are you sure you want to delete the category '{category}'?\nNotes in this category will be moved to Uncategorized.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:

            for note_id, note_data in self.notes.items():
                if note_data.get("category") == category:
                    note_data["category"] = "Uncategorized"


            if category in self.categories:
                self.categories.remove(category)


            self.save_notes()
            self.load_categories()
            self.show_all_notes()
            dialog.accept()

    def add_new_category(self):
        """Show dialog to add a new category"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Category")
        dialog.setFixedWidth(300)

        dialog_layout = QVBoxLayout(dialog)


        label = QLabel("Category Name:")
        dialog_layout.addWidget(label)

        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter category name")
        dialog_layout.addWidget(name_input)


        color_label = QLabel("Category Color:")
        dialog_layout.addWidget(color_label)

        default_color = "#FF69B4"
        color_btn = QPushButton()
        color_btn.setStyleSheet(f"background-color: {default_color}; min-height: 30px;")
        color_btn.clicked.connect(lambda: self.show_color_picker(color_btn))
        dialog_layout.addWidget(color_btn)


        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)

        add_btn = QPushButton("Add Category")
        add_btn.setDefault(True)

        def add_category():
            category_name = name_input.text().strip()
            if not category_name:
                QMessageBox.warning(dialog, "Invalid Name", "Please enter a category name.")
                return

            if category_name in self.categories:
                QMessageBox.warning(dialog, "Duplicate Category", f"Category '{category_name}' already exists.")
                return


            self.categories.append(category_name)
            self.categories.sort()


            self.load_categories()
            self.show_category(category_name)
            dialog.accept()

        add_btn.clicked.connect(add_category)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(add_btn)
        dialog_layout.addLayout(button_layout)

        dialog.exec()

    def generate_note_id(self):
        return datetime.now().strftime("%Y%m%d%H%M%S%f")

    def load_notes(self):
        if os.path.exists(NOTES_FILE):
            try:
                with open(NOTES_FILE, 'r') as f:
                    self.notes = json.load(f)
            except json.JSONDecodeError:
                self.notes = {}
                QMessageBox.warning(self, "Load Error", "Could not load notes.json. File might be corrupted.")
        else:
            self.notes = {}

    def save_notes(self):
        try:
            with open(NOTES_FILE, 'w') as f:
                json.dump(self.notes, f, indent=4)
        except IOError:
            QMessageBox.critical(self, "Save Error", "Could not save notes to notes.json.")

    def check_expired_notes(self):
        """Check and handle both temporary notes and recycle bin notes older than 30 days"""
        current_time = datetime.now()
        notes_to_delete = []

        for note_id, note_data in self.notes.items():

            if not isinstance(note_data, dict):
                print(f"Warning: Corrupted note data found for ID {note_id}. Skipping...")
                notes_to_delete.append(note_id)
                continue

            try:

                if note_data.get("temporary", False):
                    created_at = datetime.fromisoformat(note_data.get("created_at", current_time.isoformat()))
                    age = current_time - created_at


                    if age.days >= 30:
                        notes_to_delete.append(note_id)


                if note_data.get("deleted", False):
                    deleted_at = datetime.fromisoformat(note_data.get("deleted_at", current_time.isoformat()))
                    time_in_bin = current_time - deleted_at


                    if time_in_bin.days >= 30:
                        notes_to_delete.append(note_id)
            except (ValueError, TypeError, KeyError) as e:
                print(f"Warning: Error processing note {note_id}: {str(e)}. Skipping...")
                continue


        for note_id in notes_to_delete:
            del self.notes[note_id]


        if notes_to_delete:
            print(f"Deleted {len(notes_to_delete)} expired/corrupted notes")
            self.save_notes()

    def add_or_update_note(self, note_id=None, title="", content="", is_temporary=False, category=None):
        if not note_id:
            note_id = self.generate_note_id()
            created_at = datetime.now().isoformat()

            if category is None and self.current_filter == "category":
                category = self.current_category
        else:
            created_at = self.notes.get(note_id, {}).get("created_at", datetime.now().isoformat())

            if category is None:
                category = self.notes.get(note_id, {}).get("category", "Uncategorized")

        self.notes[note_id] = {
            "title": title,
            "content": content,
            "created_at": created_at,
            "updated_at": datetime.now().isoformat(),
            "category": category or "Uncategorized",
            "favorite": self.notes.get(note_id, {}).get("favorite", False),
            "temporary": is_temporary,
            "deleted": self.notes.get(note_id, {}).get("deleted", False),
            "deleted_at": self.notes.get(note_id, {}).get("deleted_at", None)
        }
        self.save_notes()
        self.load_categories()
        self.display_filtered_notes()

    def create_new_note_popup(self):
        if self.active_popup:
            self.active_popup.close()


        is_temporary = (self.current_filter == "temporary_notes")
        category = self.current_category if self.current_filter == "category" else None


        self.active_popup = CategoryNotePopup(
            self.main_widget,
            on_save=self.add_or_update_note,
            is_temporary=is_temporary,
            categories=self.categories,
            initial_category=category
        )
        self.active_popup.show()


        if hasattr(self, 'buddy_companion') and self.buddy_companion.isVisible():
            self.buddy_companion.raise_()

    def edit_note_popup(self, note_id):
        note = self.notes.get(note_id)
        if not note:
            return

        if self.active_popup:
            self.active_popup.close()


        self.active_popup = CategoryNotePopup(
            self.main_widget,
            on_save=self.add_or_update_note,
            note_id=note_id,
            title=note["title"],
            content=note["content"],
            is_temporary=note.get("temporary", False),
            categories=self.categories,
            initial_category=note.get("category", "Uncategorized")
        )
        self.active_popup.show()


        if hasattr(self, 'buddy_companion') and self.buddy_companion.isVisible():
            self.buddy_companion.raise_()

    def toggle_favorite(self, note_id):
        if note_id in self.notes:
            self.notes[note_id]["favorite"] = not self.notes[note_id]["favorite"]
            self.save_notes()
            self.display_filtered_notes()

    def delete_note_confirmed(self, note_id, permanent=False):
        if note_id in self.notes:
            if permanent:

                del self.notes[note_id]
            else:

                self.notes[note_id]["deleted"] = True
                self.notes[note_id]["deleted_at"] = datetime.now().isoformat()
            self.save_notes()
            self.display_filtered_notes()

    def delete_note_prompt(self, note_id):
        note = self.notes.get(note_id)
        if not note:
            return

        reply = QMessageBox.question(self, 'Delete Note',
                                     f"Are you sure you want to delete '{note['title'] or 'Untitled'}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_note_confirmed(note_id)

    def restore_note(self, note_id):
        if note_id in self.notes:
            self.notes[note_id]["deleted"] = False
            self.notes[note_id]["deleted_at"] = None
            self.save_notes()
            self.display_filtered_notes()

    def show_all_notes(self):
        self.show_notes_view()
        self.current_filter = "home"
        self.section_title.setText("All Notes")
        self.temp_notes_explanation_label.setVisible(False)
        self.display_filtered_notes()
        self.update_active_nav_button()

    def show_favorite_notes(self):
        self.show_notes_view()
        self.current_filter = "favorites"
        self.section_title.setText("Favorites")
        self.temp_notes_explanation_label.setVisible(False)
        self.display_filtered_notes()
        self.update_active_nav_button()

    def show_temporary_notes(self):
        self.show_notes_view()
        self.current_filter = "temporary_notes"
        self.section_title.setText("Temporary Notes")
        self.temp_notes_explanation_label.setVisible(True)
        self.display_filtered_notes()
        self.update_active_nav_button()

    def update_active_nav_button(self):
        for key, btn in self.sidebar.nav_buttons_widgets.items():
            is_active = (key == self.current_filter)
            btn.setChecked(is_active)
            if hasattr(self.sidebar, 'get_modern_button_style'):

                 is_settings = (key == "settings")
                 btn.setStyleSheet(self.sidebar.get_modern_button_style(is_sidebar_item=True, is_checked=is_active, is_settings_button=is_settings))

    def get_num_columns(self):


        container_width = self.scroll_area.viewport().width() if self.scroll_area.viewport() else self.scroll_area.width()
        card_min_width = 220
        num_cols = max(1, container_width // card_min_width)
        return num_cols

    def display_filtered_notes(self):


        if self.current_filter == "temporary_notes":
            self.temp_notes_explanation_label.setVisible(True)
            self.temp_notes_explanation_label.setText("Notes in this section are temporary and will be automatically deleted after 30 days.")
        elif self.current_filter == "recycle_bin":
            self.temp_notes_explanation_label.setVisible(True)
            self.temp_notes_explanation_label.setText("Notes in the recycle bin will be permanently deleted after 30 days.")
        else:
            self.temp_notes_explanation_label.setVisible(False)


        self.update_category_tag(self.current_category if self.current_filter == "category" else None)


        active_notes_dict = {}
        if self.current_filter == "home":
            active_notes_dict = {k:v for k,v in self.notes.items() if not v.get("deleted", False)}
        elif self.current_filter == "favorites":
            active_notes_dict = {k:v for k,v in self.notes.items() if v["favorite"] and not v.get("deleted", False)}
        elif self.current_filter == "temporary_notes":
            active_notes_dict = {k:v for k,v in self.notes.items() if v.get("temporary", False) and not v.get("deleted", False)}
        elif self.current_filter == "recycle_bin":
            active_notes_dict = {k:v for k,v in self.notes.items() if v.get("deleted", False)}
        elif self.current_filter == "category" and self.current_category:
            active_notes_dict = {k:v for k,v in self.notes.items()
                               if v.get("category") == self.current_category and not v.get("deleted", False)}


        while self.notes_layout.count():
            child = self.notes_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        if not active_notes_dict:
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.setContentsMargins(0, 60, 0, 0)
            no_notes_label = QLabel("No Notes")
            no_notes_label.setFont(QFont("San Francisco", 18))
            no_notes_label.setStyleSheet(f"color: {current_theme_colors['TEXT_TERTIARY']};")
            empty_layout.addWidget(no_notes_label)
            if self.current_filter == "recycle_bin":
                create_hint = QLabel("Deleted notes will appear here.")
                create_hint.setFont(QFont("San Francisco", 13))
                create_hint.setStyleSheet(f"color: {current_theme_colors['TEXT_TERTIARY']}; margin-top: 5px;")
                empty_layout.addWidget(create_hint)
            elif self.current_filter == "category":
                create_hint = QLabel(f"No notes in the '{self.current_category}' category. Create a new note or drag existing notes here.")
                create_hint.setFont(QFont("San Francisco", 13))
                create_hint.setStyleSheet(f"color: {current_theme_colors['TEXT_TERTIARY']}; margin-top: 5px;")
                create_hint.setWordWrap(True)
                empty_layout.addWidget(create_hint)
            elif self.current_filter != "favorites":
                create_hint = QLabel("Click 'Create Note' to add a new one.")
                create_hint.setFont(QFont("San Francisco", 13))
                create_hint.setStyleSheet(f"color: {current_theme_colors['TEXT_TERTIARY']}; margin-top: 5px;")
                empty_layout.addWidget(create_hint)
            empty_layout.addStretch()
            self.notes_layout.addWidget(empty_widget, 0, 0, 1, self.get_num_columns())
            return

        sorted_notes = sorted(active_notes_dict.items(), key=lambda item: item[1]['updated_at'], reverse=True)
        num_columns = self.get_num_columns()
        row, col = 0, 0
        for note_id, note_data in sorted_notes:
            if self.current_filter == "recycle_bin":

                note_widget = RecycleBinNoteWidget(
                    note_id, note_data["title"], note_data["content"],
                    note_data["favorite"], note_data.get("temporary", False),
                    note_data["created_at"], note_data["updated_at"],
                    note_data.get("deleted_at", ""),
                    on_restore=self.restore_note,
                    on_permanent_delete=lambda nid=note_id: self.delete_note_confirmed(nid, permanent=True),
                    parent=self
                )
            else:
                note_widget = NoteWidget(
                    note_id, note_data["title"], note_data["content"],
                    note_data["favorite"], note_data.get("temporary", False),
                    note_data["created_at"],  note_data["updated_at"],
                    category=note_data.get("category", "Uncategorized"),
                    on_click=self.edit_note_popup,
                    on_delete=self.delete_note_prompt,
                    on_favorite=self.toggle_favorite,
                    on_category_change=self.change_note_category
                )


                if self.current_filter != "category":
                    note_widget.setDragEnabled(True)

            self.notes_layout.addWidget(note_widget, row, col)
            col += 1
            if col >= num_columns:
                col = 0
                row += 1

    def change_note_category(self, note_id, new_category):
        """Change the category of a note"""
        if note_id in self.notes:

            self.notes[note_id]["category"] = new_category


            if new_category not in self.categories and new_category != "Uncategorized":
                self.categories.append(new_category)
                self.categories.sort()


            self.save_notes()
            self.load_categories()


            if self.current_filter == "category":
                if self.current_category == new_category:

                    self.display_filtered_notes()
                else:

                    self.display_filtered_notes()


                    QMessageBox.information(
                        self,
                        "Note Moved",
                        f"Note moved to '{new_category}' category."
                    )
            else:

                self.display_filtered_notes()

    def update_visible_note_countdowns(self):
        if not self.notes_widget_container.isVisible():
            return
        if self.current_filter != "temporary_notes" and self.current_filter != "home":

            return

        for i in range(self.notes_layout.count()):
            item = self.notes_layout.itemAt(i)
            if item:
                widget = item.widget()
                if isinstance(widget, NoteWidget) and widget.is_temporary:
                    widget.update_metadata_display()

                    if widget.get_formatted_expiry_countdown() == "Expired":

                        pass

    def resizeEvent(self, event):

        super().resizeEvent(event)

        QTimer.singleShot(100, self.display_filtered_notes)


        if hasattr(self, 'buddy_companion'):
            self.buddy_companion.reposition()

    def closeEvent(self, event):
        self.live_countdown_timer.stop()
        self.amogus_timer.stop()
        self.check_expired_notes()
        self.save_notes()
        super().closeEvent(event)

    def load_settings_and_apply_theme(self):
        global current_user_accent_color, current_theme_name, current_theme_colors, enable_amogus_jokes, current_buddy
        settings = {
            "accent_color": DEFAULT_ACCENT_COLOR,
            "theme": DEFAULT_THEME,
            "amogus_jokes": DEFAULT_AMOGUS_JOKES,
            "buddy": DEFAULT_BUDDY
        }

        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    loaded_settings = json.load(f)

                    if loaded_settings.get("theme") == "auto":
                        loaded_settings["theme"] = DEFAULT_THEME
                    settings.update(loaded_settings)
            except json.JSONDecodeError:
                print(f"Error decoding {SETTINGS_FILE}. Using default settings.")


        current_user_accent_color = settings.get("accent_color", DEFAULT_ACCENT_COLOR)
        current_theme_name = settings.get("theme", DEFAULT_THEME)
        enable_amogus_jokes = settings.get("amogus_jokes", DEFAULT_AMOGUS_JOKES)
        current_buddy = settings.get("buddy", DEFAULT_BUDDY)


        current_theme_colors = THEMES.get(current_theme_name, THEMES["light"])

        print(f"Applying Theme: {current_theme_name}, Accent: {current_user_accent_color}")
        self.apply_theme()


        if hasattr(self, 'buddy_companion'):
            self.buddy_companion.set_buddy(current_buddy)


        if enable_amogus_jokes and not self.amogus_timer.isActive():
            self.set_random_amogus_interval()
            self.amogus_timer.start()
        elif not enable_amogus_jokes and self.amogus_timer.isActive():
            self.amogus_timer.stop()

    def save_settings(self, new_settings):

        settings = {}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
            except json.JSONDecodeError:
                pass

        settings.update(new_settings)
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=4)
        except IOError:
            QMessageBox.critical(self, "Settings Error", f"Could not save to {SETTINGS_FILE}.")

    def apply_theme(self):
        global current_theme_colors
        print(f"Applying theme: {current_theme_name}, Accent: {current_user_accent_color}")


        self.main_widget.setStyleSheet(f"background-color: {current_theme_colors['BACKGROUND_MAIN']};")
        self.stacked_content_widget.setStyleSheet(f"border-left: 1px solid {current_theme_colors['BORDER_MEDIUM']};")


        if hasattr(self, 'section_title'):
            self.section_title.setStyleSheet(f"color: {current_theme_colors['TEXT_PRIMARY']}; padding-bottom: 0px;")
        if hasattr(self, 'temp_notes_explanation_label'):
             self.temp_notes_explanation_label.setStyleSheet(f"color: {current_theme_colors['TEXT_SECONDARY']}; padding-bottom: 10px;")
        if hasattr(self, 'scroll_area'):
            self.scroll_area.setStyleSheet(f"""
                QScrollArea {{ background-color: transparent; border: none; }}
                QScrollBar:vertical {{ background: {current_theme_colors['BACKGROUND_MAIN']}; width: 10px; margin: 0px; border-radius: 5px; }}
                QScrollBar::handle:vertical {{ background: {current_theme_colors['SCROLLBAR_HANDLE']}; min-height: 25px; border-radius: 5px; }}
                QScrollBar::handle:vertical:hover {{ background: {current_theme_colors['SCROLLBAR_HANDLE_HOVER']}; }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
            """)


        if hasattr(self, 'sidebar'):
            self.sidebar.apply_styles()


        if hasattr(self, 'settings_view'):
            self.settings_view.apply_styles()


        if hasattr(self, 'buddy_companion') and hasattr(self.buddy_companion, 'chat_window') and self.buddy_companion.chat_window:
            self.buddy_companion.chat_window.apply_styles()


        self.update_visible_note_widget_styles()


        if self.active_popup:
             self.active_popup.apply_styles()

        print("Theme fully applied.")

    def update_visible_note_widget_styles(self):
         if not self.notes_widget_container.isVisible():
            return
         for i in range(self.notes_layout.count()):
            item = self.notes_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), NoteWidget):
                widget = item.widget()
                widget.apply_styles()


    def show_notes_view(self):
        self.stacked_content_widget.setCurrentWidget(self.notes_page_widget)

    def show_settings_view(self):
        self.stacked_content_widget.setCurrentWidget(self.settings_view)
        self.current_filter = "settings"
        self.update_active_nav_button()

    def show_recycle_bin(self):
        self.show_notes_view()
        self.current_filter = "recycle_bin"
        self.section_title.setText("Recycle Bin")
        self.temp_notes_explanation_label.setVisible(True)
        self.temp_notes_explanation_label.setText("Items in the recycle bin will be permanently deleted after 30 days.")
        self.display_filtered_notes()
        self.update_active_nav_button()

    def set_random_amogus_interval(self):

        interval = random.randint(10 * 60 * 1000, 60 * 60 * 1000)
        self.amogus_timer.setInterval(interval)

    def maybe_create_amogus_joke(self):

        if enable_amogus_jokes and random.random() < 0.2:

            joke = random.choice(AMOGUS_JOKES)
            note_id = self.generate_note_id()
            created_at = datetime.now().isoformat()

            self.notes[note_id] = {
                "title": joke["title"],
                "content": joke["content"],
                "created_at": created_at,
                "updated_at": created_at,
                "category": "Amogus",
                "favorite": False,
                "temporary": True
            }
            self.save_notes()


            if self.current_filter in ["home", "temporary_notes"]:
                self.display_filtered_notes()


            notification = QMessageBox(self)
            notification.setWindowTitle("Sus Activity Detected")
            notification.setText(f"Emergency Meeting! A new '{joke['title']}' note was created.")
            notification.setStandardButtons(QMessageBox.StandardButton.Ok)
            notification.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {current_theme_colors['BACKGROUND_MAIN']};
                    color: {current_theme_colors['TEXT_PRIMARY']};
                }}
                QLabel {{
                    color: {current_theme_colors['TEXT_PRIMARY']};
                }}
                QPushButton {{
                    background-color: {current_user_accent_color};
                    border-radius: 4px;
                    min-width: 80px;
                    min-height: 30px;
                    color: {get_contrasting_text_color(current_user_accent_color)};
                    font-weight: bold;
                }}
            """)

            icon_path = "images/amogus.webp"
            if os.path.exists(icon_path):
                notification.setWindowIcon(QIcon(icon_path))
            notification.exec()


        self.set_random_amogus_interval()
        self.amogus_timer.start()

    def show_chat_view(self):
        """Show the chat view in the main window"""
        self.stacked_content_widget.setCurrentWidget(self.chat_view)
        self.current_filter = "chat"
        self.update_active_nav_button()

class RecycleBinNoteWidget(QWidget):
    def __init__(self, note_id, title, content_preview, favorite, is_temporary,
                 created_at, updated_at, deleted_at, on_restore, on_permanent_delete, parent=None):
        super().__init__(parent)
        self.note_id = note_id
        self.title_text = title
        self.content_text = content_preview
        self.is_favorite = favorite
        self.is_temporary = is_temporary
        self.created_at_str = created_at
        self.updated_at_str = updated_at
        self.deleted_at_str = deleted_at
        self.on_restore = on_restore
        self.on_permanent_delete = on_permanent_delete

        self.setMinimumHeight(150)
        self.apply_styles()

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 10)
        main_layout.setSpacing(8)

        self.preview_area = QFrame()
        self.preview_area.setMinimumHeight(80)
        self.preview_area.setStyleSheet(f"""
            QFrame {{
                background-color: {current_theme_colors['BACKGROUND_CARD_PREVIEW']};
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom: 1px solid {current_theme_colors['BORDER_LIGHT']};
            }}
        """)
        preview_area_layout = QVBoxLayout(self.preview_area)
        preview_area_layout.setContentsMargins(12, 10, 12, 10)
        preview_text_full = self.content_text.replace("\n", " \n")
        max_chars_preview = 100
        elided_preview = preview_text_full[:max_chars_preview] + ("..." if len(preview_text_full) > max_chars_preview else "")
        preview_label = QLabel(elided_preview if elided_preview else "No content preview")
        preview_label.setFont(QFont("San Francisco", 11))
        preview_label.setStyleSheet(f"color: {current_theme_colors['TEXT_SECONDARY']}; background-color: transparent;")
        preview_label.setWordWrap(True)
        preview_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        preview_area_layout.addWidget(preview_label)
        main_layout.addWidget(self.preview_area, 1)

        title_container = QWidget()
        title_container_layout = QVBoxLayout(title_container)
        title_container_layout.setContentsMargins(12, 5, 12, 0)
        title_label = QLabel(self.title_text if self.title_text else "Untitled")
        title_label.setFont(QFont("San Francisco", 12, QFont.Weight.DemiBold))
        title_label.setStyleSheet(f"color: {current_theme_colors['TEXT_PRIMARY']}; background-color: transparent;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_container_layout.addWidget(title_label)
        main_layout.addWidget(title_container)

        self.metadata_layout_widget = QWidget()
        metadata_layout = QHBoxLayout(self.metadata_layout_widget)
        metadata_layout.setContentsMargins(12, 0, 12, 0)
        metadata_layout.setSpacing(6)

        self.deletion_label = QLabel()
        self.deletion_label.setFont(QFont("San Francisco", 10))
        self.deletion_label.setStyleSheet(f"color: {current_theme_colors['TEXT_TERTIARY']}; background-color: transparent;")
        self.update_deletion_display()
        metadata_layout.addWidget(self.deletion_label)
        metadata_layout.addStretch()


        action_layout = QHBoxLayout()
        action_layout.setSpacing(6)

        restore_btn = QToolButton()
        restore_btn.setIcon(QIcon.fromTheme("document-revert", QIcon()))
        restore_btn.setText("↺")
        restore_btn.setToolTip("Restore Note")
        restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restore_btn.clicked.connect(self._handle_restore)
        restore_btn.setStyleSheet(f"""
            QToolButton {{
                color: {current_user_accent_color};
                background-color: transparent;
                border: none;
                padding: 3px;
                font-size: 16px;
            }}
            QToolButton:hover {{ background-color: {current_theme_colors['BORDER_LIGHT']}; }}
        """)
        action_layout.addWidget(restore_btn)

        delete_btn = QToolButton()
        delete_btn.setIcon(QIcon.fromTheme("edit-delete", QIcon()))
        delete_btn.setText("🗑️")
        delete_btn.setToolTip("Permanently Delete")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(self._handle_permanent_delete)
        delete_btn.setStyleSheet(f"""
            QToolButton {{
                color: #FF5555;
                background-color: transparent;
                border: none;
                padding: 3px;
                font-size: 16px;
            }}
            QToolButton:hover {{ background-color: {current_theme_colors['BORDER_LIGHT']}; }}
        """)
        action_layout.addWidget(delete_btn)

        metadata_layout.addLayout(action_layout)

        main_layout.addWidget(self.metadata_layout_widget)

    def apply_styles(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {current_theme_colors['BACKGROUND_CARD']};
                border-radius: 8px;
                border: 1px solid {current_theme_colors['BORDER_LIGHT']};
            }}
            QWidget:hover {{
                border-color: {current_theme_colors['BORDER_MEDIUM']};
            }}
        """)

        if hasattr(self, 'graphicsEffect') and isinstance(self.graphicsEffect(), QGraphicsDropShadowEffect):
            self.graphicsEffect().setColor(QColor(current_theme_colors['SHADOW_COLOR']))

        if hasattr(self, 'preview_area'):
            self.preview_area.setStyleSheet(f"""
                QFrame {{
                    background-color: {current_theme_colors['BACKGROUND_CARD_PREVIEW']};
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    border-bottom: 1px solid {current_theme_colors['BORDER_LIGHT']};
                }}
            """)

        if hasattr(self, 'deletion_label'):
            self.update_deletion_display()

    def update_deletion_display(self):
        try:
            deletion_date = datetime.fromisoformat(self.deleted_at_str)
            days_left = 30 - (datetime.now() - deletion_date).days
            days_left = max(0, days_left)

            if days_left > 1:
                deletion_text = f"Deleted · {days_left} days left"
            elif days_left == 1:
                deletion_text = "Deleted · 1 day left"
            else:
                deletion_text = "Deleted · Will be removed soon"

            self.deletion_label.setText(deletion_text)
            self.deletion_label.setStyleSheet(f"color: {current_theme_colors['TEXT_TERTIARY']}; background-color: transparent;")
        except (ValueError, TypeError):
            self.deletion_label.setText("Deleted")

    def _handle_restore(self):
        self.on_restore(self.note_id)

    def _handle_permanent_delete(self):
        reply = QMessageBox.question(self, 'Permanently Delete',
                                     f"Permanently delete '{self.title_text or 'Untitled'}'? This cannot be undone.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.on_permanent_delete()

class AmogusCompanion(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent


        self.setFixedSize(100, 100)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)


        if parent:
            self.move(parent.width() - self.width() - 20, parent.height() - self.height() - 20)


        self.setVisible(False)


        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)


        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(True)
        self.image_label.setFixedSize(100, 100)

        self.image_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout.addWidget(self.image_label)


        self.chat_window = None


        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.chat_window:

                self.chat_window = AmogusBuddyChat(self.parent.window())
            self.chat_window.show()
            self.chat_window.raise_()

    def set_buddy(self, buddy_file):
        """Set the buddy image from a file"""
        if not buddy_file:
            self.setVisible(False)
            return

        buddy_path = BUDDIES_FOLDER / buddy_file
        if not os.path.exists(buddy_path):
            print(f"Error: Buddy file {buddy_path} not found")
            self.setVisible(False)
            return

        pixmap = QPixmap(str(buddy_path))
        if pixmap.isNull():
            print(f"Error: Failed to load buddy image {buddy_path}")
            self.setVisible(False)
            return

        self.image_label.setPixmap(pixmap)
        self.setVisible(True)

    def reposition(self):
        """Reposition the buddy when parent resizes"""
        if self.parent:

            self.move(self.parent.width() - self.width() - 20,
                      self.parent.height() - self.height() - 20)

class AmogusBuddyChat(QWidget):
    def __init__(self, parent_window):
        super().__init__(None)
        self.parent_window = parent_window


        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)


        self.setFixedSize(450, 500)


        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)


        self.container = QWidget()
        self.container.setObjectName("chatContainer")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 15, 20, 15)
        container_layout.setSpacing(15)


        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 10)


        title = GradientLabel("Chat with Amogus Buddy")
        title.setFont(QFont("San Francisco", 16, QFont.Weight.Bold))
        header_layout.addWidget(title, 1, Qt.AlignmentFlag.AlignCenter)

        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.clicked.connect(self.close)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {current_theme_colors['TEXT_SECONDARY']};
                font-size: 20px;
            }}
            QPushButton:hover {{
                color: {current_theme_colors['TEXT_PRIMARY']};
            }}
        """)
        header_layout.addWidget(close_btn)
        container_layout.addLayout(header_layout)


        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.chat_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background-color: {current_theme_colors['BACKGROUND_MAIN']};
                width: 8px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background-color: {current_theme_colors['BORDER_MEDIUM']};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {current_theme_colors['BORDER_MEDIUM']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)


        self.chat_content = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(10)
        self.chat_scroll.setWidget(self.chat_content)
        container_layout.addWidget(self.chat_scroll)


        self.add_message("I can help you with:\n• Creating new notes\n• Showing your recent notes\n• Managing temporary notes\n• Opening settings\n• Accessing the recycle bin\n\nJust tell me what you'd like to do!")


        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 10, 0, 0)
        input_layout.setSpacing(10)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.returnPressed.connect(self.handle_input)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {current_theme_colors['BACKGROUND_CARD']};
                border: 1px solid {current_theme_colors['BORDER_LIGHT']};
                border-radius: 20px;
                padding: 10px 15px;
                color: {current_theme_colors['TEXT_PRIMARY']};
            }}
            QLineEdit:focus {{
                border-color: {current_user_accent_color};
            }}
        """)
        input_layout.addWidget(self.input_field)

        send_btn = QPushButton("↑")
        send_btn.setFixedSize(40, 40)
        send_btn.clicked.connect(self.handle_input)
        send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {current_user_accent_color};
                border-radius: 20px;
                color: {get_contrasting_text_color(current_user_accent_color)};
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {QColor(current_user_accent_color).darker(110).name()};
            }}
        """)
        input_layout.addWidget(send_btn)

        container_layout.addWidget(input_container)


        layout.addWidget(self.container)


        self.apply_styles()

    def showEvent(self, event):

        if self.parent_window and hasattr(self.parent_window, 'buddy_companion'):
            buddy = self.parent_window.buddy_companion
            if buddy.isVisible():

                window_rect = self.parent_window.geometry()
                buddy_pos = buddy.mapToGlobal(QPoint(0, 0))


                x = buddy_pos.x() - self.width() - 20
                y = buddy_pos.y() + buddy.height() - self.height()


                if x < window_rect.left():
                    x = buddy_pos.x() + buddy.width() + 20


                if x + self.width() > window_rect.right():
                    x = (window_rect.width() - self.width()) // 2 + window_rect.left()


                if y < window_rect.top():
                    y = window_rect.top() + 20
                elif y + self.height() > window_rect.bottom():
                    y = window_rect.bottom() - self.height() - 20

                self.move(x, y)
        super().showEvent(event)

    def handle_input(self):
        text = self.input_field.text().strip()
        if not text:
            return

        self.input_field.clear()
        self.add_message(text, is_user=True)


        text_lower = text.lower()
        if "create" in text_lower and "note" in text_lower:
            self.create_note_action()
        elif "recent" in text_lower or "show" in text_lower and "notes" in text_lower:
            self.show_recent_notes_action()
        elif "temp" in text_lower:
            self.view_temp_notes_action()
        elif "settings" in text_lower:
            self.open_settings_action()
        elif "delete" in text_lower or "recycle" in text_lower:
            if "note" in text_lower:
                self.delete_note_action()
            else:
                self.show_recycle_bin_action()
        elif "web" in text_lower:

            search_terms = text_lower.replace("web", "").strip()
            if search_terms:
                self.web_search_action(search_terms)
            else:
                self.add_message("What would you like me to search for on the web? Try something like 'web quantum computing' or 'web space exploration'.")
        elif "search" in text_lower or "find" in text_lower:
            search_terms = text_lower.replace("search", "").replace("find", "").strip()
            if search_terms:
                self.search_notes_action(search_terms)
            else:
                self.add_message("What would you like me to search for? Try something like 'search meeting notes' or 'find todo'.")
        elif "wikipedia" in text_lower or "wiki" in text_lower:
            search_terms = text_lower.replace("wikipedia", "").replace("wiki", "").strip()
            if search_terms:
                self.wikipedia_search_action(search_terms)
            else:
                self.add_message("What would you like me to look up on Wikipedia? Try something like 'wikipedia kebabs' or 'wiki space'.")
        else:
            self.add_message("I can help you with:\n• Creating notes\n• Showing recent notes\n• Managing temporary notes\n• Opening settings\n• Accessing the recycle bin\n• Searching notes (try 'search [term]')\n• Deleting notes (say 'delete note')\n• Wikipedia lookups (try 'wiki [topic]')\n• Web searches (try 'web [topic]')\n\nJust let me know what you'd like to do!")

    def web_search_action(self, search_terms):
        """Search the web and create a smart summary with references"""
        self.add_message(f"🔍 Searching the web for '{search_terms}'...", is_loading=True)

        try:

            results = self.web_search(search_terms)

            if not results:
                self.add_message(f"😕 I couldn't find any web results for '{search_terms}'.", is_success=True)
                return


            web_widget = QWidget()
            web_layout = QVBoxLayout(web_widget)
            web_layout.setContentsMargins(10, 5, 10, 5)


            title_label = QLabel(f"Search Results: {search_terms}")
            title_label.setFont(QFont("San Francisco", 14, QFont.Weight.Bold))
            title_label.setStyleSheet(f"color: {current_theme_colors['TEXT_PRIMARY']};")
            web_layout.addWidget(title_label)


            display_summary = ""
            references = []
            note_content_parts = []

            for result in results[:3]:
                snippet = result.get('snippet', '')
                title = result.get('title', '')
                url = result.get('link', '')


                snippet = ' '.join(snippet.split())

                if snippet and title and url:
                    display_summary += f"{snippet}\n\n"
                    references.append(f"• {title}\n  {url}")

                    note_content_parts.append(f"{snippet}")


            content_label = QLabel(display_summary.strip())
            content_label.setWordWrap(True)
            content_label.setTextFormat(Qt.TextFormat.PlainText)
            content_label.setOpenExternalLinks(True)
            content_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {current_theme_colors['BACKGROUND_CARD']};
                    color: {current_theme_colors['TEXT_PRIMARY']};
                    border: 1px solid {current_theme_colors['BORDER_LIGHT']};
                    border-radius: 8px;
                    padding: 12px;
                    line-height: 1.5;
                }}
            """)
            web_layout.addWidget(content_label)


            if references:
                ref_label = QLabel("References:")
                ref_label.setFont(QFont("San Francisco", 12, QFont.Weight.Bold))
                ref_label.setStyleSheet(f"color: {current_theme_colors['TEXT_PRIMARY']}; margin-top: 10px;")
                web_layout.addWidget(ref_label)

                ref_content_display = QLabel("\n".join(references))
                ref_content_display.setWordWrap(True)
                ref_content_display.setStyleSheet(f"""
                    QLabel {{
                        color: {current_theme_colors['TEXT_SECONDARY']};
                        padding: 5px;
                    }}
                """)
                web_layout.addWidget(ref_content_display)


            buttons_widget = QWidget()
            buttons_layout = QHBoxLayout(buttons_widget)
            buttons_layout.setContentsMargins(0, 5, 0, 0)


            copy_btn = QPushButton("📋 Copy Text")
            copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)

            copy_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {current_user_accent_color};
                    color: {get_contrasting_text_color(current_user_accent_color)};
                    border: none;
                    border-radius: 15px;
                    padding: 8px 15px;
                }}
                QPushButton:hover {{
                    background-color: {QColor(current_user_accent_color).darker(110).name()};
                }}
            """)

            def copy_to_clipboard():

                full_text_to_copy = "\n\n".join(note_content_parts)
                if references:
                    full_text_to_copy += "\n\nReferences:\n" + "\n".join(references)


                processed_text = "\n".join([' '.join(line.split()) for line in full_text_to_copy.split("\n")])

                QApplication.clipboard().setText(processed_text.strip())
                copy_btn.setText("✅ Copied!")
                QTimer.singleShot(2000, lambda: copy_btn.setText("📋 Copy Text"))

            copy_btn.clicked.connect(copy_to_clipboard)
            buttons_layout.addWidget(copy_btn)


            note_btn = QPushButton("📝 Create Note")
            note_btn.setCursor(Qt.CursorShape.PointingHandCursor)

            note_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {current_theme_colors['BACKGROUND_CARD']};
                    color: {current_theme_colors['TEXT_PRIMARY']};
                    border: 1px solid {current_theme_colors['BORDER_LIGHT']};
                    border-radius: 15px;
                    padding: 8px 15px;
                }}
                QPushButton:hover {{
                    background-color: {current_theme_colors['BORDER_LIGHT']};
                    border-color: {current_theme_colors['BORDER_MEDIUM']};
                }}
            """)

            def create_note_from_search():

                formatted_note_content = "\n\n".join(note_content_parts).strip()


                full_note_text = formatted_note_content
                if references:
                    full_note_text += "\n\nReferences:\n" + "\n".join(references)


                processed_text = "\n".join([' '.join(line.split()) for line in full_note_text.split("\n")])

                self.parent_window.add_or_update_note(
                    title=f"Web Nugget: {search_terms}",
                    content=processed_text.strip()
                )
                note_btn.setText("✅ Note Created!")
                QTimer.singleShot(2000, lambda: note_btn.setText("📝 Create Note"))

            note_btn.clicked.connect(create_note_from_search)
            buttons_layout.addWidget(note_btn)

            web_layout.addWidget(buttons_widget)


            msg_widget = QWidget()
            msg_layout = QVBoxLayout(msg_widget)
            msg_layout.setContentsMargins(10, 5, 10, 5)
            msg_layout.addWidget(web_widget)
            self.chat_layout.addWidget(msg_widget)


            QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
                self.chat_scroll.verticalScrollBar().maximum()
            ))

        except Exception as e:
            print(f"Web search error: {e}")
            self.add_message("😕 Sorry, I had trouble searching the web. Please try again later.", is_success=True)

    def web_search(self, query):
        """Helper function to perform web search using DuckDuckGo as a reliable alternative"""
        try:
            import os
            import requests
            from bs4 import BeautifulSoup

            print(f"[DEBUG] Performing search for: {query}")


            ddg_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://duckduckgo.com/",
                "DNT": "1"
            }

            print(f"[DEBUG] Requesting DuckDuckGo search: {ddg_url}")
            response = requests.get(ddg_url, headers=headers)
            print(f"[DEBUG] DuckDuckGo Status Code: {response.status_code}")


            with open("/tmp/ddg_page.html", "w", encoding="utf-8") as f:
                f.write(response.text)
                print(f"[DEBUG] Saved raw DuckDuckGo HTML to /tmp/ddg_page.html")


            soup = BeautifulSoup(response.text, 'html.parser')


            def test_selector(selector, soup_obj):
                print(f"[DEBUG] Testing selector: {selector}")
                elements = soup_obj.select(selector)
                print(f"[DEBUG] Found {len(elements)} elements with selector: {selector}")
                for i, elem in enumerate(elements[:2]):

                    text = elem.get_text(strip=True)

                    if len(text) > 100:
                        text = text[:100] + "..."
                    print(f"[DEBUG]   Element {i+1}: {text}")
                return elements


            test_selector('.result', soup)
            test_selector('.result__title', soup)
            test_selector('.result__snippet', soup)


            search_results = []
            result_elements = soup.select('.result')

            print(f"[DEBUG] Found {len(result_elements)} total results")

            for idx, result in enumerate(result_elements):
                if idx >= 5:
                    break

                title_elem = result.select_one('.result__title')
                snippet_elem = result.select_one('.result__snippet')
                link_elem = result.select_one('.result__url')

                if title_elem:

                    a_tag = title_elem.find('a')
                    title = a_tag.get_text(strip=True) if a_tag else title_elem.get_text(strip=True)


                    link = a_tag.get('href', '') if a_tag else ''

                    if link.startswith('/'):
                        link = f"https://duckduckgo.com{link}"


                    if link_elem:
                        visible_url = link_elem.get_text(strip=True)
                        if visible_url and not visible_url.startswith('http'):
                            visible_url = f"https://{visible_url}"
                            link = visible_url


                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""


                    import re
                    snippet = re.sub(r'([a-z])([A-Z])', r'\1 \2', snippet)


                    snippet = snippet.replace("AmogOSis", "AmogOS is")
                    snippet = snippet.replace("parodyOS", "parody OS")
                    snippet = snippet.replace("PiOS", "Pi OS")


                    snippet = ' '.join(snippet.split())


                    if not title or not snippet or len(snippet) < 10 or 'advertisement' in snippet.lower():
                        continue

                    search_results.append({
                        'title': title,
                        'link': link,
                        'snippet': snippet
                    })
                    print(f"[DEBUG] Added result: {title}")

            if not search_results:
                print("[DEBUG] No useful results found, using fallback")
                search_results = [{
                    'title': f"Search Results for: {query}",
                    'link': f"https://duckduckgo.com/?q={requests.utils.quote(query)}",
                    'snippet': f"Sorry, I couldn't find detailed results for '{query}'. You can try searching online directly."
                }]

            print(f"[DEBUG] Returning {len(search_results)} search results")
            return search_results

        except Exception as e:
            print(f"Web search error: {e}")
            import traceback
            traceback.print_exc()
            return [{
                'title': f"Search Results for: {query}",
                'link': f"https://duckduckgo.com/?q={requests.utils.quote(query)}",
                'snippet': f"Sorry, I encountered an error while searching. You can try searching online directly."
            }]

    def wikipedia_search_action(self, search_terms):
        """Search Wikipedia and display results with a copy button"""
        self.add_message(f"🔍 Searching Wikipedia for '{search_terms}'...", is_loading=True)

        try:
            import requests


            simple_url = f"https://simple.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "titles": search_terms,
                "redirects": True
            }

            response = requests.get(simple_url, params=params)
            data = response.json()
            page = next(iter(data["query"]["pages"].values()))


            if "extract" not in page or not page["extract"].strip():
                regular_url = f"https://en.wikipedia.org/w/api.php"
                response = requests.get(regular_url, params=params)
                data = response.json()
                page = next(iter(data["query"]["pages"].values()))

            if "extract" in page and page["extract"].strip():

                wiki_widget = QWidget()
                wiki_layout = QVBoxLayout(wiki_widget)
                wiki_layout.setContentsMargins(10, 5, 10, 5)


                title = page.get("title", search_terms)
                title_label = QLabel(title)
                title_label.setFont(QFont("San Francisco", 14, QFont.Weight.Bold))
                title_label.setStyleSheet(f"color: {current_theme_colors['TEXT_PRIMARY']};")
                wiki_layout.addWidget(title_label)


                content = page["extract"]
                content_label = QLabel(content)
                content_label.setWordWrap(True)
                content_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {current_theme_colors['BACKGROUND_CARD']};
                        color: {current_theme_colors['TEXT_PRIMARY']};
                        border: 1px solid {current_theme_colors['BORDER_LIGHT']};
                        border-radius: 8px;
                        padding: 12px;
                    }}
                """)
                wiki_layout.addWidget(content_label)


                buttons_widget = QWidget()
                buttons_layout = QHBoxLayout(buttons_widget)
                buttons_layout.setContentsMargins(0, 5, 0, 0)


                copy_btn = QPushButton("📋 Copy Text")
                copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                copy_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {current_user_accent_color};
                        color: {get_contrasting_text_color(current_user_accent_color)};
                        border: none;
                        border-radius: 15px;
                        padding: 8px 15px;
                    }}
                    QPushButton:hover {{
                        background-color: {QColor(current_user_accent_color).darker(110).name()};
                    }}
                """)

                def copy_to_clipboard():
                    source = "Source: Wikipedia"
                    if "simple.wikipedia.org" in response.url:
                        source = "Source: Simple English Wikipedia"
                    full_text = f"{content}\n\n{source}"
                    QApplication.clipboard().setText(full_text)
                    copy_btn.setText("✅ Copied!")
                    QTimer.singleShot(2000, lambda: copy_btn.setText("📋 Copy Text"))

                copy_btn.clicked.connect(copy_to_clipboard)
                buttons_layout.addWidget(copy_btn)


                note_btn = QPushButton("📝 Create Note")
                note_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                note_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {current_theme_colors['BACKGROUND_CARD']};
                        color: {current_theme_colors['TEXT_PRIMARY']};
                        border: 1px solid {current_theme_colors['BORDER_LIGHT']};
                        border-radius: 15px;
                        padding: 8px 15px;
                    }}
                    QPushButton:hover {{
                        background-color: {current_theme_colors['BORDER_LIGHT']};
                        border-color: {current_theme_colors['BORDER_MEDIUM']};
                    }}
                """)

                def create_note_from_wiki():
                    source = "Source: Wikipedia"
                    if "simple.wikipedia.org" in response.url:
                        source = "Source: Simple English Wikipedia"
                    full_text = f"{content}\n\n{source}"
                    self.parent_window.add_or_update_note(
                        title=f"Wiki: {title}",
                        content=full_text
                    )
                    note_btn.setText("✅ Note Created!")
                    QTimer.singleShot(2000, lambda: note_btn.setText("📝 Create Note"))

                note_btn.clicked.connect(create_note_from_wiki)
                buttons_layout.addWidget(note_btn)

                wiki_layout.addWidget(buttons_widget)


                msg_widget = QWidget()
                msg_layout = QVBoxLayout(msg_widget)
                msg_layout.setContentsMargins(10, 5, 10, 5)
                msg_layout.addWidget(wiki_widget)
                self.chat_layout.addWidget(msg_widget)


                QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
                    self.chat_scroll.verticalScrollBar().maximum()
                ))
            else:
                self.add_message(f"😕 I couldn't find any Wikipedia information about '{search_terms}'.", is_success=True)

        except Exception as e:
            print(f"Wikipedia search error: {e}")
            self.add_message("😕 Sorry, I had trouble accessing Wikipedia. Please try again later.", is_success=True)

    def add_message(self, text, is_user=False, is_loading=False, is_success=False, include_notes=None):
        msg_widget = QWidget()
        msg_layout = QVBoxLayout(msg_widget)
        msg_layout.setContentsMargins(10, 5, 10, 5)


        bubble_widget = QWidget()
        bubble_layout = QHBoxLayout(bubble_widget)
        bubble_layout.setContentsMargins(0, 0, 0, 0)

        if is_loading:
            loading_label = QLabel("⌛")
            bubble_layout.addWidget(loading_label)
            text = "Processing your request..."
        elif is_success:
            success_label = QLabel("✅")
            bubble_layout.addWidget(success_label)

        msg_label = QLabel(text)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(f"""
            QLabel {{
                background-color: {current_user_accent_color if is_user else current_theme_colors['BACKGROUND_CARD']};
                color: {get_contrasting_text_color(current_user_accent_color) if is_user else current_theme_colors['TEXT_PRIMARY']};
                border-radius: 10px;
                padding: 10px;
            }}
        """)

        if is_user:
            bubble_layout.addStretch()
        bubble_layout.addWidget(msg_label)
        if not is_user:
            bubble_layout.addStretch()

        msg_layout.addWidget(bubble_widget)


        if include_notes is not None:
            notes_widget = self.display_recent_notes(include_notes)
            msg_layout.addWidget(notes_widget)

        self.chat_layout.addWidget(msg_widget)


        QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        ))

        return msg_widget

    def display_recent_notes(self, notes_dict, title="Recent Notes"):
        notes_widget = QWidget()
        notes_layout = QVBoxLayout(notes_widget)
        notes_layout.setSpacing(8)


        sorted_notes = sorted(
            [(k, v) for k, v in notes_dict.items()],
            key=lambda x: x[1].get("updated_at", ""),
            reverse=True
        )[:5]

        if not sorted_notes:
            empty_label = QLabel("No notes found")
            empty_label.setStyleSheet(f"color: {current_theme_colors['TEXT_SECONDARY']};")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            notes_layout.addWidget(empty_label)
            return notes_widget

        for note_id, note_data in sorted_notes:
            note_btn = QPushButton()
            note_btn.setCursor(Qt.CursorShape.PointingHandCursor)


            title = note_data.get("title", "Untitled")
            preview = note_data.get("content", "")[:50] + "..." if len(note_data.get("content", "")) > 50 else note_data.get("content", "")


            if note_data.get("favorite", False):
                title = "★ " + title


            if note_data.get("temporary", False):
                title = "⏳ " + title


            if note_data.get("deleted", False):
                title = "🗑️ " + title

            note_btn.setText(f"{title}\n{preview}")


            note_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {current_theme_colors['BACKGROUND_CARD']};
                    border: 1px solid {current_theme_colors['BORDER_LIGHT']};
                    border-radius: 8px;
                    padding: 12px;
                    color: {current_theme_colors['TEXT_PRIMARY']};
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {current_theme_colors['BORDER_LIGHT']};
                    border-color: {current_theme_colors['BORDER_MEDIUM']};
                }}
            """)


            if note_data.get("deleted", False):
                note_btn.clicked.connect(lambda checked, nid=note_id: self.parent_window.restore_note(nid))
            else:
                note_btn.clicked.connect(lambda checked, nid=note_id: self.parent_window.edit_note_popup(nid))
            notes_layout.addWidget(note_btn)

        return notes_widget

    def create_note_action(self):
        self.add_message("Create a new note", is_user=True)
        loading_msg = self.add_message("", is_loading=True)
        self.parent_window.create_new_note_popup()
        loading_msg.deleteLater()
        self.add_message("✨ Created a new note for you!", is_success=True)

        self.add_message("Here are your recent notes:", include_notes=self.parent_window.notes)

    def show_recent_notes_action(self):
        self.add_message("Show my recent notes", is_user=True)
        loading_msg = self.add_message("", is_loading=True)
        self.parent_window.show_all_notes()
        loading_msg.deleteLater()
        self.add_message("📝 Here are your recent notes:", is_success=True, include_notes=self.parent_window.notes)

    def view_temp_notes_action(self):
        self.add_message("Show temporary notes", is_user=True)
        loading_msg = self.add_message("", is_loading=True)
        self.parent_window.show_temporary_notes()
        loading_msg.deleteLater()

        temp_notes = {k: v for k, v in self.parent_window.notes.items() if v.get("temporary", False)}
        self.add_message("⏳ Here are your temporary notes:", is_success=True, include_notes=temp_notes)

    def open_settings_action(self):
        self.add_message("Open settings", is_user=True)
        loading_msg = self.add_message("", is_loading=True)
        self.parent_window.show_settings_view()
        loading_msg.deleteLater()
        self.add_message("⚙️ Settings opened!", is_success=True)

    def show_recycle_bin_action(self):
        self.add_message("Show deleted notes", is_user=True)
        loading_msg = self.add_message("", is_loading=True)
        self.parent_window.show_recycle_bin()
        loading_msg.deleteLater()

        deleted_notes = {k: v for k, v in self.parent_window.notes.items() if v.get("deleted", True)}
        if deleted_notes:
            self.add_message("🗑️ Here are your deleted notes:", is_success=True, include_notes=deleted_notes)
        else:
            self.add_message("🗑️ The recycle bin is empty.", is_success=True)

    def apply_styles(self):

        self.container.setStyleSheet(f"""
            QWidget#chatContainer {{
                background-color: {current_theme_colors['BACKGROUND_MAIN']};
                border: 1px solid {current_theme_colors['BORDER_MEDIUM']};
                border-radius: 15px;
            }}
        """)


        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(current_theme_colors['SHADOW_COLOR']))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)


        self.chat_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background-color: {current_theme_colors['BACKGROUND_MAIN']};
                width: 8px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background-color: {current_theme_colors['SCROLLBAR_HANDLE']};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {current_theme_colors['SCROLLBAR_HANDLE_HOVER']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)


        self.chat_content.setStyleSheet(f"background-color: {current_theme_colors['BACKGROUND_MAIN']};")


        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {current_theme_colors['BACKGROUND_CARD']};
                border: 1px solid {current_theme_colors['BORDER_LIGHT']};
                border-radius: 20px;
                padding: 10px 15px;
                color: {current_theme_colors['TEXT_PRIMARY']};
            }}
            QLineEdit:focus {{
                border-color: {current_user_accent_color};
            }}
        """)


        for i in range(self.chat_layout.count()):
            widget = self.chat_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'findChildren'):

                widget.setStyleSheet(f"background-color: {current_theme_colors['BACKGROUND_MAIN']};")


                for btn in widget.findChildren(QPushButton):

                    if btn.text() and "Delete" in btn.text() and "Yes" in btn.text():
                        continue

                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {current_theme_colors['BACKGROUND_CARD']};
                            border: 1px solid {current_theme_colors['BORDER_LIGHT']};
                            border-radius: 8px;
                            padding: 12px;
                            color: {current_theme_colors['TEXT_PRIMARY']};
                            text-align: left;
                        }}
                        QPushButton:hover {{
                            background-color: {current_theme_colors['BORDER_LIGHT']};
                        }}
                    """)


                for label in widget.findChildren(QLabel):

                    if "background-color:" in label.styleSheet() and current_user_accent_color in label.styleSheet():
                        continue

                    label.setStyleSheet(f"""
                        color: {current_theme_colors['TEXT_PRIMARY']};
                        background-color: {current_theme_colors['BACKGROUND_CARD'] if "padding: 10px" in label.styleSheet() else "transparent"};
                    """)

    def search_notes_action(self, search_terms):
        """Search through notes and display matching results"""
        self.add_message(f"🔍 Searching for '{search_terms}'...", is_loading=True)


        matching_notes = {}
        for note_id, note_data in self.parent_window.notes.items():
            if note_data.get("deleted", False):
                continue

            title = note_data.get("title", "").lower()
            content = note_data.get("content", "").lower()


            for term in search_terms.split():
                if term in title or term in content:
                    matching_notes[note_id] = note_data
                    break


        if matching_notes:
            self.add_message(f"✨ Here are the notes I found matching '{search_terms}':",
                           is_success=True, include_notes=matching_notes)
        else:
            self.add_message(f"😕 I couldn't find any notes matching '{search_terms}'.",
                           is_success=True)

    def delete_note_action(self):
        """Show notes that can be deleted"""

        available_notes = {k: v for k, v in self.parent_window.notes.items()
                         if not v.get("deleted", False)}

        if not available_notes:
            self.add_message("😕 You don't have any notes to delete.", is_success=True)
            return

        self.add_message("Here are your notes. Click on one to delete it:", is_success=True)


        notes_widget = QWidget()
        notes_layout = QVBoxLayout(notes_widget)
        notes_layout.setSpacing(8)


        sorted_notes = sorted(
            available_notes.items(),
            key=lambda x: x[1].get("updated_at", ""),
            reverse=True
        )

        for note_id, note_data in sorted_notes:
            note_btn = QPushButton()
            note_btn.setCursor(Qt.CursorShape.PointingHandCursor)


            title = note_data.get("title", "Untitled")
            preview = note_data.get("content", "")[:50] + "..." if len(note_data.get("content", "")) > 50 else note_data.get("content", "")


            if note_data.get("favorite", False):
                title = "★ " + title
            if note_data.get("temporary", False):
                title = "⏳ " + title

            note_btn.setText(f"🗑️ {title}\n{preview}")


            note_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {current_theme_colors['BACKGROUND_CARD']};
                    border: 1px solid {current_theme_colors['BORDER_LIGHT']};
                    border-radius: 8px;
                    padding: 12px;
                    color: {current_theme_colors['TEXT_PRIMARY']};
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {current_theme_colors['BORDER_LIGHT']};
                    border-color: #FF5555;
                    color: #FF5555;
                }}
            """)


            note_btn.clicked.connect(lambda checked, nid=note_id, ntitle=title: self.confirm_delete_note(nid, ntitle))
            notes_layout.addWidget(note_btn)

        msg_widget = QWidget()
        msg_layout = QVBoxLayout(msg_widget)
        msg_layout.setContentsMargins(10, 5, 10, 5)
        msg_layout.addWidget(notes_widget)
        self.chat_layout.addWidget(msg_widget)


        QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        ))

    def confirm_delete_note(self, note_id, title):
        """Show confirmation before deleting a note"""
        self.add_message(f"Are you sure you want to delete '{title}'?")


        confirm_widget = QWidget()
        confirm_layout = QHBoxLayout(confirm_widget)
        confirm_layout.setContentsMargins(10, 5, 10, 5)

        yes_btn = QPushButton("Yes, Delete It")
        yes_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FF5555;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px 15px;
            }}
            QPushButton:hover {{
                background-color: #FF3333;
            }}
        """)
        yes_btn.clicked.connect(lambda: self.execute_delete_note(note_id, title))

        no_btn = QPushButton("No, Keep It")
        no_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {current_theme_colors['BORDER_LIGHT']};
                color: {current_theme_colors['TEXT_PRIMARY']};
                border: 1px solid {current_theme_colors['BORDER_MEDIUM']};
                border-radius: 15px;
                padding: 8px 15px;
            }}
            QPushButton:hover {{
                background-color: {current_theme_colors['BORDER_MEDIUM']};
            }}
        """)
        no_btn.clicked.connect(lambda: self.add_message("Okay, I won't delete it."))

        confirm_layout.addWidget(yes_btn)
        confirm_layout.addWidget(no_btn)

        msg_widget = QWidget()
        msg_layout = QVBoxLayout(msg_widget)
        msg_layout.setContentsMargins(10, 5, 10, 5)
        msg_layout.addWidget(confirm_widget)
        self.chat_layout.addWidget(msg_widget)


        QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        ))

    def execute_delete_note(self, note_id, title):
        """Actually delete the note"""
        self.parent_window.delete_note_confirmed(note_id)
        self.add_message(f"✅ Deleted note '{title}'. You can find it in the recycle bin.", is_success=True)

class BuddySelectionButton(QPushButton):
    def __init__(self, buddy_file, buddy_name):
        super().__init__()
        self.buddy_file = buddy_file
        self.buddy_name = buddy_name
        self.setFixedSize(100, 100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)


        self.image_container = QLabel()
        self.image_container.setFixedSize(70, 70)
        self.image_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_container.setStyleSheet("background: transparent;")


        if buddy_file:
            buddy_path = BUDDIES_FOLDER / buddy_file
            if os.path.exists(buddy_path):
                pixmap = QPixmap(str(buddy_path))
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(70, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.image_container.setPixmap(scaled_pixmap)

        else:
            self.image_container.setText("❌")
            self.image_container.setStyleSheet(f"""
                QLabel {{
                    color: {current_theme_colors['TEXT_SECONDARY']};
                    font-size: 24px;
                    background: transparent;
                }}
            """)

        layout.addWidget(self.image_container)


        self.name_label = QLabel(buddy_name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)


        if current_theme_name in ["dark", "amoled"]:
            text_color = "#FFFFFF"
        else:
            text_color = current_theme_colors['TEXT_PRIMARY']

        self.name_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                background: transparent;
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(self.name_label)

        self.apply_styles()

    def apply_styles(self):
        is_selected = (self.buddy_file == current_buddy)


        bg_color = current_theme_colors['BACKGROUND_CARD']
        text_color = get_contrasting_text_color(bg_color)


        if current_theme_name in ["dark", "amoled"]:
            label_color = "#FFFFFF"
        else:
            label_color = current_theme_colors['TEXT_PRIMARY']

        self.name_label.setStyleSheet(f"""
            QLabel {{
                color: {label_color};
                background: transparent;
                font-size: 12px;
                font-weight: bold;
            }}
        """)

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {current_theme_colors['BACKGROUND_CARD']};
                border: 2px solid {current_user_accent_color if is_selected else current_theme_colors['BORDER_LIGHT']};
                border-radius: 12px;
                padding: 5px;
                color: {text_color};
            }}
            QPushButton:hover {{
                background-color: {current_theme_colors['BORDER_LIGHT']};
                border-color: {current_user_accent_color};
            }}
        """)

    def setSelected(self, selected):
        self.apply_styles()

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(resource_path('images/Amogus.ico')))

    window = MainWindow()
    window.setWindowIcon(QtGui.QIcon(resource_path('images/Amogus.ico')))
    
    app.processEvents() 
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()