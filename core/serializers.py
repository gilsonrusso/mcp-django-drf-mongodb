from rest_framework import serializers
from .models import Task, Project


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer para Tarefas com todos os campos incluindo relacionamento com projeto.
    """

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["created_at"]


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer para Projetos com contagem de tarefas.
    """

    tasks_count = serializers.SerializerMethodField(
        help_text="Número total de tarefas no projeto"
    )
    completed_tasks_count = serializers.SerializerMethodField(
        help_text="Número de tarefas concluídas no projeto"
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "status",
            "start_date",
            "end_date",
            "created_at",
            "updated_at",
            "tasks_count",
            "completed_tasks_count",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "tasks_count",
            "completed_tasks_count",
        ]

    def get_tasks_count(self, obj):
        return obj.tasks.count()

    def get_completed_tasks_count(self, obj):
        return obj.tasks.filter(completed=True).count()


class ProjectDetailSerializer(ProjectSerializer):
    """
    Serializer detalhado para Projetos incluindo lista de tarefas.
    """

    tasks = TaskSerializer(many=True, read_only=True)

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ["tasks"]
