from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from medications.models import Presentation
from residents.models import MedicationInventory, Prescription, Resident


"""
NOTA: Esta pagina deberia obtener solo los residentes que tienen el mismo Site del usuario, esto hay que corregirlo, 
se puede tomar como referencia residents.views para ver como se hace este proceso. Una disculpa
"""

class StockIndexView(LoginRequiredMixin, ListView):
    """
    It shows a list of all the medications in the database.
    Offers actions to alter the medications:
    - Create a new medication
    - Edit an existing medication
    - Delete an existing medication
    """

    def post(self, request, **kwargs):

        print("Testeando post")
        my_data = request.POST.get("secret", None)  
        residents = Resident.objects.all()
        lista = []
        i = 0
        for r in residents:
            pres = Prescription.objects.filter(resident = r)            

        messages.success(
            request, "Se han enviado los correos correctamente: " 
        )
        return redirect("stock:index")

    model = Resident

    context_object_name = "residents"
    template_name = "stock/index.html"

    def get_context_data(self, **kwargs):
        context = super(StockIndexView, self).get_context_data(**kwargs) # get the default context data
        entradas = MedicationInventory.objects.all()
        residents = Resident.objects.all()
        totales = entradas.values("presentation").annotate(total_cantidad = Sum(('ammount')))
        tot_test = []
        for r in residents:
            tot_test.append(r.get_inventory_info)
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
