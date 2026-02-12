# Mapeamento Automático: Django REST -> MCP Tools

Este documento mostra como o `DRFMCPRegistry` mapeou as ViewSets para ferramentas MCP.

| MCP Tool | Verb | Path | Descrição | Parâmetros (Assinatura) |
| :--- | :--- | :--- | :--- | :--- |
| `task_list` | **GET** | `/tasks/` | Action list on task. | `(search: str | None = None, page_size: int | None = None, page: int | None = None, ordering: str | None = None, limit: int | None = None, offset: int | None = None)` |
| `task_create` | **POST** | `/tasks/` | Action create on task. | `(title: str, description: str, completed: str | None = None)` |
| `task_completed` | **GET** | `/tasks/completed/` | Action completed on task. | `(search: str | None = None, page_size: int | None = None, page: int | None = None, ordering: str | None = None, limit: int | None = None, offset: int | None = None)` |
| `task_retrieve` | **GET** | `/tasks/{pk}/` | Action retrieve on task. | `(pk: int)` |
| `task_update` | **PUT** | `/tasks/{pk}/` | Action update on task. | `(pk: int, title: str, description: str, completed: str | None = None)` |
| `task_partial_update` | **PATCH** | `/tasks/{pk}/` | Action partial_update on task. | `(pk: int, title: str | None = None, description: str | None = None, completed: str | None = None)` |
| `task_destroy` | **DELETE** | `/tasks/{pk}/` | Action destroy on task. | `(pk: int)` |
