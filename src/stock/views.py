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

from django.db.models import Sum

from residents.models import Resident, MedicationInventory, Prescription
from medications.models import Presentation

class StockIndexView(LoginRequiredMixin, ListView):
    """
    It shows a list of all the medications in the database.
    Offers actions to alter the medications:
    - Create a new medication
    - Edit an existing medication
    - Delete an existing medication
    """

    model = Resident

    context_object_name = "residents"
    template_name = "stock/index.html"

    def get_context_data(self, **kwargs):
        context = super(StockIndexView, self).get_context_data(**kwargs) # get the default context data
        entradas = MedicationInventory.objects.all()
        residents = Resident.objects.all()
        totales = entradas.values("presentation").annotate(total_cantidad = Sum(('ammount')))
        for r in residents:
            entradas = MedicationInventory.objects.filter(resident = r)
            pres = Prescription.objects.filter(resident = r)
            totales = entradas.values("presentation").annotate(total_cantidad = Sum(('ammount')))
            for t in totales:          
                name = Presentation.objects.get(pk = t.get("presentation"))
                try:                        
                    p = pres.filter(presentation = t.get("presentation")).latest("date_delivery")
                    dosage = p.get_full_dosage                
                except Prescription.DoesNotExist:
                    dosage = 0
                
                stock_ammount = t.get("total_cantidad")
                t["presentation_name"] = name
                t["resident"] = r
                t["stock"] = stock_ammount
                t["dosage"] = dosage
        
        return context


    def get_queryset(self):

        residentes = Resident.objects.all()
        return residentes
