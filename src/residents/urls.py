from django.urls import path

from . import views
from . import relative_views
from . import prescription_views
from . import inventory_views


app_name = "residents"
urlpatterns = [
    # name: residents:index, path: /residentes/
    path("", views.ResidentsIndexView.as_view(), name="index"),
    # name: users:detail, path: /residentes/<pk>/,
    path("<int:pk>/", views.DetailResidentView.as_view(), name="detail"),
    # name: residents:new, path: /residentes/nuevo/
    path("nuevo/", views.NewResidentView.as_view(), name="new"),
    # name: residents:edit, path: /residentes/<pk>/editar/
    path("<int:pk>/editar/", views.EditResidentView.as_view(), name="edit"),
    # name: residents:delete, path: /residentes/<pk>/eliminar/
    path(
        "<int:pk>/eliminar/",
        views.DeleteResidentView.as_view(),
        name="delete",
    ),
    # name: residents:new_relative, path: /residentes/<pk>/nuevo_familiar/
    path(
        "<int:pk>/nuevo_familiar/",
        relative_views.NewRelativeView.as_view(),
        name="new_relative",
    ),
    # name: residents:edit_relative, path: /residentes/<pk>/editar_familiar/
    path(
        "<int:pk>/editar_familiar/<int:relative_pk>/",
        relative_views.EditRelativeView.as_view(),
        name="edit_relative",
    ),
    # name: residents:delete_relative, path: /residentes/<pk>/eliminar_familiar/
    path(
        "<int:pk>/eliminar_familiar/<int:relative_pk>/",
        relative_views.DeleteRelativeView.as_view(),
        name="delete_relative",
    ),
    # name: residents:new_prescription, path: /residentes/<pk>/nueva_prescripcion/
    path(
        "<int:pk>/nueva_prescripcion/",
        prescription_views.NewPrescriptionView,
        name="new_prescription",
    ),

    # name: residents:create_report, path: /residentes/<pk>/create_report/    
    path(
        "<int:pk>/crear_reporte/",
        inventory_views.CreateReport.as_view(),
        name="create_report",
    ),
]
