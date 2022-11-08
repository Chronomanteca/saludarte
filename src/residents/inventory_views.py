from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

from django.urls import reverse_lazy

from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView,
    ListView,
)

from django.db.models import Avg, Count, Min, Sum

from .models import MedicationInventory, Resident, Relative
from accounts.models import User
from core.models import Person
from medications.models import Presentation
from .views import OnlyAccessMySiteResidentsMixin


class InventoryEntryIndexView(LoginRequiredMixin, ListView):

    context_object_name = "entries"
    template_name = "residents/detail_inventory_entry.html"

    def get_object(self):
        return MedicationInventory.objects.get(pk=self.kwargs["medication_inventory_pk"])


    def get_queryset(self):
        """
        Returns all the residents in the database that match
        the user's site. If the user's site is Global (1)
        then it returns all the residents in the database.
        """

        if self.request.user.site.id == 1:
            return Resident.objects.all()

        return Resident.objects.filter(site=self.request.user.site)




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
        user = User.objects.get(email = self.request.user)
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

class EditInventoryEntry(
    LoginRequiredMixin, OnlyAccessMySiteResidentsMixin, UpdateView
):
    """
    It shows a form to edit an existing relative.
    """


    model = MedicationInventory
    template_name = "residents/edit_inventory_entry.html"
    fields = [
        "presentation",
        "relative",
        "ammount",
        "delivery_units",
        "date_delivery",
        "comentarios",        
    ]


    def get_context_data(self, **kwargs):
        r = get_object_or_404(Resident, pk=self.kwargs["pk"])

        context = super().get_context_data(**kwargs)
        entry = MedicationInventory.objects.get(pk=self.kwargs["medication_inventory_pk"])
        entry.responsible = None
        print("entradas individuales")
        all = MedicationInventory.objects.all()
        for a in all:
            msg = a.get_presentation.__str__()+" cantidad = "+a.ammount.__str__()
            print(msg)
        print("Imprimiento prueba")
        test = MedicationInventory.objects.values("presentation").annotate(total_cantidad = Sum('ammount'))
        for t in test:
            msg = Presentation.objects.get(pk = t.get("presentation")).__str__()+" total = "+t.get("total_cantidad").__str__()
            print(msg)
            



        context["presentation_set"] =  Presentation.objects.filter(pk = entry.presentation.id)
        context["relatives"] = Relative.objects.filter(resident_id = r.id)
        
        return context

    def get_object(self):
        return MedicationInventory.objects.get(pk=self.kwargs["medication_inventory_pk"])

    def get_success_url(self):
        url = super(UpdateView, self).get_success_url()
        messages.success(
            self.request, "La entrada de inventario se ha sido editado exitosamente."
        )
        return url


class DeleteInventoryEntry(
    LoginRequiredMixin, OnlyAccessMySiteResidentsMixin, DeleteView
):
    """
    Deletes a relative given its id.
    """

    model = MedicationInventory

    def get_object(self, **kwargs):
        return MedicationInventory.objects.get(pk=self.kwargs["medication_inventory_pk"])

    def get_success_url(self):
        messages.success(
            self.request, "La entrada se ha sido eliminado exitosamente."
        )
        return (
            reverse_lazy("residents:detail", kwargs={"pk": self.kwargs["pk"]})
            + "?page=4"
        )
