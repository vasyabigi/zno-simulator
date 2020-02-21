from django.shortcuts import render
from core.models import ZNOSubject


def landing_page_view(request):
    subjects = ZNOSubject.objects.filter(is_active=True)

    return render(request, "landing_page.html", context={"subjects": subjects})


def about_us_view(request):
    subjects = ZNOSubject.objects.filter(is_active=True)

    variable = []
    return render(
        request, "about_us.html", context={"about": variable, "subjects": subjects},
    )
