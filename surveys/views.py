from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import ResponseData, Survey, Response
from .serializers import ResponseDataSerializer, SurveySerializer, ResponseSerializer


class SurveyListCreateView(generics.ListCreateAPIView):
    queryset = Survey.objects.all().prefetch_related("sections__fields")
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SurveyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Survey.objects.all().prefetch_related("sections__fields")
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()

        # Retrieve the user's previous responses for the current survey
        survey = self.get_object()
        user = self.request.user

        # Assuming responses are tracked by user (or anonymous email if user is not logged in)
        user_responses = {}
        if user.is_authenticated:
            responses = ResponseData.objects.filter(response__survey=survey, response__email=user.email)
            user_responses = {resp.field.id: resp.value for resp in responses}

        context["user_responses"] = user_responses
        return context


class ResponseListCreateView(generics.ListCreateAPIView):
    queryset = Response.objects.all().select_related("survey")
    serializer_class = ResponseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ResponseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Response.objects.all().select_related("survey")
    serializer_class = ResponseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ResponseDataListCreateView(generics.ListCreateAPIView):
    queryset = ResponseData.objects.all().select_related("response", "field")
    serializer_class = ResponseDataSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ResponseDataDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ResponseData.objects.all().select_related("response", "field")
    serializer_class = ResponseDataSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
