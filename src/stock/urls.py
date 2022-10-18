from django.urls import path

from . import views


app_name = "stock"
urlpatterns = [
    # name: residents:index, path: /inventarios/
    path("", views.StockIndexView.as_view(), name="index"),
]
