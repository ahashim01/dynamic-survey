from django.test import TestCase
from surveys.models import Survey, Section, Field, Response, ResponseData
from surveys.serializers import SurveySerializer, ResponseSerializer, ResponseDataSerializer


class SurveySerializerTest(TestCase):

    def setUp(self):
        # Initial data setup for testing
        self.survey_data = {
            "title": "Customer Satisfaction Survey",
            "description": "A survey to gauge customer satisfaction.",
            "sections": [
                {
                    "title": "General Feedback",
                    "order": 1,
                    "fields": [
                        {
                            "label": "How satisfied are you with our service?",
                            "field_type": "radio",
                            "required": True,
                            "order": 1,
                        }
                    ],
                },
                {
                    "title": "Product Feedback",
                    "order": 2,
                    "fields": [
                        {
                            "label": "How would you rate the quality of the product?",
                            "field_type": "radio",
                            "required": True,
                            "order": 1,
                        }
                    ],
                },
            ],
        }

        self.survey = Survey.objects.create(title="Old Title", description="Old Description")
        self.section = Section.objects.create(survey=self.survey, title="Old Section", order=1)
        self.field = Field.objects.create(
            section=self.section,
            label="Old Field",
            field_type="text",
            required=False,
            order=1,
        )

    def test_survey_serializer_create(self):
        """Test that the SurveySerializer's create method correctly handles nested data."""
        serializer = SurveySerializer(data=self.survey_data)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)

        survey = serializer.save()

        # Check that the survey was created
        self.assertEqual(Survey.objects.count(), 2)  # Old survey and new survey
        self.assertEqual(survey.title, self.survey_data["title"])
        self.assertEqual(survey.description, self.survey_data["description"])

        # Check that the sections were created and linked to the survey
        self.assertEqual(Section.objects.filter(survey=survey).count(), len(self.survey_data["sections"]))
        for section_data in self.survey_data["sections"]:
            section = Section.objects.get(title=section_data["title"])
            self.assertEqual(section.survey, survey)
            self.assertEqual(section.order, section_data["order"])

            # Check that the fields were created and linked to the sections
            self.assertEqual(Field.objects.filter(section=section).count(), len(section_data["fields"]))
            for field_data in section_data["fields"]:
                field = Field.objects.get(label=field_data["label"])
                self.assertEqual(field.section, section)
                self.assertEqual(field.field_type, field_data["field_type"])
                self.assertEqual(field.required, field_data["required"])
                self.assertEqual(field.order, field_data["order"])

    def test_survey_serializer_invalid(self):
        """Test that SurveySerializer is invalid with missing title."""
        self.survey_data.pop("title")
        serializer = SurveySerializer(data=self.survey_data)
        self.assertFalse(serializer.is_valid())

    def test_survey_serializer_update(self):
        """Test the SurveySerializer's update method for full updates (PUT)."""
        update_data = {
            "title": "Updated Survey",
            "description": "Updated Description",
            "sections": [
                {
                    "title": "Updated Section",
                    "order": 1,
                    "fields": [
                        {
                            "label": "Updated Field",
                            "field_type": "text",
                            "required": True,
                            "order": 1,
                        }
                    ],
                }
            ],
        }

        serializer = SurveySerializer(self.survey, data=update_data)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)

        survey = serializer.save()

        # Check that the survey was updated
        self.assertEqual(survey.title, update_data["title"])
        self.assertEqual(survey.description, update_data["description"])

        # Check that the sections were updated
        self.assertEqual(Section.objects.count(), 1)
        section = Section.objects.get(title="Updated Section")
        self.assertEqual(section.survey, survey)
        self.assertEqual(section.order, 1)

        # Check that the fields were updated
        self.assertEqual(Field.objects.count(), 1)
        field = Field.objects.get(label="Updated Field")
        self.assertEqual(field.section, section)
        self.assertEqual(field.field_type, "text")
        self.assertTrue(field.required)
        self.assertEqual(field.order, 1)

    def test_survey_serializer_partial_update(self):
        """Test the SurveySerializer's update method for partial updates (PATCH)."""
        partial_update_data = {
            "title": "Partially Updated Survey",
        }

        serializer = SurveySerializer(self.survey, data=partial_update_data, partial=True)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)

        survey = serializer.save()

        # Check that only the title was updated
        self.assertEqual(survey.title, partial_update_data["title"])
        self.assertEqual(survey.description, "Old Description")  # Should remain unchanged

        # Check that sections and fields remain unchanged
        self.assertEqual(Section.objects.count(), 1)
        section = Section.objects.get(title="Old Section")
        self.assertEqual(section.survey, survey)
        self.assertEqual(section.order, 1)

        self.assertEqual(Field.objects.count(), 1)
        field = Field.objects.get(label="Old Field")
        self.assertEqual(field.section, section)
        self.assertEqual(field.field_type, "text")
        self.assertFalse(field.required)
        self.assertEqual(field.order, 1)


class ResponseSerializerTest(TestCase):

    def setUp(self):
        self.survey = Survey.objects.create(
            title="Customer Satisfaction Survey", description="A survey to gauge customer satisfaction."
        )
        self.response_data = {"survey": self.survey.pk, "email": "test@example.com", "completed": True}

    def test_response_serializer_create(self):
        """Test that the ResponseSerializer's create method correctly handles data."""
        serializer = ResponseSerializer(data=self.response_data)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)

        response: Response = serializer.save()

        # Check that the response was created
        self.assertEqual(Response.objects.count(), 1)
        self.assertEqual(response.survey.pk, self.response_data["survey"])
        self.assertEqual(response.email, self.response_data["email"])
        self.assertEqual(response.completed, self.response_data["completed"])

    def test_response_serializer_invalid(self):
        """Test that ResponseSerializer is invalid with missing survey."""
        self.response_data.pop("survey")
        serializer = ResponseSerializer(data=self.response_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("survey", serializer.errors)


class ResponseDataSerializerTest(TestCase):

    def setUp(self):
        # Set up a survey with a section and a field
        self.survey = Survey.objects.create(
            title="Customer Satisfaction Survey", description="A survey to gauge customer satisfaction."
        )
        self.section = Section.objects.create(survey=self.survey, title="General Feedback", order=1)
        self.field = Field.objects.create(
            section=self.section,
            label="How satisfied are you with our service?",
            field_type="radio",
            required=True,
            order=1,
        )
        self.response = Response.objects.create(survey=self.survey, email="test@example.com", completed=True)
        self.response_data = {"response": self.response.id, "field": self.field.id, "value": "Very Satisfied"}

    def test_response_data_serializer_create(self):
        """Test that the ResponseDataSerializer's create method correctly handles data."""
        serializer = ResponseDataSerializer(data=self.response_data)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)

        response_data: ResponseData = serializer.save()

        # Check that the response data was created
        self.assertEqual(ResponseData.objects.count(), 1)
        self.assertEqual(response_data.response, self.response)
        self.assertEqual(response_data.field, self.field)
        self.assertEqual(response_data.value, "Very Satisfied")

    def test_response_data_serializer_invalid(self):
        """Test that the ResponseDataSerializer raises validation errors for missing data."""
        invalid_data = self.response_data.copy()
        invalid_data.pop("field")  # Remove the field to test validation

        serializer = ResponseDataSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("field", serializer.errors)
