from django.contrib import admin
from import_export.fields import Field
from import_export import resources

from .models import Advert, Department, Requirement, Application
# Register your models here.


class SummaryTableResource(resources.ModelResource):
    applicant__profile__first_name = Field(
        attribute='applicant__profile__first_name', column_name='First Name')
    applicant__profile__surname = Field(
        attribute='applicant__profile__surname', column_name='Last Name')
    applicant__academic_qualifications = Field(
        attribute='applicant__academic_qualifications', column_name='Qualifications')
    applicant__experience = Field(
        attribute="applicant__experience", column_name="Experience")
    applicant__references = Field(
        attribute="applicant__references", column_name="References")
    applicant__contacts = Field(
        attribute="applicant__contacts", column_name="Contacts")
    date_applied = Field()

    class Meta:
        model = Application
        fields = ('applicant__profile__first_name', 'applicant__profile__surname', "applicant__contacts",
                  'applicant__academic_qualifications', "applicant__experience", "applicant__references", "date_applied")

    def dehydrate_applicant__experience(self, obj):
        experience = [x.job_title for x in obj.applicant.experience.all()]
        return ", ".join(experience)

    def dehydrate_applicant__contacts(self, obj):
        contacts = [f'{x.contact_phone}' for x in obj.applicant.contacts.all()]
        return ", ".join(contacts)

    def dehydrate_applicant__academic_qualifications(self, obj):
        qualifications = [
            f'{x.level} - {x.grade}' for x in obj.applicant.academic_qualifications.all()]
        return ", ".join(qualifications)

    def dehydrate_applicant__references(self, obj):
        references = [
            f'{x.full_name} - {x.organization} - {x.position} - {x.email} - {x.contact_phone}' for x in obj.applicant.references.all()]
        return ", ".join(references)

    def dehydrate_date_applied(self, obj):
        return obj.date_applied.strftime("%d-%m-%Y")


admin.site.register(Department)
admin.site.register(Advert)
admin.site.register(Application)
admin.site.register(Requirement)
