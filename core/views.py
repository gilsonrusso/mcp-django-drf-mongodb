from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Task, Project
from .serializers import TaskSerializer, ProjectSerializer, ProjectDetailSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Tarefas.

    Permite criar, listar, atualizar e deletar tarefas.
    Suporta filtros por projeto e status de conclusão.
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "title", "priority"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="completed",
                type=bool,
                description="Filtrar por tarefas concluídas (true) ou pendentes (false)",
            ),
            OpenApiParameter(
                name="project",
                type=int,
                description="Filtrar tarefas por ID do projeto",
            ),
            OpenApiParameter(
                name="priority",
                type=str,
                description="Filtrar por prioridade (low, medium, high)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Task.objects.all()

        # Filtro por conclusão
        completed = self.request.query_params.get("completed")
        if completed is not None:
            is_completed = completed.lower() == "true"
            queryset = queryset.filter(completed=is_completed)

        # Filtro por projeto
        project = self.request.query_params.get("project")
        if project:
            queryset = queryset.filter(project_id=project)

        # Filtro por prioridade
        priority = self.request.query_params.get("priority")
        if priority:
            queryset = queryset.filter(priority=priority)

        return queryset

    @extend_schema(
        description="Lista apenas as tarefas concluídas",
        responses={200: TaskSerializer(many=True)},
    )
    @action(detail=False, methods=["get"])
    def completed(self, request):
        """Retorna apenas tarefas concluídas."""
        completed_tasks = Task.objects.filter(completed=True)
        serializer = self.get_serializer(completed_tasks, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Marca uma tarefa como concluída", responses={200: TaskSerializer}
    )
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Marca uma tarefa específica como concluída."""
        task = self.get_object()
        task.completed = True
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Projetos.

    Permite criar, listar, atualizar e deletar projetos.
    Inclui ações customizadas para arquivar, ativar e obter estatísticas.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "name", "status"]

    def get_serializer_class(self):
        """Usa serializer detalhado para retrieve."""
        if self.action == "retrieve":
            return ProjectDetailSerializer
        return ProjectSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="status",
                type=str,
                description="Filtrar por status (planning, active, completed, archived)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Project.objects.all()

        # Filtro por status
        project_status = self.request.query_params.get("status")
        if project_status:
            queryset = queryset.filter(status=project_status)

        return queryset

    @extend_schema(
        description="Arquiva um projeto (muda status para 'archived')",
        responses={200: ProjectSerializer},
    )
    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        """Arquiva um projeto específico."""
        project = self.get_object()
        project.status = "archived"
        project.save()
        serializer = self.get_serializer(project)
        return Response(serializer.data)

    @extend_schema(
        description="Ativa um projeto (muda status para 'active')",
        responses={200: ProjectSerializer},
    )
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Ativa um projeto específico."""
        project = self.get_object()
        project.status = "active"
        project.save()
        serializer = self.get_serializer(project)
        return Response(serializer.data)

    @extend_schema(
        description="Retorna estatísticas detalhadas do projeto",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "total_tasks": {"type": "integer"},
                    "completed_tasks": {"type": "integer"},
                    "pending_tasks": {"type": "integer"},
                    "completion_percentage": {"type": "number"},
                    "tasks_by_priority": {"type": "object"},
                },
            }
        },
    )
    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None):
        """Retorna estatísticas detalhadas sobre as tarefas do projeto."""
        project = self.get_object()
        tasks = project.tasks.all()

        total = tasks.count()
        completed = tasks.filter(completed=True).count()
        pending = total - completed

        stats = {
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "completion_percentage": (completed / total * 100) if total > 0 else 0,
            "tasks_by_priority": {
                "low": tasks.filter(priority="low").count(),
                "medium": tasks.filter(priority="medium").count(),
                "high": tasks.filter(priority="high").count(),
            },
        }

        return Response(stats)
