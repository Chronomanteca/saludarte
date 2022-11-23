from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm

from django.http import (
    HttpResponseNotAllowed,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from core.views import StaffMemberRequiredMixin
from accounts.models import Site

class HqIndexView(StaffMemberRequiredMixin, ListView):
    """
    It shows a list of all the sites in the database.
    Offers actions to edit the users:
    - Create a new site
    - View an existing site
    - Edit an existing site
    - Delete an existing site
    """

    template_name = "headquarters/index.html"
    context_object_name = "sites"
    model = Site

    def get_queryset(self):
        sites = Site.objects.all()  
        print(sites)
        return  sites


class NewHqView(StaffMemberRequiredMixin, CreateView):
    """
    It allows a staff user to create a new user.
    It shows a form to input the user's data.
    It also sends a welcome email to the user with
    a link to reset their password.
    """

    model = Site
    template_name = "headquarters/new_site.html"
    # The password is not included because it is left blank when a new
    # user is created. The welcome email has a link to reset the password.
    fields = [
        "name",
        "address",
    ]

    def get_success_url(self):
        messages.success(
            self.request, "La sede ha sido creado exitosamente."
        )
        return reverse_lazy("headquarters:index")



class EditHqView(StaffMemberRequiredMixin, UpdateView):
    """
    It allows a staff user to update an existing user.
    It shows a form to edit the user's data.
    """

    model = Site
    template_name = "headquarters/edit_site.html"
    fields = [
        "name",
        "address",
    ]

    def get_object(self):
        return Site.objects.get(pk=self.kwargs["pk"])

    def get_success_url(self):
        messages.success(
            self.request, "La sede ha sido editada exitosamente."
        )
        return reverse_lazy("headquarters:index")

    


class DeleteHqView(StaffMemberRequiredMixin, DeleteView):
    """
    Deletes an user given its id.
    """

    model = Site

    def get_success_url(self):
        messages.success(
            self.request, "El usuario ha sido eliminado exitosamente."
        )
        return reverse_lazy("headquarters:index")
