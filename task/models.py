from django.db import models
from django.contrib.auth.models import User # new

class Task(models.Model):
  title = models.CharField(max_length=255)
  description = models.CharField(max_length=500)

  class TaskStatus(models.TextChoices):
        PENDING = 'PG', ('Pending')
        IN_PROGRESS = 'IG', ('In Progress')
        COMPLETED = 'CD', ('Completed')

  status = models.CharField(
        max_length=2,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING,
    )
  
  assignee = models.ForeignKey(User, on_delete=models.CASCADE)
  due_date = models.DateField()