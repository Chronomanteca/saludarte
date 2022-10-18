from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

from django.urls import reverse_lazy

from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView,
)

from .models import MedicationInventory, Resident, Relative
from medications.models import Presentation
from .views import OnlyAccessMySiteResidentsMixin




class NewInventoryEntry(
    LoginRequiredMixin, OnlyAccessMySiteResidentsMixin, CreateView
):
    """
    It shows a form to create a new relative.
    """

    model = MedicationInventory
    template_name = "residents/new_inventory_entry.html"
    fields = [
        "presentation",
        "relative",
        "ammount",
        "delivery_units",
        "date_delivery",
        "comentarios",
    ]

    def form_valid(self, form):
        resident = get_object_or_404(Resident, pk=self.kwargs["pk"])
        user = self.request.user
        form.instance.responsible = user
        form.instance.resident = resident
        return super(NewInventoryEntry, self).form_valid(form)


    def get_context_data(self, **kwargs):
        r = get_object_or_404(Resident, pk=self.kwargs["pk"])

        context = super().get_context_data(**kwargs)
        context["presentation_set"] = Presentation.objects.all()
        context["relatives"] = Relative.objects.filter(resident_id = r.id)
        return context

    def get_success_url(self):
        messages.success(
            self.request, "La entrada de inventario se ha creado correctamente"
        )
        return (
            reverse_lazy("residents:detail", kwargs={"pk": self.kwargs["pk"]})
            + "?page=4"
        )
