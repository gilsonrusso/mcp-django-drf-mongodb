from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls), # Omitindo admin por enquanto por causa do suporte Mongo limitado
    path('', include('core.urls')),
]
