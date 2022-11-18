from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView
from medications.models import Presentation

from .models import Distribution, Prescription, Resident
from accounts.models import User
from .prescription_forms import DistributionFormSet, PrescriptionForm
from .views import OnlyAccessMySiteResidentsMixin
from residents.models import MedicationInventory, Resident, Relative, Prescription, Loan
from django.core.exceptions import ObjectDoesNotExist

#from .views import OnlyAccessMySiteResidentsMixin



#Concept: 1 - input, 2 - output,  3 - loan
def manage_pillbox(request, **callback_kwargs):
    """
    It shows a form to create a new prescription.
    It does so by rendering two forms:
    - A medication form to create the medication model.
    - Multiple distribution forms to create the distributions
    of the prescriptions, using the modelformset_factory.
    """    
    presentation_set = Presentation.objects.all()    
    
    resident = get_object_or_404(Resident, pk=callback_kwargs["pk"])
    rel = Relative.objects.get(first_name = "Saludarte",resident = resident)
    user = User.objects.get(email = request.user) 

    totales = resident.get_inventory_info()
    print(totales)

    if request.method == "POST":  # If the forms were submitted
        data = []
        for i in range(len(totales)):
            idPresentation = "presentation_id_"+str(i+1)
            strPresentation = request.POST.get(idPresentation, None).split("/")[0]
            idOutput = "output_"+str(i+1)
            idAmmount = "ammount_"+str(i+1)
            strAmmount = request.POST.get(idAmmount, None).split()[0]   
            pres = Presentation.objects.get(pk = strPresentation)
            output = float(request.POST.get(idOutput, None))
            ammount = float(strAmmount)
            #Looking up related prrescription
            prescription_set = Prescription.objects.filter(resident = resident)
            prescription = prescription_set.filter(presentation = pres).latest("date_delivery")
            #control de prestamos y salidas
            if output > ammount:                
                #first we loan the difference between the output and the ammount, then we take that out through regulat pillbox filling
                loan = abs(output-ammount)
                print("TENGO DEUDA= output "+str(output)+" ammount = "+str(ammount)+" loan = "+str(loan))
                inv_loan = MedicationInventory(resident = resident, relative = rel,presentation = pres,delivery_units = prescription.dosage_units, ammount = loan,comentarios = "Prestamo para el pastillero",responsible = user, concept = 3)
                try:
                    loan_object = Loan.objects.get(presentation = pres)
                    loan_object.ammount_loan = loan_object.ammount_loan+(loan)                    
                    print(loan_object)
                    loan_object.save()
                except ObjectDoesNotExist:
                    print("no hay deuda")
                    Loan(resident = resident, presentation = pres,loan_units = prescription.dosage_units, ammount_loan = loan).save()
                inv_loan.save()
            inv = MedicationInventory(resident = resident, relative = rel,presentation = pres,concept = 2, ammount = -output,comentarios = "Llenado de pastillero",responsible = user)
            data.append(ammount)
            if(output>0):
                inv.save()
            


        messages.success(
            request
        )
        return redirect("residents:index")

    return render(
        request,
        "residents/fill_pillbox.html",
        # Additional context are the forms
        {
            "inventory":totales
        },
    )
