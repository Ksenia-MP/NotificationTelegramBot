import os
import time
from typing import Optional, List
import telebot
from config import config
from services.message_cleaner import MessageCleaner

class MessageService:
    """Сервис для отправки сообщений (с повторами, картинками)"""
    
    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot
        self.thread_id = config.THREAD_ID
        self.cleaner = None

    def _get_cleaner(self) -> MessageCleaner:
        """Ленивая инициаллизация MessageCleaner"""
        if self.cleaner is None:
            self.cleaner = MessageCleaner(self.bot)
        return self.cleaner
    
    def send_with_auto_delete(self, chat_id: int, text: str, 
                              delete_after_days: int,
                              pic: Optional[str] = None, 
                              info: str = "no info"):
        """Отправляет сообщение и автоматически добавляет его в очередь на удаление."""
        sent_message = self.send(chat_id, text, pic)

        if sent_message and hasattr(sent_message, 'message_id'):
            self._get_cleaner().add_message(
                message_id=sent_message.message_id,
                chat_id = chat_id,
                delete_after_days=delete_after_days,
                info=info
            )
        
        return sent_message
        

    def send(self, chat_id: int, text: str, 
             pic: Optional[str] = None, 
             options: Optional[List[str]] = None):
        """Основной метод отправки"""
        type = 'картинки' if pic else 'опроса' if options else 'текста'

        print(f"💬 Начинается отправка {type}")
        thread_id = self.thread_id if chat_id < 0 else None
        message_id = None
        if pic:
            message_id = self._send_photo_with_retry(chat_id, pic, text, thread_id)
        elif options:
            message_id = self._send_poll(chat_id, text, options, thread_id)
        else:
            message_id = self._send_text(chat_id, text, thread_id)
        
        print(f"✅ Отправка {type} выполнена")
        return message_id
    
    def _send_photo_with_retry(self, chat_id: int, pic: str, 
                               caption: str, thread_id: Optional[int]):
        """
        Отправка фото с повторами
        
        Returns: 
            ID отправленного сообщения или None при ошибке
        """
        if not os.path.exists(pic):
            return self._send_text(chat_id, f"{caption}\n\n(картинка не найдена)", thread_id)
                    
        for attempt in range(3):
            try:
                with open(pic, 'rb') as photo:
                    msg = self.bot.send_photo(
                        chat_id=chat_id,
                        photo=photo,
                        caption=caption,
                        message_thread_id=thread_id,
                        timeout=60,
                        parse_mode = 'HTML'
                    )
                print(f"   Фото отправлено с {attempt + 1} попытки")
                return msg
            except Exception as e:
                print(f"⚠️ Попытка {attempt + 1}/3: {e}")
                if attempt < 2:
                    time.sleep(3 * (attempt + 1))
        
        # Если все попытки провалились
        return self._send_text(chat_id, f"{caption}\n\n(не удалось загрузить картинку)", thread_id)
    
    def _send_poll(self, chat_id: int, question: str, 
                   options: List[str], thread_id: Optional[int]):
        """Отправка опроса"""
        return self.bot.send_poll(
            chat_id=chat_id,
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=True,
            message_thread_id=thread_id
        )
    
    def _send_text(self, chat_id: int, text: str, thread_id: Optional[int]):
        """Отправка текста"""
        return self.bot.send_message(
            chat_id=chat_id,
            text=text,
            message_thread_id=thread_id,
            parse_mode = 'HTML'
        )
    
    def cleanup_old_messages(self):
        """Запускает очистку старых сообщений"""
        return self._get_cleaner().cleanup()