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
            fields_data = section_data.pop("fields")
            section = Section.objects.create(survey=survey, **section_data)

            for field_data in fields_data:
                Field.objects.create(section=section, **field_data)

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
                fields_data = section_data.pop("fields")
                section = Section.objects.create(survey=instance, **section_data)

                for field_data in fields_data:
                    Field.objects.create(section=section, **field_data)

        return instance


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
