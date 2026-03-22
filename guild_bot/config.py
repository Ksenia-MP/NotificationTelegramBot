import os
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    """Все настройки бота в одном месте"""
    # Директории и пути к файлам расписания и логов для самоочиски
    BASE_DIR = Path(__file__).parent.parent # Выше на 2 директории чем config.py (D:\MyProjects\>>Guild<<\guild_bot\config.py)
    IMAGES_DIR = os.path.join(BASE_DIR, "images")
    SCHEDULE_CSV = os.path.join(BASE_DIR, "schedule.csv")
    MESSAGE_LOG_JSON = os.path.join(BASE_DIR, "message_log.json")

    BOT_TOKEN: str = "8745543448:AAGMklSx8e-8cnq2Ch4WC4HXBG4ugeSzu94"
    CHAT_ID: int = -1003778217245
    THREAD_ID: int = 3
    TIME_SHIFT: int = -1
    TIME_ZONE: str = "Europe/Moscow"
    MORNING_DIGEST_HOUR: int = 11
    MORNING_DIGEST_MINUTE: int = 00
    
    # Пути к картинкам
    IMAGE_PATHS = {
        'boss_1': os.path.join(IMAGES_DIR, "boss_6.jpg"),
        'boss_2': os.path.join(IMAGES_DIR, "boss_11.jpg"),
        'arena': os.path.join(IMAGES_DIR, "arena.jpg"),
        'join_realm': os.path.join(IMAGES_DIR, "join_realm.jpg"),
        'guild_war': os.path.join(IMAGES_DIR, "guild_war.jpg"),
        'guild_party': os.path.join(IMAGES_DIR, "guild_party.jpg"),
        'join_forest': os.path.join(IMAGES_DIR, "join_forest.jpg"),
        'gvg_rmdr': os.path.join(IMAGES_DIR, "GvG_rmdr.jpg"),
    }
    
    # Дни недели
    DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", 
            "Пятница", "Суббота", "Воскресенье"]

config = Config()