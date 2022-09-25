from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

from django.urls import reverse_lazy

from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView,
)

from .models import Resident, Relative
from .views import OnlyAccessMySiteResidentsMixin



class NewPrescriptionView():
    def hola():
        return 0