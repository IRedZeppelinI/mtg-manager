# para render à view
# from django.shortcuts import render

# Create your views here.

# from django.http import HttpResponse


# def index(request):
#     return HttpResponse("MTG Manager — Card catalogue")

from django.shortcuts import redirect, render

from .forms import CardForm
from .models import Card


def card_list(request):
    cards = Card.objects.all().order_by("name")

    context = {
        "cards": cards,
    }

    return render(request, "cards/card_list.html", context)


def card_create(request):
    if request.method == "POST":
        form = CardForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("cards:list")
    else:
        form = CardForm()

    context = {
        "form": form,
    }

    return render(request, "cards/card_form.html", context)