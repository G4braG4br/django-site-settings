import nh3
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


DEFAULT_ALLOWED_TAGS = {"a", "b", "i", "strong", "em", "p", "br", "span", "ul", "ol", "li", "h1", "h2", "h3"}
DEFAULT_ALLOWED_ATTRIBUTES = {
    "a": {"href", "title", "target"},
    "span": {"class", "style"},
}


class SanitizedHTMLField(models.TextField):
    def __init__(self, *args, **kwargs):
        self.allowed_tags = kwargs.pop(
            "allowed_tags",
            DEFAULT_ALLOWED_TAGS
        )
        self.allowed_attributes = kwargs.pop(
            "allowed_attributes",
            DEFAULT_ALLOWED_ATTRIBUTES
        )
        super().__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        value = super().clean(value, model_instance)

        if value:
            clean_value = nh3.clean(
                value,
                tags=self.allowed_tags,
                attributes=self.allowed_attributes,
                link_rel="noopener noreferrer"
            )

            if value.strip() != clean_value.strip():
                raise ValidationError(
                    _("The text contains text formatting tags or attributes that are not allowed for security reasons.")
                )

        return value
