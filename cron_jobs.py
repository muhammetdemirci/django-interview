
from task.models import Task
from datetime import date, timedelta
from helpers.send_email import send_email

def due_date_reminder():
    startdate = date.today()
    enddate = startdate + timedelta(days=1)
    
    tasks = Task.objects.filter(due_date__range=[startdate, enddate])

    for task in tasks:
        send_email("Task Due Date", "the due date of task is near", [task.user.email])