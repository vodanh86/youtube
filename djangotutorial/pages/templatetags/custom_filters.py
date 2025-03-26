from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """Lấy giá trị từ dictionary bằng key."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None