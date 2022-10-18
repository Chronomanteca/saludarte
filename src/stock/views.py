from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from residents.models import Resident, MedicationInventory, Prescription
from medications.models import Medication

class StockIndexView(LoginRequiredMixin, ListView):
    """
    It shows a list of all the medications in the database.
    Offers actions to alter the medications:
    - Create a new medication
    - Edit an existing medication
    - Delete an existing medication
    """

    model = MedicationInventory

    context_object_name = "inventory"
    template_name = "stock/index.html"

    def get_context_data(self, **kwargs):
        context = super(StockIndexView, self).get_context_data(**kwargs)
        context.update({
            'medication_inventory': MedicationInventory.objects.all(),
            'prescriptions': Prescription.objects.all(),
        })
        return context

    def get_queryset(self):
        return MedicationInventory.objects.order_by("resident")
