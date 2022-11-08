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

#from .views import OnlyAccessMySiteResidentsMixin




def create_prescription(request, **callback_kwargs):
    """
    It shows a form to create a new prescription.
    It does so by rendering two forms:
    - A medication form to create the medication model.
    - Multiple distribution forms to create the distributions
    of the prescriptions, using the modelformset_factory.
    """    
    presentation_set = Presentation.objects.all()
    
    resident = get_object_or_404(Resident, pk=callback_kwargs["pk"])

    if request.method == "POST":  # If the forms were submitted
        prescription_form = PrescriptionForm(request.POST,initial={'resident': resident})
        prescription_form.instance.resident = resident
        distribution_formset = DistributionFormSet(request.POST)

        if prescription_form.is_valid() and distribution_formset.is_valid():
            print("FORM VALID -----------------------------------")
            user = User.objects.get(email = request.user) 
            print(user.first_name)        

            prescription_form.instance.responsible = user
            prescription = prescription_form.save(commit = False)
            prescription.save()

            # Get the presentations' models from the formset
            # but delete those marked for deletion
            #distributions = distribution_formset.save(commit=False)

            # Set the medication to the presentations

            for distribution in distribution_formset:
                data = distribution.save(commit = False)
                data.prescription = prescription
                data.save()

            messages.success(
                request, "Se creo la prescripcion correctamente."
            )
            return redirect("residents:index")
    else:  # First GET request
        # Create empty forms        
        prescription_form = PrescriptionForm(initial={'resident': resident})
        distribution_formset = DistributionFormSet(
            queryset=Distribution.objects.none()
        )

    return render(
        request,
        "residents/new_prescription.html",
        # Additional context are the forms
        {
            "prescription_form": prescription_form,
            "distribution_formset": distribution_formset,
            "presentation_set" : presentation_set,
        },
    )

def edit_prescription(request,pk, **callback_kwargs):
    """
    It shows a form to create a new prescription.
    It does so by rendering two forms:
    - A medication form to create the medication model.
    - Multiple distribution forms to create the distributions
    of the prescriptions, using the modelformset_factory.
    """    

    presentation_set = Presentation.objects.all()
    prescription =  get_object_or_404(Prescription, pk=callback_kwargs["prescription_pk"])
    
    #resident = get_object_or_404(Resident, pk=callback_kwargs["pk"])

    if request.method == "POST":  # If the forms were submitted
        prescription_form = PrescriptionForm(request.POST,instance = prescription)
        #prescription_form.instance.resident = resident

        distribution_formset = DistributionFormSet(request.POST)

        if prescription_form.is_valid() and distribution_formset.is_valid():
            print("FORM VALID -----------------------------------")
            prescription = prescription_form.save(commit = False)
            prescription.save()
            distribution_formset.save(commit=False)

            messages.success(
                request, "Se creo la prescripcion correctamente."
            )
            return redirect("residents:index")
    else:  # First GET request
        # Create empty forms                
        prescription_form = PrescriptionForm(instance = prescription)        
        distribution_formset = DistributionFormSet(
            queryset=Distribution.objects.filter(prescription = prescription)
        )

    return render(
        request,
        "residents/edit_prescription.html",
        # Additional context are the forms
        {
            "prescription_form": prescription_form,
            "distribution_formset": distribution_formset,
            "presentation_set" : presentation_set,
        },
    )

class DeletePrescriptionView(LoginRequiredMixin, OnlyAccessMySiteResidentsMixin, DeleteView):
    """
    Deletes a relative given its id.
    """

    model = Prescription

    def get_object(self):
        return Prescription.objects.get(pk=self.kwargs["prescription_pk"])

    def get_success_url(self):
        messages.success(
            self.request, "La prescripcion se ha borrado correctamente."
        )
        return (
            reverse_lazy("residents:detail", kwargs={"pk": self.kwargs["pk"]})
            + "?page=3"
        )
