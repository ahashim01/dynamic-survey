from django.test import TestCase
from surveys.models import Survey, Section, Field, Response, ResponseData
from surveys.serializers import SectionSerializer, SurveySerializer, ResponseSerializer, ResponseDataSerializer
from rest_framework.exceptions import ValidationError


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


class SectionSerializerConditionalLogicTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.survey = Survey.objects.create(
            title="Customer Satisfaction Survey", description="A survey to gauge customer satisfaction."
        )
        cls.section = Section.objects.create(survey=cls.survey, title="General Feedback", order=1)
        cls.field1 = Field.objects.create(
            section=cls.section, label="Are you satisfied?", field_type="radio", required=True, order=1
        )
        cls.field2 = Field.objects.create(
            section=cls.section,
            label="Why are you satisfied?",
            field_type="text",
            required=False,
            order=2,
            conditional_logic={"depends_on_field": cls.field1.id, "operator": "==", "value": "yes"},
        )
        cls.response = Response.objects.create(survey=cls.survey, email="test@example.com", completed=False)
        ResponseData.objects.create(response=cls.response, field=cls.field1, value="yes")

    def test_conditional_logic_in_survey_serializer(self):
        """Test that the SurveySerializer respects conditional logic when serializing."""
        context = {"user_responses": {self.field1.id: "yes"}}
        serializer = SurveySerializer(self.survey, context=context)

        # Assertions
        data = serializer.data
        self.assertEqual(len(data["sections"][0]["fields"]), 2)  # Both fields should be included

        # Test with a different response that should hide Field 2
        context = {"user_responses": {self.field1.id: "no"}}
        serializer = SurveySerializer(self.survey, context=context)
        data = serializer.data
        self.assertEqual(len(data["sections"][0]["fields"]), 1)  # Only Field 1 should be included

    def test_unsupported_operator_raises_valueerror(self):
        """Test that unsupported operators raise a ValueError."""
        Field.objects.create(
            section=self.section,
            label="Field 3",
            field_type="text",
            order=3,
            conditional_logic={"depends_on_field": self.field2.id, "operator": "unsupported", "value": "yes"},
        )

        context = {"user_responses": {self.field2.id: "yes"}}
        with self.assertRaises(ValueError):
            serializer = SurveySerializer(self.survey, context=context)
            _ = serializer.data  # Trigger the evaluation by accessing the data


class SectionSerializerDependencyTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.survey = Survey.objects.create(title="Dependency Test Survey", description="Testing dependencies.")
        cls.section = Section.objects.create(survey=cls.survey, title="Dependency Section", order=1)
        cls.field1 = Field.objects.create(section=cls.section, label="Field 1", field_type="text", order=1)
        cls.field2 = Field.objects.create(
            section=cls.section,
            label="Dependent Field",
            field_type="text",
            order=2,
            dependencies={"depends_on_field": cls.field1.id, "operator": "in", "values": ["yes", "maybe"]},
        )

    def test_evaluate_dependencies_in(self):
        """Test that _evaluate_dependencies includes field when dependency is met."""
        context = {"user_responses": {self.field1.id: "yes"}}
        serializer = SectionSerializer(instance=self.section, context=context)

        # Since the dependency is met, field2 should be included
        fields = serializer.data["fields"]
        self.assertEqual(len(fields), 2)  # Both fields should be present

    def test_evaluate_dependencies_not_met(self):
        """Test that _evaluate_dependencies excludes field when dependency is not met."""
        context = {"user_responses": {self.field1.id: "no"}}
        serializer = SectionSerializer(instance=self.section, context=context)

        # Since the dependency is not met, field2 should be excluded
        fields = serializer.data["fields"]
        self.assertEqual(len(fields), 1)  # Only field1 should be present

    def test_evaluate_dependencies_not_in(self):
        """Test that _evaluate_dependencies includes field when dependency with 'not_in' is met."""
        self.field2.dependencies = {"depends_on_field": self.field1.id, "operator": "not_in", "values": ["no"]}
        self.field2.save()

        context = {"user_responses": {self.field1.id: "yes"}}
        serializer = SectionSerializer(instance=self.section, context=context)

        # Since the 'not_in' dependency is met, field2 should be included
        fields = serializer.data["fields"]
        self.assertEqual(len(fields), 2)  # Both fields should be present

    def test_evaluate_dependencies_unsupported_operator_raises_valueerror(self):
        """Test that _evaluate_dependencies raises a ValueError for unsupported operators."""
        self.field2.dependencies = {"depends_on_field": self.field1.id, "operator": "unsupported", "values": ["no"]}
        self.field2.save()

        context = {"user_responses": {self.field1.id: "yes"}}
        with self.assertRaises(ValueError):
            serializer = SectionSerializer(instance=self.section, context=context)
            _ = serializer.data


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
        # Create a Section instance to associate with the Field
        self.survey = Survey.objects.create(title="Response Data Test Survey", description="Testing dependencies.")
        self.section = Section.objects.create(survey=self.survey, title="Response Data Section", order=1)

        # Create a Field instance with choices
        self.field_with_choices = Field.objects.create(
            section=self.section,
            label="Choice Field",
            field_type="dropdown",
            required=True,
            order=1,
            choices=["option1", "option2", "option3"],
            conditional_logic=None,
            dependencies=None,
        )

        # Create a Field instance without choices but with conditional logic and dependencies
        self.field_with_logic_and_dependencies = Field.objects.create(
            section=self.section,
            label="Conditional Field",
            field_type="text",
            required=True,
            order=2,
            choices=None,
            conditional_logic={"show_if": {"field_id": 1, "value": "option1"}},
            dependencies={"dependent_on": 1, "value_required": "option2"},
        )

        # Create a Response instance
        self.response = Response.objects.create(survey=self.survey)

    def test_validate_invalid_choice(self):
        """Test validation fails when value is not in predefined choices."""
        data = {"response": self.response.id, "field": self.field_with_choices.id, "value": "invalid_option"}

        serializer = ResponseDataSerializer(data=data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)

        self.assertIn("Value 'invalid_option' is not a valid choice.", str(context.exception))

    def test_validate_conditional_logic_not_satisfied(self):
        """Test validation fails when conditional logic is not satisfied."""
        # Override _check_conditional_logic to return False
        ResponseDataSerializer._check_conditional_logic = lambda self, field, data: False

        data = {"response": self.response.id, "field": self.field_with_logic_and_dependencies.id, "value": "some_value"}

        serializer = ResponseDataSerializer(data=data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)

        self.assertIn("Conditional logic not satisfied.", str(context.exception))

    def test_validate_dependencies_not_met(self):
        """Test validation fails when dependencies are not met."""
        # Override _check_dependencies to return False
        ResponseDataSerializer._check_conditional_logic = lambda self, field, data: True
        ResponseDataSerializer._check_dependencies = lambda self, field, data: False

        data = {"response": self.response.id, "field": self.field_with_logic_and_dependencies.id, "value": "some_value"}

        serializer = ResponseDataSerializer(data=data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)

        self.assertIn("Dependency conditions not met.", str(context.exception))

    def test_validate_successful(self):
        """Test successful validation when all conditions are met."""
        data = {"response": self.response.id, "field": self.field_with_choices.id, "value": "option1"}

        serializer = ResponseDataSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["value"], "option1")

    def test_validate_with_empty_field(self):
        """Test validation when the value field is empty."""
        data = {"response": self.response.id, "field": self.field_with_choices.id, "value": ""}

        serializer = ResponseDataSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("This field may not be blank.", serializer.errors["value"])
