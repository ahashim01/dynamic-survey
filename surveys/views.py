from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Survey, Response
from .serializers import SurveySerializer, ResponseSerializer


class SurveyListCreateView(generics.ListCreateAPIView):
    queryset = Survey.objects.all().prefetch_related("sections__fields")
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SurveyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Survey.objects.all().prefetch_related("sections__fields")
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ResponseListCreateView(generics.ListCreateAPIView):
    queryset = Response.objects.all().select_related("survey")
    serializer_class = ResponseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ResponseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Response.objects.all().select_related("survey")
    serializer_class = ResponseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
