from django.urls import path
from .views import (
    ResponseDataDetailView,
    ResponseDataListCreateView,
    SurveyListCreateView,
    SurveyDetailView,
    ResponseListCreateView,
    ResponseDetailView,
)

urlpatterns = [
    # Survey endpoints
    path("surveys/", SurveyListCreateView.as_view(), name="survey-list-create"),
    path("surveys/<int:pk>/", SurveyDetailView.as_view(), name="survey-detail"),
    # Response endpoints
    path("responses/", ResponseListCreateView.as_view(), name="response-list-create"),
    path("responses/<int:pk>/", ResponseDetailView.as_view(), name="response-detail"),
    # ResponseData endpoints
    path("response-data/", ResponseDataListCreateView.as_view(), name="response-data-list-create"),
    path("response-data/<int:pk>/", ResponseDataDetailView.as_view(), name="response-data-detail"),
]
