from apscheduler.triggers.cron import CronTrigger
from services.notification_service import NotificationService
from models.event import Event
from config import config

def setup_schedule(scheduler, notif_service: NotificationService):
    """Настройка всех задач в планировщике"""
    
    scheduler.remove_all_jobs()
    notification_count = 0
    
    # Утренний дайджест
    scheduler.add_job(
        notif_service.send_morning_digest,
        CronTrigger(hour=config.MORNING_DIGEST_HOUR, 
                   minute=config.MORNING_DIGEST_MINUTE, 
                   timezone=config.TIME_ZONE),
        id='morning_digest'
    )
    print(f"🌅  Утренний дайджест в {config.MORNING_DIGEST_HOUR:02d}:{config.MORNING_DIGEST_MINUTE:02d}\n")

    # Напоминание для каждого события
    for i, event in enumerate(notif_service.schedule.schedule):
        h, m = map(int, event.time.split(':'))
        type = "notification" if event.is_notification else "start"

        if type != "notification": # Не нотис, нужно досрочное напоминание
            # --- Напоминание за offset минут ---
            offset = 11
            reminder_hours = h
            reminder_minutes = m - offset

            # Если минуты ушли в отрицательные, корректируем часы
            if reminder_minutes < 0:
                reminder_hours -= 1
                reminder_minutes += 60
            
            # Проверяем, что время напоминания не ушло в предыдущий день
            # (если событие в 00:05, то напоминание будет в 23:54 предыдущего дня)
            
            reminder_day = event.day
            if reminder_hours < 0:
                # Если напоминание попадает на предыдущий день (например, событие в 00:05)
                # В этом случае нужно добавить задачу на предыдущий день
                reminder_day = (event.day - 1) % 7 
                reminder_hours = 23
                reminder_minutes = 60 + (m - offset)

            scheduler.add_job(
                notif_service.send_notification,
                CronTrigger(day_of_week=reminder_day,
                            hour=reminder_hours,
                            minute=reminder_minutes,
                            timezone=config.TIME_ZONE),
                id=f'reminder_{i}',
                args=[event, "reminder"]
            )
            print(f"🔔 {event.name} (напоминание) в {reminder_hours:02d}:{reminder_minutes:02d} {config.DAYS[event.day]}")
            print(f"⚔️  {event.name} в {h:02d}:{m:02d} {config.DAYS[event.day]}\n")
        else:
            notification_count += 1
            print(f"📌 {event.name} (нотис) в {h:02d}:{m:02d} {config.DAYS[event.day]}\n")

        # --- Уведомление о начале события или создание нотиса ---
        scheduler.add_job(
            notif_service.send_notification,
            CronTrigger(day_of_week=event.day,
                        hour=h,
                        minute=m,
                        timezone=config.TIME_ZONE),
            id=f'{type}_{i}',
            args=[event, type]
        )
    print(f"\n✅ Всего добавлено задач: {len(scheduler.get_jobs())}\n📊 Из них нотисов:{notification_count}\n")
