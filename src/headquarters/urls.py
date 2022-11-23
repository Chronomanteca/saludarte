from django.urls import path

from . import views


app_name = "headquarters"
urlpatterns = [
    # name: headquarters:index, path: /usuarios/
    path("", views.HqIndexView.as_view(), name="index"),
    # name: headquarters:new, path: /usuarios/nuevo/
    path("nueva/", views.NewHqView.as_view(), name="new"),
    # name: headquarters:edit, path: /usuarios/<pk>/editar/
    path("<int:pk>/editar/", views.EditHqView.as_view(), name="edit"),
    # name: headquarters:delete, path: /usuarios/<pk>/eliminar/
    path("<int:pk>/eliminar/", views.DeleteHqView.as_view(), name="delete"),
]
