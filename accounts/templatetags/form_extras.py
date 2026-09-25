"""Small template helpers for rendering plain Django forms with Bootstrap 5
classes, since we don't pull in a forms-rendering package (e.g.
django-crispy-forms) for this scaffold.

Usage in any app's template:
    {% load form_extras %}
    {{ field|add_class:"form-control" }}
"""
from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(field, css_class):
    """Add a CSS class to a bound form field's widget for rendering."""
    existing = field.field.widget.attrs.get("class", "")
    classes = f"{existing} {css_class}".strip()
    return field.as_widget(attrs={**field.field.widget.attrs, "class": classes})
