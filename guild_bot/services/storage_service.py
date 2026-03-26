import csv
import os
from typing import List, Dict, Any
from models.event import Event
from config import config

class CSVEventStorage:
    """
    Сервис для хранения и загрузки событий из CSV-файла.
    Позволяет редактировать расписание без изменения кода.
    """
    
    def __init__(self, file_path: str = config.SCHEDULE_CSV):
        """
        Args:
            file_path: Путь к CSV-файлу с расписанием.
        """
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Создает файл с заголовками, если он не существует."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'day', 'time', 'description', 'image_key', 'is_notification'])
    
    def load_events(self) -> List[Event]:
        """
        Загружает события из CSV-файла.
        
        Returns:
            Список объектов Event.
        """
        events = []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Пропускаем пустые строки, если они есть
                    if not row.get('name'):
                        continue
                        
                    # Получаем путь к картинке, если указан ключ
                    image_url = None
                    if row.get('image_key'):
                        image_url = config.IMAGE_PATHS.get(row['image_key'])
                    
                    # Создаем событие. Флаг is_notification храним как bool
                    event = Event(
                        name=row['name'],
                        day=int(row['day']),
                        time=row['time'],
                        description=row.get('description', ''),
                        image_url=image_url,
                        is_notification=row.get('is_notification', 'False').lower() == 'true'
                    )
                    events.append(event)
            print(f"✅ Загружено {len(events)} событий из {self.file_path}")
        except FileNotFoundError:
            print(f"⚠️ Файл {self.file_path} не найден. Создан новый.")
        except Exception as e:
            print(f"❌ Ошибка при загрузке из CSV: {e}")
        
        return events
    
    def save_events(self, events: List[Event]):
        """
        Сохраняет список событий в CSV-файл.
        Полезно для команды /reload, если вы захотите редактировать файл через бота.
        
        Args:
            events: Список событий для сохранения.
        """
        try:
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                # Определяем ключ картинки по URL (обратная операция)
                reverse_image_map = {v: k for k, v in config.IMAGE_PATHS.items()}
                
                fieldnames = ['name', 'day', 'time', 'description', 'image_key', 'is_notification']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for event in events:
                    # Ищем ключ картинки
                    image_key = reverse_image_map.get(event.image_url, '')
                    
                    row = {
                        'name': event.name,
                        'day': event.day,
                        'time': event.time,
                        'description': event.description,
                        'image_key': image_key,
                        'is_notification': str(event.is_notification)
                    }
                    writer.writerow(row)
            print(f"✅ Сохранено {len(events)} событий в {self.file_path}")
        except Exception as e:
            print(f"❌ Ошибка при сохранении в CSV: {e}")
