from rest_framework import serializers
from .models import Survey, Section, Field, Response, ResponseData


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = [
            "id",
            "label",
            "field_type",
            "required",
            "order",
            "conditional_logic",
            "dependencies",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SectionSerializer(serializers.ModelSerializer):
    fields = FieldSerializer(many=True)

    class Meta:
        model = Section
        fields = ["id", "title", "order", "fields", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        fields_data = validated_data.pop("fields")
        section = Section.objects.create(**validated_data)

        for field_data in fields_data:
            Field.objects.create(section=section, **field_data)

        return section

    def to_representation(self, instance):
        """Override to customize how sections and fields are serialized."""
        ret = super().to_representation(instance)
        user_responses = self.context.get("user_responses", {})
        relevant_fields = []

        for field in instance.fields.all():
            if self._should_include_field(field, user_responses):
                relevant_fields.append(FieldSerializer(field).data)

        ret["fields"] = relevant_fields
        return ret

    def _should_include_field(self, field, user_responses):
        # Evaluate conditional logic
        if field.conditional_logic:
            if not self._evaluate_conditional_logic(field.conditional_logic, user_responses):
                return False

        # Evaluate dependencies
        if field.dependencies:
            if not self._evaluate_dependencies(field.dependencies, user_responses):
                return False

        return True

    def _evaluate_conditional_logic(self, logic, user_responses):
        operator_map = {
            "==": lambda actual, expected: actual == expected,
            "!=": lambda actual, expected: actual != expected,
            ">": lambda actual, expected: actual > expected,
            "<": lambda actual, expected: actual < expected,
            ">=": lambda actual, expected: actual >= expected,
            "<=": lambda actual, expected: actual <= expected,
        }

        field_id = logic.get("depends_on_field")
        operator = logic.get("operator")
        expected_value = logic.get("value")
        actual_value = user_responses.get(field_id)

        if operator in operator_map:
            return operator_map[operator](actual_value, expected_value)
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    def _evaluate_dependencies(self, dependencies, user_responses):
        operator_map = {
            "in": lambda actual, expected_values: actual in expected_values,
            "not_in": lambda actual, expected_values: actual not in expected_values,
            "contains": lambda actual, expected_value: expected_value in actual if isinstance(actual, list) else False,
        }

        field_id = dependencies.get("depends_on_field")
        operator = dependencies.get("operator")
        expected_values = dependencies.get("values")  # Expected values should be a list
        actual_value = user_responses.get(field_id)

        if operator in operator_map:
            return operator_map[operator](actual_value, expected_values)
        else:
            raise ValueError(f"Unsupported operator: {operator}")


class SurveySerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True)

    class Meta:
        model = Survey
        fields = ["id", "title", "description", "sections", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        sections_data = validated_data.pop("sections")
        survey = Survey.objects.create(**validated_data)

        for section_data in sections_data:
            section_data["survey"] = survey
            SectionSerializer.create(SectionSerializer(), validated_data=section_data)

        return survey

    def update(self, instance: Survey, validated_data):
        sections_data = validated_data.pop("sections", None)

        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.save()

        if sections_data is not None:
            # Clear existing sections
            instance.sections.all().delete()

            # Create new sections and fields
            for section_data in sections_data:
                section_data["survey"] = instance
                SectionSerializer.create(SectionSerializer(), validated_data=section_data)

        return instance

    def to_representation(self, instance):
        # Retrieve user responses from the context to pass down to the section serializer
        user_responses = self.context.get("user_responses", {})
        self.context["user_responses"] = user_responses
        return super().to_representation(instance)


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ["id", "survey", "email", "completed", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ResponseDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponseData
        fields = ["id", "response", "field", "value", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        field: Field = data["field"]
        value = data["value"]

        # Validate against predefined choices if the field has them
        if field.choices and value not in field.choices:
            raise serializers.ValidationError(f"Value '{value}' is not a valid choice.")

        # Conditional logic check
        if field.conditional_logic:
            # Implement logic to check if the conditions are met
            if not self._check_conditional_logic(field, data):
                raise serializers.ValidationError("Conditional logic not satisfied.")

        # Dependencies check
        if field.dependencies:
            # Implement logic to ensure dependencies are respected
            if not self._check_dependencies(field, data):
                raise serializers.ValidationError("Dependency conditions not met.")

        return data

    def _check_conditional_logic(self, field, data):
        # Logic to evaluate conditional logic JSON and compare it with previous responses
        # Placeholder implementation
        return True

    def _check_dependencies(self, field, data):
        # Logic to evaluate dependencies JSON and compare it with previous responses
        # Placeholder implementation
        return True
