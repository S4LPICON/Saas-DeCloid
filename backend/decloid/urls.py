"""
URL configuration for decloid project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/auth/", include("applications.api.auth.urls")),
    path("api/v1/nodes/", include("applications.api.nodes.urls")),
    
    path("api/v1/artifacts/", include("applications.api.artifacts.urls")),
    path("api/v1/servers/", include("applications.api.servers.urls")),
    path("api/v1/orchestrator/servers/", include("applications.api.orchestrator.urls")),
    path("api/v1/orchestrator/nodes/", include("applications.nodes.urls")),


]
