from django.db import models
from django_mongodb_backend.fields import ObjectIdAutoField

class Task(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
