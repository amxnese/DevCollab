COLOR_BG = "#0f1117"
COLOR_SURFACE = "#171a23"
COLOR_SURFACE_2 = "#1d212c"
COLOR_SURFACE_3 = "#252b38"
COLOR_BORDER = "#303747"
COLOR_ACCENT = "#7c5cff"
COLOR_ACCENT_HOVER = "#8e74ff"
COLOR_TEXT = "#f4f5f8"
COLOR_TEXT_DIM = "#9aa3b5"
COLOR_LIKE = "#42c98a"
COLOR_DISLIKE = "#ef6672"
COLOR_WOI = "#f0be57"
COLOR_COMPLETED = "#62d99e"
COLOR_DANGER = "#e85462"

APP_STYLESHEET = f"""
QWidget {{
    background: {COLOR_BG}; color: {COLOR_TEXT};
    font-family: 'Segoe UI', 'Inter', 'Ubuntu', sans-serif; font-size: 14px;
}}
QFrame#card, QFrame#taskCard, QFrame#commentCard {{
    background: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER}; border-radius: 14px;
}}
QFrame#taskCard:hover {{ border-color: #46506a; }}
QFrame#taskCard[selected="true"] {{ border: 1px solid {COLOR_ACCENT}; background: #1b1f2b; }}
QLabel#logoMark {{ background: {COLOR_ACCENT}; color: white; border-radius: 12px; font-size: 18px; font-weight: 900; padding: 8px 10px; }}
QLabel#brand {{ font-size: 18px; font-weight: 800; }}
QLabel#heroTitle {{ font-size: 31px; font-weight: 850; }}
QLabel#titleLabel {{ font-size: 23px; font-weight: 800; }}
QLabel#sectionTitle {{ font-size: 16px; font-weight: 750; }}
QLabel#subtitleLabel {{ color: {COLOR_TEXT_DIM}; font-size: 13px; }}
QLabel#muted {{ color: {COLOR_TEXT_DIM}; }}
QLabel#statusLabel {{ font-size: 12px; font-weight: 700; }}
QLineEdit, QTextEdit {{
    background: {COLOR_SURFACE_2}; border: 1px solid {COLOR_BORDER}; border-radius: 10px;
    padding: 10px 12px; color: {COLOR_TEXT}; selection-background-color: {COLOR_ACCENT};
}}
QLineEdit:focus, QTextEdit:focus {{ border-color: {COLOR_ACCENT}; }}
QPushButton {{
    background: {COLOR_ACCENT}; color: white; border: none; border-radius: 9px;
    padding: 10px 16px; font-weight: 700;
}}
QPushButton:hover {{ background: {COLOR_ACCENT_HOVER}; }}
QPushButton:disabled {{ background: #353b4b; color: #7e8798; }}
QPushButton#secondaryButton {{ background: {COLOR_SURFACE_2}; border: 1px solid {COLOR_BORDER}; color: {COLOR_TEXT}; }}
QPushButton#secondaryButton:hover {{ border-color: {COLOR_ACCENT}; }}
QPushButton#dangerButton {{ background: #3a1e24; color: #ff8b95; border: 1px solid #6f3039; }}
QPushButton#dangerButton:hover {{ background: {COLOR_DANGER}; color: white; }}
QPushButton#likeButton {{ background: #19372c; color: {COLOR_LIKE}; }}
QPushButton#dislikeButton {{ background: #3a2025; color: {COLOR_DISLIKE}; }}
QPushButton#statusButton {{ background: {COLOR_SURFACE_3}; color: {COLOR_TEXT}; }}
QListWidget, QScrollArea {{ background: transparent; border: none; }}
QListWidget::item {{ background: transparent; border: none; margin: 4px 0; }}
QListWidget::item:selected {{ background: transparent; }}
QScrollBar:vertical {{ background: transparent; width: 8px; }}
QScrollBar::handle:vertical {{ background: #3d4557; border-radius: 4px; min-height: 30px; }}
QDialog {{ background: {COLOR_SURFACE}; }}

QTabWidget#homeRoomTabs::pane {{
    border: none;
    background: transparent;
}}
QTabWidget#homeRoomTabs QTabBar::tab {{
    background: transparent;
    color: {COLOR_TEXT_DIM};
    border: none;
    border-bottom: 2px solid transparent;
    padding: 8px 3px 10px 3px;
    margin-right: 20px;
    font-size: 14px;
    font-weight: 700;
}}
QTabWidget#homeRoomTabs QTabBar::tab:hover {{ color: {COLOR_TEXT}; }}
QTabWidget#homeRoomTabs QTabBar::tab:selected {{
    color: {COLOR_TEXT};
    border-bottom: 2px solid {COLOR_ACCENT};
}}
QListWidget#roomList {{
    background: transparent; border: none; padding: 2px 0 6px 0;
}}
QListWidget#roomList::item {{
    background: transparent; border: none; margin: 0 0 5px 0; padding: 0;
}}
"""
