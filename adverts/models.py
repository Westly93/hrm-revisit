import os
import datetime
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.core.validators import MinValueValidator
from ckeditor.fields import RichTextField
from phonenumber_field.modelfields import PhoneNumberField
import magic


from accounts.models import UserAccount, Reference


class Advert(models.Model):
    class Meta:
        verbose_name = "Advert"
        verbose_name_plural = "Adverts"
        ordering = ("-id",)

    STATUS_CHOICES = (
        ("published", "Published"),
        ("closed", "Closed"),
        ("pending", "Pending"),
    )
    ADVERT_TYPE_CHOICES = (
        ("Internal", "Internal"),
        ("External", "External"),
    )
    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, unique=True)
    content = RichTextField()
    advert_type = models.CharField(
        max_length=20, default="External", choices=ADVERT_TYPE_CHOICES)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="pending")
    requirements = models.ManyToManyField(
        "Requirement", related_name="requirements")
    date_created = models.DateTimeField(auto_now_add=True)
    closing_date = models.DateField(validators=[
        MinValueValidator(datetime.date.today())])
    number_of_posts = models.PositiveIntegerField(default=1)

    @property
    def is_internal(self):
        return self.advert_type == "Internal"

    def __str__(self):
        return self.title

    def has_expired(self):
        return self.closing_date < datetime.date.today()

    @property
    def is_published(self):
        return self.status == "published"


class Department(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Requirement(models.Model):
    description = models.CharField(max_length=1000)
    weight = models.IntegerField()

    def __str__(self):
        return self.description


ext_validators = FileExtensionValidator(['doc', 'pdf'])


def validate_file_mimetype(file):
    accept = ["application/pdf", "image/jpeg", "image/png"]
    file_mime_type = magic.from_buffer(file.read(1024), mime=True)
    print(file_mime_type)
    if file_mime_type not in accept:
        raise ValidationError("Unsupported file type")


def validate_file_size(value):
    limit = 2 * 1024 * 1024  # 2MB limit
    if value.size > limit:
        raise ValidationError('File size must be 2MB or less.')


class Application(models.Model):
    class StatusChoices(models.TextChoices):
        SHORTLIST = "shortlist"
        REJECT = "reject"
        INTERVIEW = 'interview'
        PENDING = 'pending'

    applicant = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    advert = models.ForeignKey(
        Advert, on_delete=models.CASCADE, related_name="applications")
    documents = models.FileField(
        blank=True, null=True,
        upload_to="applications/cover_letters/", validators=[ext_validators, validate_file_mimetype, validate_file_size])
    status = models.CharField(
        max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    requirements_met = models.ManyToManyField(
        Requirement, related_name="requirements_met")
    comment = models.TextField()
    date_applied = models.DateTimeField(default=timezone.now)

    @property
    def document_extension(self):
        _, extension = os.path.splitext(self.documents.name)
        return extension

    @property
    def resume_extension(self):
        _, extension = os.path.splitext(self.resume.name)
        return extension

    def __str__(self):
        return self.advert.title


""" 
def custom_file_extension_validator(value):
    validate_file_extension(value, ['pdf', 'doc', 'docx']) """


class Reference(models.Model):
    INITIAL_CHOICES = (
        ("Mr", "Mr"),
        ("Mrs", "Mrs"),
        ("Miss", "Miss"),
        ("Dr", "Dr"),
    )
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="references")
    initial = models.CharField(max_length=5, choices=INITIAL_CHOICES)
    full_name = models.CharField(max_length=1000)
    email = models.EmailField()
    contact_phone = PhoneNumberField()
    organization = models.CharField(max_length=1000)
    position = models.CharField(max_length=1000)

    def __str__(self):
        return self.full_name


class JobOffer(models.Model):
    advert = models.ForeignKey(Advert, on_delete=models.CASCADE)
    application = models.ForeignKey(
        "Application", on_delete=models.SET_NULL, null=True,  related_name="job_offer")
    offer_date = models.DateTimeField(auto_now_add=True)
    body = models.TextField(null=True, blank=True)
    documents = models.FileField(
        blank=True, null=True,
        upload_to="applications/job_offer/", validators=[ext_validators, validate_file_mimetype, validate_file_size])

    def __str__(self):
        return f"Job Offer for {self.application.applicant.email} - {self.advert.title}"


class EmailReferee(models.Model):
    application_id = models.IntegerField(null=True)
    referee_id = models.IntegerField(null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application.applicant.profile.first_name} {self.application.applicant.profile.surname} - {self.referee.full_name}"


class InterviewInvitation(models.Model):
    advert = models.ForeignKey(
        Advert, on_delete=models.CASCADE, related_name="interview_invitation")
    body = models.TextField(null=True, blank=True)
    candidate = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name="candidate_invited")
    venue = models.CharField(max_length=1000)
    date = models.DateTimeField()

    def __str__(self):
        return f"Interview Invitation for {self.advert.title}"


class JobOfferReply(models.Model):
    job_offer = models.OneToOneField(
        "JobOffer", on_delete=models.CASCADE, related_name='job_offer_reply')

    message = models.CharField(max_length=1000, blank=True, null=True)
    attachment = models.FileField()
    reply_date = models.DateTimeField(default=timezone.now)


class Interview(models.Model):
    candidate = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name="candidate")
    interview_date = models.DateField()
    job = models.ForeignKey(
        Advert, on_delete=models.SET_NULL, null=True, related_name="job_post")
    interviewer = models.ForeignKey(
        UserAccount, on_delete=models.SET_NULL, null=True, blank=True)
    comments = models.TextField(blank=True)
    overall_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    offered_job = models.BooleanField(default=False)

    def __str__(self):
        return f"Interview for {self.candidate.username} on {self.interview_date}"
