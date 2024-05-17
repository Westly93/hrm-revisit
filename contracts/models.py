import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.core.validators import FileExtensionValidator
from phonenumber_field.modelfields import PhoneNumberField
from accounts.models import UserAccount
from adverts.models import Department

ext_validators = FileExtensionValidator(['doc', 'docx', 'pdf'])


class Contract(models.Model):
    CONTRACT_TYPES = (
        ("open", "Open"),
        ("closed", "Closed")
    )
    CONTRACT_STATUS = (
        ("pending", "Pending"),
        ("approved", "Approved")
    )
    employee = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    contract_type = models.CharField(max_length=10, choices=CONTRACT_TYPES)
    status = models.CharField(
        max_length=10, default="pending", choices=CONTRACT_STATUS)
    start_date = models.DateField()
    end_date = models.DateField()
    position = models.ForeignKey(
        "Position", on_delete=models.CASCADE, related_name="positions")
    # salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Contract for {self.employee.username}"

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"


class Position(models.Model):

    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    grade = models.OneToOneField("Grade", on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Position"
        verbose_name_plural = "Positions"
        ordering = ("-id",)


class Grade(models.Model):
    name = models.CharField(max_length=5)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Leave(models.Model):
    LEAVE_TYPES = (
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('parental', 'Parental Leave'),
        ('bereavement', 'Bereavement Leave'),
        ('personal', 'Personal Leave'),
        ('jury_duty', 'Jury Duty Leave'),
        ('military', 'Military Leave'),
        ('study', 'Study Leave'),
        ('public_holiday', 'Public Holiday'),
    )
    employee = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name="leave")
    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    address_while_on_leave = models.CharField(
        max_length=1000, null=True, blank=True)
    reason = models.TextField()
    attachment = models.FileField(
        upload_to='leave_attachments/', blank=True, null=True)

    def __str__(self):
        return f"{self.leave_type} Leave for {self.employee.username}"


class Termination(models.Model):
    employee = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    termination_date = models.DateField()
    attachment = models.FileField(
        upload_to="terminations/", blank=True, null=True)
    reason = models.TextField()

    def __str__(self):
        return f"Termination for {self.employee.username}"


class LeaveBalance(models.Model):
    employee = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    total_leave_days = models.PositiveIntegerField(default=0)
    remaining_leave_days = models.PositiveIntegerField(default=0)
    leave = models.ForeignKey(
        Leave, on_delete=models.CASCADE, related_name='leave_balances')

    def __str__(self):
        return f"Leave Balance for {self.employee.username}"


class AcademicQualification(models.Model):
    LEVEL_CHOICES = (
        ("Ordinary Level", "Ordinary Level"),
        ("Advanced Level", "Advanced Level"),
        ('Bachelor', 'Bachelor\'s Degree'),
        ('Master', 'Master\'s Degree'),
        ('PhD', 'Ph.D.'),
    )
    employee = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name="academic_qualifications")
    level = models.CharField(max_length=100, choices=LEVEL_CHOICES)
    institution = models.CharField(max_length=150)
    field_of_study = models.CharField(max_length=100)
    grade = models.CharField(max_length=255, null=True, blank=True)
    start_year = models.DateField(null=True, validators=[
        MaxValueValidator(datetime.date.today())])
    end_year = models.DateField(null=True, blank=True)
    attachment = models.FileField(
        upload_to="qualifications/",
        blank=True,
        null=True,
        validators=[ext_validators],
        help_text="Upload certificates"
    )

    def __str__(self):
        return f"{self.level} from {self.institution} for {self.employee.username}"

    def clean(self):
        if self.start_year and self.end_year and self.end_year < self.start_year:
            raise ValidationError(
                "End year cannot be earlier than the start year.")
        elif self.start_year > datetime.date.today():
            raise ValidationError(
                "You can not ennter future dates for the start date")


class Beneficiary(models.Model):
    employee = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name="beneficiaries")
    full_name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    national_id_number = models.CharField(max_length=10, unique=True)
    contact_phone = PhoneNumberField()
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"Beneficiary: {self.full_name} ({self.relationship})"


class NextOfKin(models.Model):
    employee = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name="next_of_kin")
    full_name = models.CharField(max_length=100)
    national_id_number = models.CharField(max_length=11, unique=True)
    relationship = models.CharField(max_length=50)
    contact_phone = PhoneNumberField()
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"Next of Kin: {self.full_name} ({self.relationship})"


class Spouse(models.Model):
    employee = models.OneToOneField(
        UserAccount, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    national_id_number = models.CharField(max_length=10, unique=True)
    date_of_birth = models.DateField()
    contact_phone = PhoneNumberField()
    email = models.EmailField(blank=True, null=True)
    attachment = models.FileField(
        upload_to="spouse/", blank=True, null=True)

    def __str__(self):
        return f"Spouse: {self.full_name} (Employee: {self.employee.username})"


class Children(models.Model):
    employee = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name="children")
    full_name = models.CharField(max_length=1000, unique=True)
    date_of_birth = models.DateField()
