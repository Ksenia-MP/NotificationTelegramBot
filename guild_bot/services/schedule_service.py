from typing import List, Dict, Optional
from datetime import datetime
from models.event import Event
from config import config
from services.storage_service import CSVEventStorage

class ScheduleService:
    """Сервис для работы с расписанием событий"""
    
    # def __init__(self):
    #     self.schedule = self._init_schedule()

    def __init__(self, storage: Optional[CSVEventStorage] = None):
        """
        storage: Хранилище CSV. Если не указано создается новое с файлом по умолчанию.
        """
        self.storage = storage or CSVEventStorage()
        self.schedule = self._load_schedule()
    
    def _load_schedule(self) -> List[Event]:
        """Загружает расписание из хранилища"""
        return self.storage.load_events()
    
    def reload_schedule(self):
        """Перезагружает расписание из CSV"""
        self.schedule = self._load_schedule()
        print("🔄 Расписание перезагружено из CSV")

    def get_today_events(self) -> List[Event]:
        """События на сегодня"""
        today = datetime.now().weekday()
        events = [e for e in self.schedule if e.day == today]
        return sorted(events, key=lambda e: e.time)
    
    def get_all_by_day(self) -> Dict[str, List[Event]]:
        """Все события, сгруппированные по дням"""
        result = {}
        for event in self.schedule:
            day_name = config.DAYS[event.day]
            if day_name not in result:
                result[day_name] = []
            result[day_name].append(event)
        
        for day in result:
            result[day].sort(key=lambda e: e.time)
        return result
    
    def get_next_event(self) -> Event:
        """Ближайшее событие"""
        now = datetime.now()
        current_minutes = (now.hour + config.TIME_SHIFT) * 60 + now.minute
        current_day = now.weekday()
        
        nearest = None
        min_diff = float('inf')
        
        for event in self.schedule:
            # Пропускаем нотисы
            if event.is_notification: 
                continue

            days_ahead = event.day - current_day
            h, m = map(int, event.time.split(':'))
            event_minutes = h * 60 + m
            
            if days_ahead < 0 or (days_ahead == 0 and event_minutes <= current_minutes):
                days_ahead += 7
            
            total_minutes = days_ahead * 24 * 60 + event_minutes - current_minutes
            
            if total_minutes < min_diff:
                min_diff = total_minutes
                nearest = event
        
        return nearest