from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Events(models.Model):
    event_id = models.AutoField(primary_key=True)
    face_path = models.CharField(max_length=100)
    entered_at = models.DateTimeField()
    exited_at = models.DateTimeField()
    
    def __str__(self):
        return self.event_id
