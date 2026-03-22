import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import telebot

class MessageCleaner:
    """
    Сервис для автоматического удаления старых сообщений.
    Хранит лог сообщений в JSON-файле и удаляет их по расписанию.
    Не зависит от планировщика, вызывается вручную перед отправкой дайджеста.
    """
    def __init__(self, bot: telebot.TeleBot, log_file: str = "message_log.json"):
        """
        Args:
            bot: Экземпляр бота для удаления сообщений.
            log_file: Путь к JSON-файлу для хранения логов.
        """
        self.bot = bot
        self.log_file = log_file
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Создает пустой JSON-файл, если его нет."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)
    
    def _load_log(self) -> Dict[str, List[Dict[str, Any]]]:
        """Загружает лог из файла"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _safe_log(self, log: Dict[str, List[Dict[str, Any]]]):
        """Сохраняет лог в файл"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2, ensure_ascii=False)
    
    def add_message(self, message_id: int, chat_id: int, delete_after_days: int, info: str):
        """
        Добавляет сообщение в лог для будущего удаления.
        
        Args:
            message_id: ID сообщения в Telegram.
            chat_id: ID чата.
            delete_after_days: Через сколько дней удалить (1 = следующие сутки).
            info: Информация о сообщении.
        """
        delete_time = datetime.now() + timedelta(days=delete_after_days)
        date_key = delete_time.strftime("%Y-%m-%d")

        log = self._load_log()

        if date_key not in log:
            log[date_key] = []

        log[date_key].append({
            'message_id': message_id,
            'chat_id': chat_id,
            'info': info,
        })

        self._safe_log(log)
        print(f"📝 Сообщение {message_id} - {info}... будет удалено утром {date_key}")

    def cleanup(self):
        """
        Удаляет все сообщения, запланированные на сегодня и раньше.
        Вызывать перед отправкой утреннего дайджеста.
        """
        log = self._load_log()
        today = datetime.now().strftime("%Y-%m-%d")

        messages_to_delete = []
        remaining_log = {}
        
        for date_key, messages in log.items():
            if date_key <= today:
                messages_to_delete.extend(messages) # Добавлем сообщения которые нужно удалить 
            else:
                remaining_log[date_key] = messages
        
        # Удаляем сообщения
        deleted_count = 0
        for msg in messages_to_delete:
            try:
                self.bot.delete_message(
                    chat_id=msg['chat_id'],
                    message_id=msg['message_id']
                )
                deleted_count += 1
                print(f"🧹 Удалено сообщение {msg['message_id']} - {msg['info']}")
            except Exception as e:
                print(f"⚠️ Не удалось удалить сообщение {msg['message_id']} - {msg['info']}: {e}")
        
        self._safe_log(remaining_log)

        if deleted_count > 0:
            print(f"✅ Очистка завершена. Удалено сообщений: {deleted_count}")