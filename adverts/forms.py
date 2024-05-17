from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import Advert, Requirement, Department, Application, Interview, JobOfferReply, InterviewInvitation, JobOffer
from datetime import date
import numpy as np


class NewAdvertForm(forms.ModelForm):
    closing_date = forms.DateField(widget=forms.DateInput({
        "type": "date"
    }))
    # content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Advert

        fields = ["department", "title", "advert_type", "content",
                  "number_of_posts", "closing_date"]


class NewRequirementForm(forms.ModelForm):
    class Meta:
        model = Requirement
        fields = "__all__"


class NewDepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = "__all__"


class JobOfferForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(
        attrs={"rows": 3, "required": False}))
    documents = forms.FileField(label='Documents', widget=forms.FileInput(attrs={
        'class': "block w-full px-3 py-2 mt-2 text-sm text-gray-600 bg-white border border-gray-200 rounded-lg file:bg-gray-200 file:text-gray-700 file:text-sm file:px-4 file:py-1 file:border-none file:rounded-full dark:file:bg-gray-800 dark:file:text-gray-200 dark:text-gray-300 placeholder-gray-400/70 dark:placeholder-gray-500 focus:border-blue-400 focus:outline-none focus:ring focus:ring-blue-300 focus:ring-opacity-40 dark:border-gray-600 dark:bg-gray-900 dark:focus:border-blue-300"
    }))

    class Meta:
        model = JobOffer
        fields = ['body', 'documents']


class ApplicationForm(forms.ModelForm):
    BOOL_CHOICES = [(True, "Yes"), (False, 'No')]
    documents = forms.FileField(label='Documents', widget=forms.FileInput(attrs={
        'class': "block w-full px-3 py-2 mt-2 text-sm text-gray-600 bg-white border border-gray-200 rounded-lg file:bg-gray-200 file:text-gray-700 file:text-sm file:px-4 file:py-1 file:border-none file:rounded-full dark:file:bg-gray-800 dark:file:text-gray-200 dark:text-gray-300 placeholder-gray-400/70 dark:placeholder-gray-500 focus:border-blue-400 focus:outline-none focus:ring focus:ring-blue-300 focus:ring-opacity-40 dark:border-gray-600 dark:bg-gray-900 dark:focus:border-blue-300"
    }))
    comment = forms.CharField(widget=forms.Textarea(
        attrs={"rows": 3, "required": False}))

    class Meta:
        model = Application
        fields = ["documents", "comment"]


class InterviewForm(forms.ModelForm):
    interview_date = forms.DateField(widget=forms.DateInput({
        "type": "date"
    }))
    comments = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'rows': 3,
    }))

    class Meta:
        model = Interview
        fields = ("interview_date", "overall_score", "comments")

    def clean(self):
        cleaned_data = super().clean()
        interview_date = cleaned_data.get('interview_date')
        overall_score = cleaned_data.get('overall_score')

        if not np.is_busday(interview_date):
            raise forms.ValidationError(
                "The Date is not a business day, Please provide another date")
        elif interview_date > date.today():
            raise forms.ValidationError(
                "The Interview date can not be in the future, Please enter a valid interview date")
        elif overall_score > 100:
            raise forms.ValidationError(
                "The overal score cannot be over 100")


class JobOfferReplyForm(forms.ModelForm):

    class Meta:
        model = JobOfferReply
        fields = ("message", "attachment")


class InterviewInvitationForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(
        attrs={"rows": 3, "required": False}))
    date = forms.DateField(widget=forms.DateInput({
        "type": "date"
    }))

    class Meta:
        model = InterviewInvitation
        fields = ['body', 'venue', 'date']

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')

        if date < date.today():
            raise forms.ValidationError(
                "The Interview date can not be a previous date")
        elif not np.is_busday(date):
            raise forms.ValidationError(
                "The Date is not a business day, Please provide another date")
