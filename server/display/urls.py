from django.urls import path
from display import views

urlpatterns = [
    path("", views.render_default_index),  # render
    path("index_data", views.get_index_data),  # ajax
    path("group", views.render_default_group),  # render
    path("group_data", views.get_group_data),  # render
]
