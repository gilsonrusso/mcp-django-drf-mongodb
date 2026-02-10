from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        queryset = Task.objects.all()
        completed = self.request.query_params.get('completed')
        
        if completed is not None:
            # Converte string (ex: 'true') para booleano
            is_completed = completed.lower() == 'true'
            queryset = queryset.filter(completed=is_completed)
            
        return queryset

    # Criando uma "outra rota": /api/tasks/completed/
    @action(detail=False, methods=['get'])
    def completed(self, request):
        completed_tasks = Task.objects.filter(completed=True)
        serializer = self.get_serializer(completed_tasks, many=True)
        return Response(serializer.data)
