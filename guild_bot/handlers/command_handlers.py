import telebot
from datetime import datetime
from services.message_service import MessageService
from services.schedule_service import ScheduleService
from services.notification_service import NotificationService
from scheduler_config import setup_schedule
from models.event import Event
from config import config

class CommandHandlers:
    """Все обработчики команд"""
    
    def __init__(self, bot: telebot.TeleBot, msg_service: MessageService,
                 schedule_service: ScheduleService, notif_service: NotificationService,
                 scheduler):
        self.bot = bot
        self.msg = msg_service
        self.schedule = schedule_service
        self.notif = notif_service
        self.scheduler = scheduler
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрация всех команд"""
        self.bot.message_handler(commands=['start'])(self.cmd_start)
        self.bot.message_handler(commands=['today'])(self.cmd_today)
        self.bot.message_handler(commands=['week'])(self.cmd_week)
        self.bot.message_handler(commands=['next'])(self.cmd_next)
        self.bot.message_handler(commands=['forest'])(self.cmd_forest)
        self.bot.message_handler(commands=['arena'])(self.cmd_arena)
        self.bot.message_handler(commands=['start_bot'])(self.cmd_start_bot)
        self.bot.message_handler(commands=['stop_bot'])(self.cmd_stop_bot)
        self.bot.message_handler(commands=['status'])(self.cmd_status)
        self.bot.message_handler(commands=['schedule'])(self.cmd_schedule)
        self.bot.message_handler(commands=['getID'])(self.cmd_get_id)
        self.bot.message_handler(commands=['test'])(self.cmd_test)
        self.bot.message_handler(commands=['reload'])(self.cmd_reload)
    
    def cmd_start(self, message):
        text = (
            "👋 Привет! Я бот для расписания гильдии.\n\n"
            "📋 Доступные команды:\n"
            "/today - Расписание на сегодня\n"
            "/week - Расписание на всю неделю\n"
            "/next - Ближайшее событие\n"
            "/forest - Подбор команды в лес\n"
            "/arena - Выбор времени для арены\n"
            "/start_bot - Запустить автоматические рассылки\n"
            "/stop_bot - Остановить автоматические рассылки\n"
            "/status - Проверить статус бота"
        )
        self.msg.send(message.chat.id, text)
    
    def cmd_today(self, message):
        events = self.schedule.get_today_events()
        day_name = config.DAYS[datetime.now().weekday()]
        
        if events:
            text = f"📅 Расписание на сегодня ({day_name}):\n\n"
            for e in events:
                text += f"  📌 {e.name}\n  ⏰ {e.time}\n"
        else:
            text = f"📅 На {day_name} событий нет 🎉"
        
        self.msg.send(message.chat.id, text)
    
    def cmd_week(self, message):
        days = self.schedule.get_all_by_day()
        text = "📅 Расписание на неделю:\n\n"
        
        for day_name in config.DAYS:
            if day_name in days:
                text += f"🔹 {day_name}:\n"
                for e in days[day_name]:
                    text += f"  • {e.name} - {e.time}\n"
                text += "\n"
            else:
                text += f"🔹 {day_name}:\n  🎉 Выходной\n\n"
        
        self.msg.send(message.chat.id, text)
    
    def cmd_next(self, message):
        event = self.schedule.get_next_event()
        if event:
            # Расчет времени до события
            now = datetime.now()
            current_minutes = (now.hour + config.TIME_SHIFT) * 60 + now.minute
            current_day = now.weekday()
            
            days_ahead = event.day - current_day
            h, m = map(int, event.time.split(':'))
            event_minutes = h * 60 + m
            
            if days_ahead < 0 or (days_ahead == 0 and event_minutes <= current_minutes):
                days_ahead += 7
            
            total_minutes = days_ahead * 24 * 60 + event_minutes - current_minutes
            hours = total_minutes // 60
            minutes = total_minutes % 60
            
            text = (
                f"⏳ Ближайшее событие:\n\n"
                f"  📌 {event.name}\n"
                f"  ⏰ Через {hours} ч {minutes} мин\n"
                f"  📅 {config.DAYS[event.day]} в {event.time}"
            )
        else:
            text = "Не удалось найти ближайшее событие"
        
        self.msg.send(message.chat.id, text)
    
    def cmd_forest(self, message):
        # Отправляем картинку
        self.msg.send(
            message.chat.id,
            "Объявляется набор команды для похода в лес!",
            pic=config.IMAGE_PATHS['join_forest']
        )
        
        # Отправляем опрос
        options = [
            "19:00-19:30",
            "20:10-20:30 (После ги пати)",
            "20:30-21:00",
            "21:00-21:30",
            "Я за любое время",
            "Я гусь 🪿🪿🪿"
        ]
        self.msg.send(
            message.chat.id,
            "Во сколько удобно пойти в лес?",
            options=options
        )
    
    def cmd_arena(self, message):
        # Отправляем картинку
        self.msg.send(
            message.chat.id,
            "Кто хочет на арену?",
            pic=config.IMAGE_PATHS['arena']
        )
        
        # Отправляем опрос
        options = [
            "Я могу хоть сейчас",
            "Я могу после ги пати",
            "+1",
            "Я гусь 🪿🪿🪿"
        ]
        self.msg.send(
            message.chat.id,
            "Отмечаемся когда",
            options=options
        )
    
    def cmd_start_bot(self, message):
        setup_schedule(self.scheduler, self.notif)
        if not self.scheduler.running:
            self.scheduler.start()
        self.msg.send(message.chat.id, "✅ Бот запущен!")
    
    def cmd_stop_bot(self, message):
        self.scheduler.remove_all_jobs()
        self.msg.send(message.chat.id, "🛑 Автоматические рассылки остановлены")
    
    def cmd_status(self, message):
        jobs = self.scheduler.get_jobs()
        if jobs:
            status = f"✅ Бот активен\n📋 Запланировано задач: {len(jobs)}"
        else:
            status = "⏸ Бот не активен. Используй /start_bot для запуска"
        self.msg.send(message.chat.id, status)
    
    def cmd_schedule(self, message):
        jobs = self.scheduler.get_jobs()
        if not jobs:
            self.msg.send(message.chat.id, "Нет запланированных задач")
            return
        
        text = "📋 Расписание задач:\n\n"

        for job in jobs:
        # Определяем иконку по типу задачи
            if 'reminder' in job.id:
                icon = "🔔"
            elif 'start' in job.id:
                icon = "⚔️"
            elif 'morning' in job.id:
                icon = "🌅"
            else:
                icon = "📌"
        
            text += f"   {icon} {job.id}"

            if job.args and len(job.args) > 0:
                event = job.args[0]
                if hasattr(event, 'name'):
                    text += f" - {event.name}\n"
            else: text +="\n"
            
            if job.next_run_time:
                text += f"   ⏰ {job.next_run_time.strftime('%Y-%m-%d %H:%M')}\n\n"
        
        self.msg.send(message.chat.id, text)
    
    def cmd_get_id(self, message):
        text = f"🆔 ID чата: {message.chat.id}\n"
        if message.message_thread_id:
            text += f"📌 ID темы: {message.message_thread_id}\n"
        text += f"👤 Отправитель: {message.from_user.id}"
        
        self.bot.send_message(message.chat.id, text)
    
    def cmd_reload(self, message):
        """Перезагрузка расписания из CSV без перезапуска бота"""
        try:
            self.schedule.reload_schedule()
            # Перезапускаем планировщик с новым расписанием
            from scheduler_config import setup_schedule
            setup_schedule(self.scheduler, self.notif)
            self.msg.send(message.chat.id, "✅ Расписание перезагружено из CSV и задачи обновлены!")
        except Exception as e:
            self.msg.send(message.chat.id, f"❌ Ошибка при перезагрузке: {e}")
    
    def cmd_test(self, message):
        self.notif.send_morning_digest()
        # data = {"name": "тестовое событие", 
        #         "day": 1, 
        #         "time": "12:13",
        #         "description": "тестовое описание, не обращайте внимание"}
        # event = Event.from_dict(data)
        # self.notif.send_notification(event, "start")
