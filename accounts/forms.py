from django import forms
from django.contrib.auth import get_user_model
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django_countries.widgets import CountrySelectWidget
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm

from .models import Profile, UserAccount, Experience, Reference, Contact


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'block w-full px-4 py-2 text-gray-700 bg-white border rounded-lg dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600 focus:border-blue-400 focus:ring-opacity-40 dark:focus:border-blue-300 focus:outline-none focus:ring focus:ring-blue-300'}
    ))

    class Meta:
        model = UserAccount
        fields = ["email", "password1", "password2"]


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = UserAccount
        fields = ["email"]


class ProfileUpdateForm(forms.ModelForm):
    bio = forms.CharField(widget=forms.Textarea(
        attrs={"rows": 3, "placeholder": "Description about yourself", "required": False}))
    dob = forms.DateField(widget=forms.DateInput({
        "type": "date"
    }))
    national_id = forms.CharField(widget=forms.TextInput(
        attrs={"placeholder": "05121587Y05"}
    ))
    address = forms.CharField(widget=forms.TextInput(
        attrs={"placeholder": "3155 Wood Broke North "}
    ))
    city = forms.CharField(widget=forms.TextInput(
        attrs={"placeholder": "Bindura"}
    ))
    first_name = forms.CharField(widget=forms.TextInput(
        attrs={"placeholder": "John"}
    ))
    surname = forms.CharField(widget=forms.TextInput(
        attrs={"placeholder": "Doe"}
    ))
    thumbnail = forms.FileField(label='Thumbnail', widget=forms.FileInput(attrs={
        'class': "block w-full px-3 py-2 mt-2 text-sm text-gray-600 bg-white border border-gray-200 rounded-lg file:bg-gray-200 file:text-gray-700 file:text-sm file:px-4 file:py-1 file:border-none file:rounded-full dark:file:bg-gray-800 dark:file:text-gray-200 dark:text-gray-300 placeholder-gray-400/70 dark:placeholder-gray-500 focus:border-blue-400 focus:outline-none focus:ring focus:ring-blue-300 focus:ring-opacity-40 dark:border-gray-600 dark:bg-gray-900 dark:focus:border-blue-300"
    }))

    class Meta:
        model = Profile
        fields = ["first_name", "surname", "dob", "national_id", "gender",
                  "marital_status", "bio", "address", "city", "nationality", "thumbnail"]
        widgets = {"nationality": CountrySelectWidget()}


class CustomPasswordChangeForm(PasswordChangeForm):
    pass


class ExperienceForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(
        attrs={"rows": 3, "placeholder": "Roles and responsibilities"}))
    start_year = forms.DateField(widget=forms.DateInput({
        "type": "date"
    },
    ))
    end_year = forms.DateField(required=False, widget=forms.DateInput({
        "type": "date", "required": False
    }))

    class Meta:
        model = Experience
        fields = ("job_title", "company", "location",
                  "currently_working_in_this_role", "description", "start_year", "end_year")


class ReferenceForm(forms.ModelForm):
    contact_phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(
            initial="ZW",
            attrs={'class': 'text-sm rounded-md w-full mb-5'},
        ),

    )

    class Meta:
        model = Reference
        fields = ("initial", "full_name", "organization",
                  "position", "contact_phone", "email")


class ContactForm(forms.ModelForm):
    contact_phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(
            initial="ZW",
            attrs={'class': 'rounded-md w-full mb-5'},
        ),

    )

    class Meta:
        model = Contact
        fields = ("contact_phone",)


class AccountActivationForm(forms.Form):
    email = forms.EmailField(label="Email Address")

    def clean_email(self):
        email = self.cleaned_data['email']
        user = get_user_model().objects.filter(email=email).first()
        print(user)
        if not user:
            raise forms.ValidationError(
                'No User with that email, Please provide another email')
        elif user.is_active:
            raise forms.ValidationError(
                'The account is already active, Please go on to login')
        return email
