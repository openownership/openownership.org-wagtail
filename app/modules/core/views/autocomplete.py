from django.http import JsonResponse


def custom_tag_autocomplete(request, model):
    term = request.GET.get('term', None)
    if term:
        tags = model.objects.filter(name__istartswith=term).order_by('name')
    else:
        tags = model.objects.none()

    return JsonResponse([tag.name for tag in tags], safe=False)
