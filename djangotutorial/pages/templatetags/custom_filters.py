from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """Lấy giá trị từ dictionary bằng key."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def format_date(value):
    """Định dạng ngày từ YYYYMMDD thành YYYY/MM/DD."""
    if len(value) == 8 and value.isdigit():
        return f"{value[:4]}/{value[4:6]}/{value[6:]}"
    return value