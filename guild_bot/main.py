import telebot
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from config import config
from services.message_service import MessageService
from services.schedule_service import ScheduleService
from services.notification_service import NotificationService
from services.storage_service import CSVEventStorage
from handlers.command_handlers import CommandHandlers
from scheduler_config import setup_schedule

def main():
    # Создаем бота и планировщик
    bot = telebot.TeleBot(config.BOT_TOKEN)
    scheduler = BackgroundScheduler(timezone=config.TIME_ZONE)
    
    # Инициализируем сервисы
    msg_service = MessageService(bot) # Отправка сообщений, картинок, опросов
    schedule_service = ScheduleService() # Список ивентов
    notif_service = NotificationService(msg_service, schedule_service)
    
    # Настраиваем планировщик
    setup_schedule(scheduler, notif_service)
    scheduler.start()
    
    # Регистрируем обработчики команд
    CommandHandlers(bot, msg_service, schedule_service, notif_service, scheduler)
    
    # Запускаем бота
    print("🤖 Бот запущен...")
    print(f"📅 Сегодня: {config.DAYS[datetime.now().weekday()]}")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
        scheduler.shutdown()

if __name__ == "__main__":
    main()