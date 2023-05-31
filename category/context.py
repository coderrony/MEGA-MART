

from .models import Category


def context(request):
    links = Category.objects.all()

    return dict(links=links)
