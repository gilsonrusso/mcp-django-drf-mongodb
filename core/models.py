from django.db import models


class Project(models.Model):
    """
    Projeto que agrupa múltiplas tarefas relacionadas.
    """

    name = models.CharField(max_length=200, help_text="Nome do projeto")
    description = models.TextField(
        blank=True, help_text="Descrição detalhada do projeto"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("planning", "Planejamento"),
            ("active", "Ativo"),
            ("completed", "Concluído"),
            ("archived", "Arquivado"),
        ],
        default="planning",
        help_text="Status atual do projeto",
    )
    start_date = models.DateField(
        null=True, blank=True, help_text="Data de início do projeto"
    )
    end_date = models.DateField(
        null=True, blank=True, help_text="Data de conclusão do projeto"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Task(models.Model):
    """
    Tarefa individual que pode estar associada a um projeto.
    """

    title = models.CharField(max_length=200, help_text="Título da tarefa")
    description = models.TextField(help_text="Descrição detalhada da tarefa")
    completed = models.BooleanField(
        default=False, help_text="Indica se a tarefa foi concluída"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
        null=True,
        blank=True,
        help_text="Projeto ao qual esta tarefa pertence",
    )
    priority = models.CharField(
        max_length=10,
        choices=[
            ("low", "Baixa"),
            ("medium", "Média"),
            ("high", "Alta"),
        ],
        default="medium",
        help_text="Prioridade da tarefa",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
