from services.message_service import MessageService
from services.schedule_service import ScheduleService
from models.event import Event
from config import config
from datetime import datetime
import time

class NotificationService:
    """Сервис для отправки уведомлений (дайджест, напоминания)"""
    
    def __init__(self, message_service: MessageService, 
                 schedule_service: ScheduleService):
        self.msg = message_service
        self.schedule = schedule_service
    
    def send_morning_digest(self):
        """Утренний дайджест (удаляется через день)"""
        try:
            # Очистка старых уведомлений
            self.msg.cleanup_old_messages()
            
            today = datetime.now().weekday()
            events = self.schedule.get_today_events()
            day_name = config.DAYS[today]
            
            message = f"🌅 Доброе утро!\nСегодня {day_name}.\n\n"
            
            if events:
                message += "📋 План на день:\n\n"
                first_image = events[0].image_url if hasattr(events[0], 'image_url') else None
                for event in events:
                    message += f"  • {event.name}\n  ⏰ {event.time}\n\n"
            else:
                message += "🎉 Событий не запланировано! Можно отдохнуть! 🎉\n\n"
                first_image = None
            
            message += (
                "Также не забываем про лес и прочие активности!\n"
                "/forest - ⚔️ Создать опрос на сбор команды в Perception Forest \n" 
                "/arena - ⚔️ Отметиться кто хочет сегодня сходить на арену на базе гильдии."
            )
            
            self.msg.send_with_auto_delete(
                config.CHAT_ID, 
                message, 
                delete_after_days=1,
                pic=first_image,
                info="morning_digest")
            print(f"✅ Утренний дайджест отправлен в {time.strftime('%H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Ошибка в дайджесте: {e}")
    
    def send_notification(self, event: Event, type: str):
        if type == 'reminder':
            text = (
                f"🔔 НАПОМИНАНИЕ! 🔔\n\n"
                f"⚔️ {event.name}\n"
                f"⏰ Начнется совсем скоро!\n"
                f"📍 Время сбора: {event.time}\n"
                f"📌 {event.description}\n\n"
                f"👥 Начинаем подготовку!"
            )
            pic = event.image_url
            days = 1
        elif type == 'start':
            text = (
                f"⚔️ ВНИМАНИЕ! ⚔️\n\n"
                f"🔸 {event.name}\n"
                f"⏰ НАЧИНАЕТСЯ СЕЙЧАС! {event.time}\n\n"
                f"👥 До встречи в чате гильдии!"
            )
            pic = None
            days = 1
        elif type == 'notification':
            text = (
                f"🔔 НАПОМИНАНИЕ!\n"
                f"•  {event.name}\n"
                f"📋 {event.description}"
            )
            pic = event.image_url
            days = 2
        
        self.msg.send_with_auto_delete(
            config.CHAT_ID,
            text,
            delete_after_days=days,
            pic=pic,
            info=f"{type} - {event.name}"
        )

        print(f"✅ Уведомление для {event.name} ({type}) отправлено")

    

# class NotificationService:
#     """Сервис для отправки уведомлений (дайджест, напоминания)"""
    
#     def __init__(self, message_service: MessageService, 
#                  schedule_service: ScheduleService):
#         self.msg = message_service
#         self.schedule = schedule_service
    
#     def send_morning_digest(self):
#         """Утренний дайджест (удаляется через день)"""
#         try:
#             # Очистка старых уведомлений
#             self.msg.cleanup_old_messages()
            
#             today = datetime.now().weekday()
#             events = self.schedule.get_today_events()
#             day_name = config.DAYS[today]
            
#             message = f"🌅 Доброе утро!\nСегодня {day_name}.\n\n"
            
#             if events:
#                 message += "📋 План на день:\n\n"
#                 first_image = events[0].image_url if hasattr(events[0], 'image_url') else None
#                 for event in events:
#                     message += f"  • {event.name}\n  ⏰ {event.time}\n\n"
#             else:
#                 message += "🎉 Событий не запланировано! Можно отдохнуть! 🎉\n\n"
#                 first_image = None
            
#             message += "Также не забываем про лес и прочие активности!\n"
#             "/forest - ⚔️ Создать опрос на сбор команды в Perception Forest \n" 
#             "/arena - ⚔️ Отметиться кто хочет сегодня сходить на арену на базе гильдии."
            
#             self.msg.send_with_auto_delete(
#                 config.CHAT_ID, 
#                 message, 
#                 delete_after_days=1,
#                 pic=first_image,
#                 info="morning_digest")
#             print(f"✅ Утренний дайджест отправлен в {time.strftime('%H:%M:%S')}")
            
#         except Exception as e:
#             print(f"❌ Ошибка в дайджесте: {e}")
    
#     def send_event_reminder(self, event: Event):
#         """Напоминание о событии"""
#         message = (
#             f"🔔 НАПОМИНАНИЕ! 🔔\n\n"
#             f"⚔️ {event.name}\n"
#             f"⏰ Начнется совсем скоро!\n"
#             f"📍 Время сбора: {event.time}\n"
#         )
        
#         if event.description:
#             message += f"📌 {event.description}\n"
        
#         message += "\n👥 Начинаем подготовку!"
        
#         self.msg.send_with_auto_delete(
#             config.CHAT_ID, 
#             message,
#             delete_after_days=1,
#             pic=event.image_url,
#             info=f"reminder - {event.name}"
#         )
#         print(f"✅ Напоминание для {event.name}")
    
#     def send_event_start(self, event: Event):
#         """Уведомление о начале"""
#         message = (
#             f"⚔️ ВНИМАНИЕ! ⚔️\n\n"
#             f"🔸 {event.name}\n"
#             f"⏰ НАЧИНАЕТСЯ СЕЙЧАС! {event.time}\n\n"
#             f"👥 До встречи в чате гильдии!"
#         )
        
#         self.msg.send_with_auto_delete(
#             config.CHAT_ID,
#             message,
#             delete_after_days=1,
#             info=f"start - {event.name}"
#         )
#         print(f"✅ Уведомление о начале для {event.name}")

#     def send_notification(self, event: Event):
#         """Отправка обычного напоминания (для is_notification=True)"""
#         message = (
#             f"🔔 НАПОМИНАНИЕ! 🔔\n\n"
#             f"📌 {event.name}\n"
#             f"{event.description}"
#         )
#         self.msg.send_with_auto_delete(
#             config.CHAT_ID, 
#             message, 
#             delete_after_days=7,
#             info=f"notification - {event.name}"
#         )
#         print(f"✅ Уведомление о начале для {event.name}")