from apscheduler.schedulers.background import BackgroundScheduler
from app import my_interval_job

scheduler = BackgroundScheduler()
scheduler.add_job(my_interval_job, 'cron', hour='15-17', minute='01-59')
scheduler.start()
