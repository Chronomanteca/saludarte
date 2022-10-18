from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from django.views.generic import (
    ListView,
    #    UpdateView,
    DeleteView,
)

from django.forms import modelform_factory, modelformset_factory

from .models import Medication, Presentation

class MedicationsIndexView(LoginRequiredMixin, ListView):
    """
    It shows a list of all the medications in the database.
    Offers actions to alter the medications:
    - Create a new medication
    - Edit an existing medication
    - Delete an existing medication
    """
    model = Medication    
    context_object_name = "medications"
    template_name = "medications/index.html"


def create_medication(request):
    
    """
    It shows a form to create a new medication.
    It does so by rendering two forms:
    - A medication form to create the medication model.
    - Multiple presentation forms to create the presentations
    of the medications, using the modelformset_factory.
    """

    MedicationForm = modelform_factory(
        Medication,
        fields=("name", "description"),
    )
    PresentationFormSet = modelformset_factory(
        Presentation,
        fields=("type", "measure_unit", "measure"),
        can_delete=True,
    )

    if request.method == "POST":  # If the forms were submitted
        medication_form = MedicationForm(request.POST)
        presentation_formset = PresentationFormSet(request.POST, request.FILES)

        if medication_form.is_valid() and presentation_formset.is_valid():
            medication = medication_form.save()
            # Get the presentations' models from the formset
            # but delete those marked for deletion
            presentations = presentation_formset.save(commit=False)

            # Set the medication to the presentations
            for presentation in presentations:
                presentation.medication = medication
                presentation.save()

            messages.success(
                request, "The medication has been created successfully."
            )
            return redirect("medications:index")
    else:  # First GET request
        # Create empty forms
        medication_form = MedicationForm()
        presentation_formset = PresentationFormSet(
            queryset=Presentation.objects.none()
        )

    return render(
        request,
        "medications/new_medication.html",
        # Additional context are the forms
        {
            "medication_form": medication_form,
            "presentation_formset": presentation_formset,
        },
    )


def edit_medication(request, pk):
    """
    It shows a form to edit an existing medication.
    It does so by rendering two forms:
    - A medication form to edit the medication model.
    - Multiple presentation forms to edit the presentations
    of the medications, using the modelformset_factory.
    """

    medication = get_object_or_404(Medication, pk=pk)
    MedicationForm = modelform_factory(
        Medication,
        fields=("name", "description"),
    )
    PresentationFormSet = modelformset_factory(
        Presentation,
        fields=("type", "measure_unit", "measure"),
        can_delete=True,
    )

    if request.method == "POST":  # If the forms were submitted
        medication_form = MedicationForm(request.POST, instance=medication)
        presentation_formset = PresentationFormSet(
            request.POST,
            request.FILES,
            # queryset=Presentation.objects.filter(medication=medication),
        )

        if medication_form.is_valid() and presentation_formset.is_valid():
            medication = medication_form.save()
            presentations = presentation_formset.save(commit=False)

            # Set the medication to the presentations
            # for presentation in presentations:
            #    presentation.medication = medication
            #    presentation.save()

            messages.success(
                request, "The medication has been edited successfully."
            )
            return redirect("medications:index")
    else:  # First GET request
        # Create forms with the data of the medication
        medication_form = MedicationForm(instance=medication)
        presentation_formset = PresentationFormSet(
            queryset=Presentation.objects.filter(medication=medication)
        )

    return render(
        request,
        "medications/edit_medication.html",
        # Additional context are the forms
        {
            "medication_form": medication_form,
            "presentation_formset": presentation_formset,
        },
    )


class DeleteMedicationView(LoginRequiredMixin, DeleteView):
    """
    Deletes a medication given its id.
    """

    model = Medication
    # Only allow POST requests (DeleteView deletes objects using POST, crazy right?)
    # TODO: Maybe create a custom view that only allows DELETE requests?
    http_method_names = ["post"]

    def get_success_url(self):
        messages.success(
            self.request, "El medicamento ha sido eliminado exitosamente."
        )
        return reverse_lazy("medications:index")
