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



class CreateReport(
    LoginRequiredMixin, OnlyAccessMySiteResidentsMixin, CreateView
):
    """
    It shows a form to send the inventory medication report via email.
    """

    model = Relative
    template_name = "residents/new_relative.html"
    fields = [
        "first_name",
        "last_name",
        "identification_type",
        "identification_number",
        "gender",
        "kinship",
        "email",
        "contact_number",
        "email_alerts",
        "whatsapp_alerts",
    ]


    def get_success_url(self):
        messages.success(
            self.request, "El familiar ha sido creado exitosamente."
        )
        return (
            reverse_lazy("residents:detail", kwargs={"pk": self.kwargs["pk"]})
            + "?page=4"
        )