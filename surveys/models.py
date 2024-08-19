from django.db import models
from survey_platform.common.models import TimestampedModel


class Survey(TimestampedModel):
    """Model representing a survey."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class Section(TimestampedModel):
    """Model representing a section in a survey."""

    survey = models.ForeignKey(Survey, related_name="sections", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    order = models.IntegerField()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Section {self.order}: {self.title}"


class Field(TimestampedModel):
    """Model representing a field in a section."""

    FIELD_TYPES = [
        ("text", "Text"),
        ("number", "Number"),
        ("date", "Date"),
        ("dropdown", "Dropdown"),
        ("checkbox", "Checkbox"),
        ("radio", "Radio"),
    ]

    section = models.ForeignKey(Section, related_name="fields", on_delete=models.CASCADE)
    label = models.CharField(max_length=255)
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES)
    required = models.BooleanField(default=False)
    order = models.IntegerField()
    conditional_logic = models.JSONField(blank=True, null=True)  # Store complex logic for field visibility
    dependencies = models.JSONField(blank=True, null=True)  # Handle dependencies between fields across sections

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.label} ({self.field_type})"


class Response(TimestampedModel):
    """Model representing the response to a survey."""

    survey = models.ForeignKey(Survey, related_name="responses", on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)  # Email for tracking user, nullable for anonymous users
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Response to {self.survey.title} by {'Anonymous' if not self.email else self.email}"


class ResponseData(TimestampedModel):
    """Model representing the data for a specific response field."""

    response = models.ForeignKey(Response, related_name="response_data", on_delete=models.CASCADE)
    field = models.ForeignKey(Field, related_name="responses", on_delete=models.CASCADE)
    value = models.TextField()

    def __str__(self):
        return f"Response to {self.field.label}: {self.value}"
