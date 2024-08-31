from celery import Celery

from helpers.send_email import send_email

app = Celery('tasks', broker='redis://127.0.0.1:6379')

@app.task
def send_task_assignment_notification(email):
    send_email("Task Assignment", "Task is assigned to you", [email])

@app.task
def send_task_update_notification(email):
    send_email("Task is Updated", "Task is updated", [email])