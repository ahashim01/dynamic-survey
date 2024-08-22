from django.contrib import admin
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("surveys.urls")),
] + debug_toolbar_urls()  # Debug toolbar URLs will only be added if DEBUG is True
