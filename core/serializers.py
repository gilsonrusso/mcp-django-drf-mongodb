from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Task
        fields = '__all__'
