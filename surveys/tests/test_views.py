from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from surveys.models import Survey, Response
from django.contrib.auth.models import User


class SurveyViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="testpassword")
        cls.updated_description = "Updated description"

    def setUp(self):
        # Authenticate the client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.survey = Survey.objects.create(
            title="Customer Satisfaction Survey", description="A survey to gauge customer satisfaction."
        )
        self.survey_obj_result = {
            "id": self.survey.id,
            "title": "Customer Satisfaction Survey",
            "description": "A survey to gauge customer satisfaction.",
            "sections": [],
            "created_at": self.survey.created_at.isoformat().replace("+00:00", "Z"),
            "updated_at": self.survey.updated_at.isoformat().replace("+00:00", "Z"),
        }
        self.survey_url = reverse("survey-detail", kwargs={"pk": self.survey.id})

    def test_list_surveys(self):
        """Test that we can list surveys."""
        url = reverse("survey-list-create")
        expected_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [self.survey_obj_result],
        }
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response)

    def test_retrieve_survey(self):
        """Test that we can retrieve a survey."""
        response = self.client.get(self.survey_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), self.survey_obj_result)

    def test_create_survey(self):
        """Test that we can create a survey."""
        url = reverse("survey-list-create")
        data = {"title": "New Survey", "description": "A new survey for testing.", "sections": []}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_survey(self):
        """Test that we can update a survey."""
        data = {"title": "Updated Survey", "description": self.updated_description, "sections": []}
        response = self.client.put(self.survey_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.survey.refresh_from_db()
        self.assertEqual(self.survey.title, "Updated Survey")
        self.assertEqual(self.survey.description, self.updated_description)

    def test_patch_survey(self):
        """Test that we can update partially a survey."""
        data = {"description": "Updated description."}
        response = self.client.patch(self.survey_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.survey.refresh_from_db()
        self.assertEqual(self.survey.description, "Updated description.")
        self.assertEqual(self.survey.title, "Customer Satisfaction Survey")

    def test_delete_survey(self):
        """Test that we can delete a survey."""
        response = self.client.delete(self.survey_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ResponseViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="testpassword")

    def setUp(self):
        # Authenticate the client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.survey = Survey.objects.create(
            title="Customer Satisfaction Survey", description="A survey to gauge customer satisfaction."
        )
        self.response = Response.objects.create(survey=self.survey, email="test@example.com", completed=True)
        self.response_obj_result = {
            "id": self.response.id,
            "survey": self.response.survey.id,
            "email": self.response.email,
            "completed": self.response.completed,
            "created_at": self.response.created_at.isoformat().replace("+00:00", "Z"),
            "updated_at": self.response.updated_at.isoformat().replace("+00:00", "Z"),
        }
        self.response_url = reverse("response-detail", kwargs={"pk": self.response.id})

    def test_list_responses(self):
        """Test that we can list responses."""
        url = reverse("response-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_response = {"count": 1, "next": None, "previous": None, "results": [self.response_obj_result]}
        self.assertEqual(response.json(), expected_response)

    def test_retrieve_response(self):
        """Test that we can retrieve a response."""
        response = self.client.get(self.response_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.json(), self.response_obj_result)

    def test_create_response(self):
        """Test that we can create a response."""
        url = reverse("response-list-create")
        data = {"survey": self.survey.id, "email": "new@example.com", "completed": False}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Response.objects.count(), 2)
        self.assertEqual(Response.objects.last().email, "new@example.com")

    def test_update_response(self):
        """Test that we can update a response."""
        data = {"survey": self.survey.id, "email": "updated@example.com", "completed": True}
        response = self.client.put(self.response_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_response(self):
        """Test that we can delete a response."""
        response = self.client.delete(self.response_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
