from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .models import Resident, Prescription, Presentation


class OnlyAccessMySiteResidentsMixin(UserPassesTestMixin):
    """
    Verifies that the current user shares the same
    site as the resident.
    """

    login_url = reverse_lazy("login")

    def test_func(self):
        # If the user's site is Global (1) then it can access
        # all the residents.
        if self.request.user.site.id == 1:
            return True

        # Otherwise, match the user's site to the resident's site.
        resident = get_object_or_404(Resident, pk=self.kwargs["pk"])
        return self.request.user.site.id == resident.site.id


class ResidentsIndexView(LoginRequiredMixin, ListView):
    """
    It shows a list of all the residents in the database.
    Offers actions to alter the residents:
    - Create a new resident
    - View an existing resident
    - Edit an existing resident
    - Delete an existing resident
    """

    context_object_name = "residents"
    template_name = "residents/index.html"

    def get_queryset(self):
        """
        Returns all the residents in the database that match
        the user's site. If the user's site is Global (1)
        then it returns all the residents in the database.
        """

        if self.request.user.site.id == 1:
            return Resident.objects.all()

        return Resident.objects.filter(site=self.request.user.site)


class DetailResidentView(
    LoginRequiredMixin,
    OnlyAccessMySiteResidentsMixin,
    ListView,
):
    """
    It shows the details of a specific resident in a paginated view.
    - First page: resident's basic information
    - Second page: resident's relatives
    - Third page: resident's medical information
    - Fourth page: Medication inventory TODO

    Offers actions to edit the resident:
    - Edit the resident's information (relatives and inventory too)
    - Delete the resident
    """

    paginate_by = 1
    template_name = "residents/detail_resident.html"

    def get_queryset(self):
        resident = get_object_or_404(Resident, pk=self.kwargs["pk"])

        return [
            resident,
            resident.relative_set.all().order_by("kinship"),
            resident.prescription_set.all(),
            resident,
        ]


class NewResidentView(LoginRequiredMixin, CreateView):
    """
    It shows a form to create a new resident.
    """

    model = Resident
    template_name = "residents/new_resident.html"
    fields = [
        "first_name",
        "last_name",
        "identification_type",
        "identification_number",
        "gender",
        "site",
        "date_birth",
        "date_joined",
        "eps",
    ]

    def get_success_url(self):
        messages.success(
            self.request, "El residente ha sido creado exitosamente."
        )
        return reverse_lazy("residents:index")


class EditResidentView(
    LoginRequiredMixin, OnlyAccessMySiteResidentsMixin, UpdateView
):
    """
    It shows a form to edit an existing resident.
    """

    model = Resident
    template_name = "residents/edit_resident.html"
    fields = [
        "first_name",
        "last_name",
        "identification_type",
        "identification_number",
        "gender",
        "site",
        "date_birth",
        "date_joined",
        "eps",
    ]


class DeleteResidentView(
    LoginRequiredMixin, OnlyAccessMySiteResidentsMixin, DeleteView
):
    """
    Deletes a resident given its id.
    """

    model = Resident

    def get_success_url(self):
        messages.success(
            self.request, "El residente ha sido eliminado exitosamente."
        )
        return reverse_lazy("residents:index")
