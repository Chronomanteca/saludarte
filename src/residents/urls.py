from django.urls import path

from . import views
from . import relative_views
from . import prescription_views
from . import inventory_views
from . import pillbox_views


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
        prescription_views.create_prescription,
        name="new_prescription",
    ),
    # name: residents:edit_prescription, path: /residentes/<pk>/editar_prescripcion/
    path(
        "<int:pk>/editar_prescripcion/<int:prescription_pk>/",
        prescription_views.edit_prescription,
        name="edit_prescription",
    ),
    # name: residents:delete_prescription, path: /residentes/<pk>/eliminar_prescripcion/
    path(
        "<int:pk>/eliminar_prescripcion/<int:prescription_pk>/",
        prescription_views.DeletePrescriptionView.as_view(),
        name="delete_prescription",
    ),

    # name: residents:new_inventory_entry, path: /residentes/<pk>/nueva_entrada_inventario/    
    path(
        "<int:pk>/nueva_entrada_inventario/",
        inventory_views.NewInventoryEntry.as_view(),
        name="new_inventory_entry",
    ),

    # name: residents:inventory_entry_details, path: /residentes/entradas_inventario/<pk>
    path(
        "<int:pk>/entradas_inventario/<int:presentation_pk>",
        inventory_views.InventoryEntryIndexView.as_view(),
        name="inventory_entries",
    ),
    # name: residents:edit_inventory_entry, path: /residentes/<pk>/editar_entrada_inventario/
    path(
        "<int:pk>/editar_entrada_inventario/<int:medication_inventory_pk>/",
        inventory_views.EditInventoryEntry.as_view(),
        name="edit_inventory_entry",
    ),

    # name: residents:delete_inventory_entry, path: /residentes/<pk>/editar_entrada_inventario/
    path(
        "<int:pk>/eliminar_entrada_inventario/<int:medication_inventory_pk>/",
        inventory_views.DeleteInventoryEntry.as_view(),
        name="delete_inventory_entry",
    ),

    #Vista para controlar el pastillero
    # name: residents:manage_pillbox, path: /residentes/<pk>/gestionar_pastillero/
    path(
        "<int:pk>/gestionar_pastillero/",
        pillbox_views.manage_pillbox,
        name="manage_pillbox",
    ),

]
