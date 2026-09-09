from django.urls import path

from . import views


app_name = "cards"

urlpatterns = [
    # path("", views.index, name="index"),
    path("", views.card_list, name="list"),
    path("new/", views.card_create, name="create")
]