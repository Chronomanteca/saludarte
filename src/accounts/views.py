from django.urls import reverse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.views.generic import DetailView, UpdateView

class ProfileView(LoginRequiredMixin, DetailView):
    """
    It shows the profile page of the user. It includes all the information
    about the user, and some links to edit the user's profile.
    """

    model = get_user_model()
    template_name = "accounts/profile.html"

    # The context_object is the currently authenticated user
    def get_object(self, queryset=None):
        return self.request.user


class EditProfileView(LoginRequiredMixin, UpdateView):
    """
    It allows the user to edit their profile information.
    """

    model = get_user_model()
    template_name = "accounts/edit_profile.html"
    # An user can't change their staff status nor site
    fields = [
        "first_name",
        "last_name",
        "email",
        "identification_type",
        "identification_number",
        "gender",
    ]

    def get_success_url(self):
        return reverse("accounts:profile")

    # The context_object is the currently authenticated user
    def get_object(self, queryset=None):
        return self.request.user
