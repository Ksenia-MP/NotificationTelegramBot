from dataclasses import dataclass
from typing import Optional

@dataclass
class Event:
    """Класс для события (как Java POJO)"""
    name: str
    day: int
    time: str
    description: str = ""
    image_url: Optional[str] = None
    is_notification: bool = False
    
    def to_dict(self):
        """Преобразование в словарь (если нужно)"""
        return {
            'name': self.name,
            'day': self.day,
            'time': self.time,
            'description': self.description,
            'image_url': self.image_url,
            'is_notification': self.is_notification
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создание события из словаря"""
        return cls(
            name=data['name'],
            day=data['day'],
            time=data['time'],
            description=data.get('description', ''),
            image_url=data.get('image_url'),
            is_notification=data.get('is_notification', False)
        )