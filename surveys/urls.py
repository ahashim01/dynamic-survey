from django.urls import path
from .views import SurveyListCreateView, SurveyDetailView, ResponseListCreateView, ResponseDetailView

urlpatterns = [
    # Survey endpoints
    path("surveys/", SurveyListCreateView.as_view(), name="survey-list-create"),
    path("surveys/<int:pk>/", SurveyDetailView.as_view(), name="survey-detail"),  # Use <int:pk> for integer primary key
    # Response endpoints
    path("responses/", ResponseListCreateView.as_view(), name="response-list-create"),
    path("responses/<int:pk>/", ResponseDetailView.as_view(), name="response-detail"),
]
