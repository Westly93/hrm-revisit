from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django_countries.fields import CountryField
from django.db import models
from datetime import date, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_resized import ResizedImageField
from phonenumber_field.modelfields import PhoneNumberField


class UserAccountManager(BaseUserManager):
    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have email")
        if not password:
            raise ValueError("users must have password")

        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        extra_fields.setdefault("is_superuser", True)
        user.is_active = True
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email")
        if not password:
            raise ValueError("Users must have a password")

        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.save()
        return user


class UserAccount(AbstractBaseUser):

    email = models.EmailField(max_length=255, unique=True)
    # username = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    objects = UserAccountManager()

    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ["email"]

    @property
    def full_name(self):
        return f"{self.profile.first_name} {self.profile.surname}"

    def is_male(self):
        if self.profile.gender == "male":
            return True
        else:
            return False

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def __str__(self):
        return self.email


national_id_regex = r'^\d{8}[A-Za-z]\d{2}$'
national_id_validator = RegexValidator(
    national_id_regex,
    'Enter a valid national ID. The format should be 8 digits followed by a letter and then 2 digits.'
)


def validate_age_range(value):
    min_age = 18
    max_age = 65
    today = date.today()
    min_date = today - timedelta(days=(max_age * 365.25))
    max_date = today - timedelta(days=(min_age * 365.25))
    if not (min_date <= value <= max_date):
        raise ValidationError(
            f"Age must be between {min_age} and {max_age} years.")


class Profile(models.Model):
    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    )
    MARITAL_STATUS_CHOICES = (
        ("single", "Single"),
        ("married", "Married"),
        ("devorced", "Devorced"),
    )
    bio = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    surname = models.CharField(max_length=255, null=True, blank=True)
    dob = models.DateField(blank=True, null=True,
                           validators=[validate_age_range])
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    marital_status = models.CharField(
        max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True, null=True)
    user = models.OneToOneField(
        UserAccount, on_delete=models.CASCADE, related_name="profile"
    )
    address = models.CharField(max_length=1000, null=True, blank=True)
    nationality = CountryField(blank=True, null=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    national_id = models.CharField(
        max_length=11,
        null=True,
        blank=True,
        unique=True,
        validators=[national_id_validator]
    )
    thumbnail = ResizedImageField(
        size=[200, 200], quality=100, upload_to="authSystem", default="default.jpg"
    )

    @property
    def age(self):
        today = date.today()
        try:
            birthday = self.dob.replace(year=today.year)
        except ValueError:  # raised when birth date is February 29 and the current year is not a leap year
            birthday = self.dob.replace(year=today.year, day=self.dob.day - 1)
        if birthday > today:
            return today.year - self.dob.year - 1
        else:
            return today.year - self.dob.year

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"{self.user.email}'s Profile"

    def get_profile_completion(self):
        total_weight = 0
        filled_weight = 0

        # Define the fields that contribute to profile completion with their respective weights
        profile_fields = [
            (self.bio, 2),
            (self.city, 2),
            (self.first_name, 2),
            (self.surname, 2),
            (self.gender, 1),
            (self.marital_status, 1),
            (self.address, 3),
            (self.nationality, 2),
            (self.city, 2),
            (self.national_id, 2),
            (self.thumbnail, 2),
            (self.bio, 2),

        ]

        # Calculate the total weight and filled weight
        for field, weight in profile_fields:
            total_weight += weight
            if field:
                filled_weight += weight

        if self.user.references.exists():
            total_weight += 5
            filled_weight += 5
        else:
            total_weight += 5

        if self.user.experience.exists():
            total_weight += 5
            filled_weight += 5
        else:
            total_weight += 5

        if self.user.academic_qualifications.exists():
            total_weight += 5
            filled_weight += 5
        else:
            total_weight += 5

        if self.user.contacts.exists():
            total_weight += 5
            filled_weight += 5
        else:
            total_weight += 5
        # Calculate the profile completion percentage
        if total_weight > 0:
            completion_percentage = (filled_weight / total_weight) * 100
        else:
            completion_percentage = 0

        return round(completion_percentage, 2)


class Contact(models.Model):
    user = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name="contacts")
    contact_phone = PhoneNumberField(unique=True)

    def __str__(self):
        return self.contact_phone


class Experience(models.Model):
    user = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name="experience")
    job_title = models.CharField(max_length=100)
    company = models.CharField(max_length=150)
    location = models.CharField(max_length=1000, null=True, blank=True)
    currently_working_in_this_role = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    start_year = models.DateField(validators=[
        MaxValueValidator(date.today())])
    end_year = models.DateField(null=True, blank=True)

    def clean(self):
        if self.start_year and self.end_year and self.end_year < self.start_year:
            raise ValidationError(
                "End year cannot be earlier than the start year.")
        elif self.start_year > date.today():
            raise ValidationError(
                "You can not ennter future dates for the start date")


class Reference(models.Model):
    INITIAL_CHOICES = (
        ("Mr", "Mr"),
        ("Mrs", "Mrs"),
        ("Miss", "Miss"),
        ("Dr", "Dr"),
    )
    user = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name="references")
    initial = models.CharField(max_length=5, choices=INITIAL_CHOICES)
    full_name = models.CharField(max_length=1000)
    email = models.EmailField()
    contact_phone = PhoneNumberField()
    organization = models.CharField(max_length=1000)
    position = models.CharField(max_length=1000)

    def __str__(self):
        return self.full_name


@receiver(post_save, sender=UserAccount)
def create_profile(sender, created, instance, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=UserAccount)
def save_profile(sender, instance, *args, **kwargs):
    instance.profile.save()
