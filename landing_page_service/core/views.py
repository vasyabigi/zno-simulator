# from django.http import HttpResponse
from django.shortcuts import render, redirect
from core.models import ZNOSubject


def landing_page_view(request):
    subjects = ZNOSubject.objects.filter(is_active=True)

    return render(request, "ZNOtask.html", context={"subjects": subjects,},)
