from .models import Category


def nav_categories(request):
    """Make categories available in every template for the navbar dropdown."""
    return {
        'nav_categories': Category.objects.all(),
    }
