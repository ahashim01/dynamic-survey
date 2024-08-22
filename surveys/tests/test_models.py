from django.test import TestCase
from surveys.models import Survey, Section, Field, Response, ResponseData


class SurveyModelTest(TestCase):

    def setUp(self):
        self.survey = Survey.objects.create(
            title="Customer Satisfaction Survey", description="A survey to gauge customer satisfaction."
        )

    def test_survey_creation(self):
        """Test that a Survey object is created correctly."""
        self.assertEqual(self.survey.title, "Customer Satisfaction Survey")
        self.assertEqual(str(self.survey), "Customer Satisfaction Survey")
        self.assertEqual(self.survey.description, "A survey to gauge customer satisfaction.")
        self.assertIsInstance(self.survey, Survey)

    def test_section_creation(self):
        """Test that a Section object is created correctly."""
        section = Section.objects.create(survey=self.survey, title="General Feedback", order=1)
        self.assertEqual(section.survey, self.survey)
        self.assertEqual(section.title, "General Feedback")
        self.assertEqual(str(section), "Section 1: General Feedback")
        self.assertEqual(section.order, 1)

    def test_field_creation(self):
        """Test that a Field object is created correctly."""
        section = Section.objects.create(survey=self.survey, title="General Feedback", order=1)
        field = Field.objects.create(
            section=section, label="How satisfied are you with our service?", field_type="radio", order=1
        )
        self.assertEqual(field.section, section)
        self.assertEqual(field.label, "How satisfied are you with our service?")
        self.assertEqual(str(field), "How satisfied are you with our service? (radio)")
        self.assertEqual(field.field_type, "radio")
        self.assertEqual(field.order, 1)


class ResponseModelTest(TestCase):

    def setUp(self):
        self.survey = Survey.objects.create(
            title="Customer Satisfaction Survey", description="A survey to gauge customer satisfaction."
        )
        self.response = Response.objects.create(survey=self.survey, email="test@example.com", completed=True)

    def test_response_creation(self):
        """Test that a Response object is created correctly."""
        self.assertEqual(self.response.survey, self.survey)
        self.assertEqual(self.response.email, "test@example.com")
        self.assertEqual(str(self.response), "Response to Customer Satisfaction Survey by test@example.com")
        self.assertTrue(self.response.completed)

    def test_anonymous_response_creation(self):
        """Test that an AnonymousResponse object is created correctly."""
        response = Response.objects.create(survey=self.survey, completed=True)
        self.assertEqual(response.survey, self.survey)
        self.assertEqual(response.email, None)
        self.assertEqual(str(response), "Response to Customer Satisfaction Survey by Anonymous")
        self.assertTrue(response.completed)

    def test_response_data_creation(self):
        """Test that ResponseData object is created correctly."""
        section = Section.objects.create(survey=self.survey, title="General Feedback", order=1)
        field = Field.objects.create(
            section=section, label="How satisfied are you with our service?", field_type="radio", order=1
        )
        response_data = ResponseData.objects.create(response=self.response, field=field, value="Very Satisfied")
        self.assertEqual(response_data.response, self.response)
        self.assertEqual(str(response_data), "Response to How satisfied are you with our service?: Very Satisfied")
        self.assertEqual(response_data.field, field)
        self.assertEqual(response_data.value, "Very Satisfied")
