from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from adverts.models import Advert
from contracts.forms import AcademicQualificationForm

from .forms import (
    CustomPasswordChangeForm,
    ProfileUpdateForm,
    UserRegisterForm,
    UserUpdateForm,
    ExperienceForm,
    ReferenceForm,
    ContactForm, AccountActivationForm
)
from .models import Profile, UserAccount, Reference, Contact
from .decorators import user_not_authenticated, is_active, is_admin
from .tokens import account_activation_token
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from adverts.utils import send_email, send_html_email


def activate_account(request):
    if request.method == "POST":
        form = AccountActivationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = UserAccount.objects.filter(email=email).first()
            activateEmail(request, user, email)
            return redirect('accounts:login')
    else:
        form = AccountActivationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/inactive.html', context)


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(
            request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('accounts:login')
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('adverts:adverts')


def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    html_message = render_to_string(
        "accounts/verify_email_message.html", {
            'user': user.email,
            'domain': get_current_site(request).domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
            "protocol": 'https' if request.is_secure() else 'http'
        })
    try:
        send_html_email(mail_subject, html_message, [to_email])
        # email = EmailMessage(mail_subject, message, to=[to_email])
        messages.success(request, f'Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
                received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')
    except:
        messages.error(
            request, f'Problem sending email to {to_email}, check if you typed it correctly.')


class UserRegisterView(View):
    def get(self, request, *args, **kwargs):
        form = UserRegisterForm()
        return render(request, "accounts/register.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            try:
                activateEmail(request, user, form.cleaned_data.get('email'))
                messages.success(
                    request,
                    "Your Account has been created successifully, please check your email to activate it."
                )
                return redirect("accounts:login")
            except:
                messages.error(
                    request,
                    "Failed to send the activation email, Please check the email you provided!",
                )
        return render(request, "accounts/register.html", {"form": form})


class UserProfileView(LoginRequiredMixin, View):
    # login_url = '/login/'
    def test_func(self):
        # Define the test function to check if the user is a guest
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        # Redirect the user if they fail the test
        login_url = reverse(
            "accounts:login"
        )  # Replace 'login' with the URL or name of the login page
        next_url = (
            self.request.get_full_path()
        )  # Get the current URL as the 'next' parameter
        redirect_url = (
            # Append 'next' parameter to the login URL
            f"{login_url}?next={next_url}"
        )
        return redirect(redirect_url)

    def get(self, request, *args, **kwargs):
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        context = {"u_form": u_form, "p_form": p_form}
        return render(request, "accounts/profile.html", context)

    def post(self, request, *args, **kwargs):
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        context = {"u_form": u_form, "p_form": p_form}
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(
                request, "You profile has been updated successfully!")
            return redirect("accounts:dashboard")
        messages.warning(request, "Failed to update your profile!")
        return render(request, "accounts/profile.html", context)


@login_required
def dashboard(request):
    e_form = AcademicQualificationForm()
    form = ExperienceForm()
    r_form = ReferenceForm()
    adverts = Advert.objects.filter(applications__applicant=request.user)
    context = {
        "form": form,
        "adverts": adverts,
        "e_form": e_form,
        "r_form": r_form
    }
    return render(request, "accounts/dashboard.html", context)


class NewPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy(
        "accounts:password_change_done"
    )  # URL to redirect after successful password change


def password_change_done(request):
    return render(
        request, "accounts/password_change_done.html", {
            "title": "password change done"}
    )


@login_required
def add_reference(request):
    if request.method == 'POST':
        form = ReferenceForm(request.POST)
        if form.is_valid():
            reference = form.save(commit=False)
            reference.user = request.user
            reference.save()
            return render(request, "adverts/partials/references.html")
    else:
        form = ReferenceForm()
    context = {
        "form": form
    }
    return render(request, "adverts/partials/add_reference.html", context)


@login_required
def edit_reference(request, pk):
    reference = get_object_or_404(Reference, pk=pk)
    if request.method == "POST":
        form = ReferenceForm(request.POST, instance=reference)
        if form.is_valid():
            form.save()
            return render(request, "adverts/partials/references.html")
    else:
        form = ReferenceForm(instance=reference)
    context = {
        "reference": reference,
        "form": form
    }
    return render(request, "adverts/partials/edit_reference.html", context)


@login_required
def add_contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            return render(request, "accounts/partials/contacts.html")
    form = ContactForm()
    context = {
        "form": form,
    }
    return render(request, "accounts/partials/add_contact.html", context)
