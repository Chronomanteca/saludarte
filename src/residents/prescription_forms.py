from django.forms import ModelForm, modelform_factory, inlineformset_factory
from .models import Prescription, Distribution, Resident

PrescriptionForm = modelform_factory(
    Prescription, fields = {"presentation","dosage", "dosage_units"}
)

class DistributionForm(ModelForm):
    class Meta:
        model = Distribution    
        exclude = ()

DistributionFormSet = inlineformset_factory(
    Prescription,Distribution, form = DistributionForm, extra = 1
)
