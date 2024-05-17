from django import forms
from django.utils import timezone
from django.forms.widgets import SelectDateWidget
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from .models import (
    Contract, Leave, Position,
    AcademicQualification, Beneficiary, NextOfKin, Spouse,
    Children
)
from datetime import date


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = "__all__"


class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ["leave_type", "address_while_on_leave",
                  "reason", "start_date", "end_date", "attachment"]


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = "__all__"


class AcademicQualificationForm(forms.ModelForm):
    attachment = forms.FileField(
        required=False,
        help_text='Upload Academic Qualifications (max size: 2MB)',
        widget=forms.ClearableFileInput(attrs={'class': 'w-full border rounded-md border-gray-900 p-1'}))
    start_year = forms.DateField(widget=forms.DateInput({
        "type": "date"
    }))
    end_year = forms.DateField(required=False, widget=forms.DateInput({
        "type": "date"
    }))
    field_of_study = forms.CharField(
        max_length=1000,
        widget=forms.TextInput(attrs={'placeholder': 'Computer Science'})
    )
    institution = forms.CharField(
        max_length=1000,
        widget=forms.TextInput(
            attrs={'placeholder': 'Midlands State University'})
    )
    grade = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={'placeholder': '2.1'})
    )

    class Meta:
        model = AcademicQualification
        fields = ["level", "institution", "field_of_study", "grade",
                  "start_year", "end_year", "attachment"]

    def clean(self):
        cleaned_data = super().clean()
        start_year = cleaned_data.get('start_year')
        end_year = cleaned_data.get('end_year')

        if start_year and end_year and start_year > end_year:
            raise forms.ValidationError(
                "Start year cannot be greater than the end year.")


def validate_date_range(value):
    if value and value > date.today():
        raise forms.ValidationError("End year cannot be in the future.")


class BeneficiaryForm(forms.ModelForm):
    contact_phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(
            initial="ZW",
            attrs={'class': 'text-sm text-gray-50 rounded-md w-full mb-5'},
        ),

    )
    date_of_birth = forms.DateField(widget=forms.DateInput({
        "type": "date"
    }))

    class Meta:
        model = Beneficiary
        fields = ["full_name", "relationship", "date_of_birth",
                  "national_id_number", "contact_phone", "email"]


class SpouseForm(forms.ModelForm):
    contact_phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(
            initial="ZW",
            attrs={
                'class': 'text-sm text-gray-50 rounded-md w-full mb-5 border border-gray-900'},
        ),

    )
    attachment = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'w-full border rounded-md border-gray-900 p-1'}))

    date_of_birth = forms.DateField(widget=forms.DateInput({
        "type": "date"
    }))

    class Meta:
        model = Spouse
        fields = ["full_name", "national_id_number",
                  "date_of_birth", "contact_phone", "email", "attachment"]


class NextOfKinForm(forms.ModelForm):
    contact_phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(
            initial="ZW"
        ),
    )

    class Meta:
        model = NextOfKin
        fields = ["full_name", "national_id_number",
                  "relationship", "contact_phone", "email"]


class ChildrenForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput({
        "type": "date"
    }))

    class Meta:
        model = Children
        fields = ['full_name', "date_of_birth"]
