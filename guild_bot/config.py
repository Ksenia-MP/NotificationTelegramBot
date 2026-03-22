import os
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    """Все настройки бота в одном месте"""
    # Директории и пути к файлам расписания и логов для самоочиски
    BASE_DIR = Path(__file__).parent.parent # Выше на 2 директории чем config.py (С:\Path\to\project\>>NotificationTelegramBot<<\guild_bot\config.py)
    IMAGES_DIR = os.path.join(BASE_DIR, "images")
    SCHEDULE_CSV = os.path.join(BASE_DIR, "schedule.csv")
    MESSAGE_LOG_JSON = os.path.join(BASE_DIR, "message_log.json")

    BOT_TOKEN: str = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"    # Поставить свой токен бота полученный от @BotFather
    CHAT_ID: int = None        # Заменить на ID чата (формата -1234567890123), получить можно с помощью команды /test
    THREAD_ID: int = None      # Заменить на ID группы (если требуется), получить можно с помощью команды /test
    TIME_SHIFT: int = -1       # Сдвиг во времени относительно TIME_ZONE
    TIME_ZONE: str = "Europe/Moscow"    # Часовой пояс МСК (уведомления из schedule.csv будут приходить по указоннуму времени в данном часовом поясе)
    MORNING_DIGEST_HOUR: int = 11       # Время утреннего дайджеста
    MORNING_DIGEST_MINUTE: int = 00
    
    # Пути к картинкам (можно добавить свое)
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
