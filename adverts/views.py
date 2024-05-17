from __future__ import unicode_literals
import os
import datetime
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import HttpResponse, HttpResponseForbidden
from .admin import SummaryTableResource
from django.db.models import F
# from django_countries import Countries
from .models import Advert, Department, Requirement, Application, Interview, InterviewInvitation, JobOffer, EmailReferee
from .forms import (NewAdvertForm, NewDepartmentForm, NewRequirementForm,
                    InterviewForm, JobOfferReplyForm, ApplicationForm, InterviewInvitationForm,
                    JobOfferForm
                    )
from django.views.generic import ListView
from django.views import View
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .utils import send_email, send_html_email
from accounts.forms import ExperienceForm, ReferenceForm
from accounts.models import Experience, Reference
from contracts.models import AcademicQualification
from contracts.forms import AcademicQualificationForm
from .utils import generate_job_offer_pdf
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage
from formtools.wizard.views import SessionWizardView
from accounts.decorators import is_admin, is_active
from django.urls import reverse
import pdfkit
# Create your views here.


def show_references_form(wizard):
    references = Reference.objects.filter(user=wizard.request.user)
    num_references = references.count()
    return num_references < 3


class ApplyingWizardView(SessionWizardView):
    file_storage = FileSystemStorage(
        location=os.path.join(settings.MEDIA_ROOT, 'tmp'))
    form_list = [ApplicationForm]
    template_name = "adverts/application_references.html"

    def done(self, *form_list, **kwargs):
        id = self.kwargs['id']
        advert = get_object_or_404(Advert, pk=id)
        return HttpResponse("Form Submitted!")


@is_admin
def send_job_offer(request, id, pk):
    application = get_object_or_404(Application, pk=pk)
    advert = get_object_or_404(Advert, pk=id)
    if request.method == 'POST':
        form = JobOfferForm(request.POST, request.FILES)
        if form.is_valid():
            body = form.cleaned_data['body']
            subject = f"Job Offer: {advert.title} at Midlands State University"
            reciepient_mail = application.applicant.email
            try:

                job_offer = form.save(commit=False)
                job_offer.advert = advert
                job_offer.application = application
                job_offer.save()

                html_message = render_to_string(
                    'adverts/job_offer_email.html', {"body": body, "job_offer": job_offer, "protocol": 'https' if request.is_secure() else 'http', 'domain': get_current_site(request).domain, })
                send_html_email(subject, html_message, [reciepient_mail])
                messages.success(
                    request, f"The job offer email has been send to {reciepient_mail} for the job post {advert.title}")
            except:
                messages.error(
                    request, f"Failed to send job offer to {reciepient_mail} for the job post {advert.title}")
            return redirect('adverts:application_detail', id=id, pk=pk)
    else:
        form = JobOfferForm()
    context = {
        "form": form,
        "advert": advert,
        "application": application
    }
    return render(request, 'adverts/job_offer.html', context)


def pdf_summary_table(request, pk):
    advert = get_object_or_404(Advert, pk=pk)

    context = {
        'advert': advert
    }
    return render(request, "adverts/pdf_summary_table.html", context)


@is_admin
def generateSummaryTablePDF(request, pk):
    config = pdfkit.configuration(
        wkhtmltopdf=r"C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
    advert = get_object_or_404(Advert, pk=pk)
    pdf = pdfkit.from_url(request.build_absolute_uri(
        reverse('adverts:pdf_summary_table', args=[pk])), False, configuration=config)
    response = HttpResponse(pdf, content_type="application/pdf")
    response['Content-disposition'] = f'attachment; filename= "{advert.title}_summary_table.pdf"'
    return response


@is_admin
def send_email_to_referee(request, id, pk, referee_id):
    application = get_object_or_404(Application, pk=pk)
    advert = get_object_or_404(Advert, pk=id)
    referee = get_object_or_404(Reference, pk=referee_id)
    subject = f"Request for Recommendation - {application.applicant.profile.first_name} {application.applicant.profile.surname} for {advert.title} at Midlands State University"
    body = f'''

        Dear {referee.full_name},

        I hope this email finds you well. I am writing to you because {application.applicant.profile.first_name} {application.applicant.profile.surname} has applied for the {advert.title} position at Midlands State University, and they have provided your name as a professional reference.

        We are currently evaluating {application.applicant.profile.first_name} {application.applicant.profile.surname}'s application, and your input would be invaluable in helping us make an informed decision. As someone who has worked with {application.applicant.profile.first_name} {application.applicant.profile.surname} in the past, your insights and recommendations would provide us with a deeper understanding of their qualifications, strengths, and potential fit for this role.

        We would greatly appreciate it if you could take the time to provide a brief recommendation, addressing the following areas:

        1. Nature and duration of your relationship with the candidate.
        2. The candidate's key skills, abilities, and accomplishments relevant to the {advert.title} role.
        3. The candidate's work ethic, problem-solving skills, and ability to work effectively in a team.
        4. Any other relevant information that you believe would be helpful in our evaluation of the candidate.

        Please feel free to provide your recommendation in the body of this email or as a separate attachment. We would kindly request that you submit your response by {datetime.date.today() + datetime.timedelta(14)}.

        Thank you in advance for your time and consideration. If you have any questions or need additional information, please don't hesitate to reach out.

        Best regards,
        Mufudza Weston
        Human Resource Manager
        Midlands State University
        0785136429
    '''
    try:
        send_email(subject, body, referee.email)
        EmailReferee.objects.create(application_id=pk, referee_id=referee_id)
        messages.success(
            request, f"The Email has been send to the referee {referee.email}")
    except:
        messages.success(
            request, f"Oops something went wrong, Failed to send the email try again")
    return redirect('adverts:application_detail', id=id, pk=pk)


@is_admin
@require_http_methods(["DELETE"])
def delete_advert_requirement(request, id, pk):
    advert = get_object_or_404(Advert, pk=id)
    requirement = get_object_or_404(Requirement, pk=pk)

    advert.requirements.remove(requirement)
    messages.error(request, "Requirement Removed successfully")

    return render(request, "adverts/partials/requirement.html")


@is_admin
def interview_invite(request, id, pk):
    advert = get_object_or_404(Advert, pk=id)
    application = get_object_or_404(Application, pk=pk)

    if request.method == "POST":
        form = InterviewInvitationForm(request.POST)
        if form.is_valid():
            venue = form.cleaned_data['venue']
            body = form.cleaned_data['body']
            date = form.cleaned_data['date']
            subject = f"Invitation to Interview at Midlands State University: {advert.title}"
            message = f"{body}\n On {date}\n Venue {venue}"
            subject = f"Interview invitation of the {advert.title} Job post"
            reciepient_mail = application.applicant.email
            try:
                send_email(subject, message, reciepient_mail)
                application.status = "interview"
                application.save()
                InterviewInvitation.objects.create(
                    advert=advert, candidate=application.applicant,
                    body=body, date=date, venue=venue
                )
                messages.success(
                    request, f"The email was send to {application.applicant.email}")
            except:
                messages.error(
                    request, f"Ooops something went wrong failed to send the email to {application.applicant.email}")
            return redirect('adverts:application_detail', id=id, pk=pk)
    else:
        form = InterviewInvitationForm()
    context = {
        "advert": advert,
        "form": form,
        "application": application
    }
    return render(request, "adverts/interview_invite.html", context)


@is_admin
def interview_mark(request, id, pk):
    advert = get_object_or_404(Advert, pk=id)
    application = get_object_or_404(Application, pk=pk)
    interview_score = Interview.objects.filter(
        job_post=advert, candidate=application.applicant).first()
    return render(request, "adverts/partials/interview-mark.html", {"interview_score": interview_score})


@login_required
def interview(request, id, pk):
    advert = get_object_or_404(Advert, pk=id)
    application = get_object_or_404(Application, pk=pk)
    interview = Interview.objects.filter(
        candidate=application.applicant, job=advert)
    if not request.user.is_staff:
        return HttpResponseForbidden()
    mark_recorded = False
    if interview:
        mark_recorded = True
    else:
        if request.method == "POST":
            form = InterviewForm(request.POST, request.FILES)
            if form.is_valid():
                interview_score = form.save(commit=False)
                interview_score.candidate = application.applicant
                interview_score.interviewer = request.user
                interview_score.job = advert
                interview_score.save()
                application.status = "interview_score"
                application.save()
                messages.success(request, "The score is added successfully")
                return redirect('adverts:application_detail', id=id, pk=pk)
        else:
            form = InterviewForm()
    context = {
        "form": form,
        "advert": advert,
        "application": application,
        "mark_recorded": mark_recorded
    }
    return render(request, "adverts/interview-score.html", context)


@login_required
def advert_preview(request, id):
    advert = get_object_or_404(Advert, pk=id)
    """ if not request.user.is_staff and not request.user.is_admin:
        return HttpResponseForbidden() """
    return render(request, "adverts/advert_preview.html", {"advert": advert})


@login_required
def publish_advert(request, id):
    advert = get_object_or_404(Advert, pk=id)
    """ if not request.user.is_admin:
        return HttpResponseForbidden() """
    advert.status = "published"
    advert.save()
    messages.success(request, "The advert is published successfully")
    return redirect("adverts:adverts")


@login_required
@require_http_methods(["POST"])
def add_advert_requirements(request, id):
    advert = get_object_or_404(Advert, pk=id)
    """ if not request.user.is_staff:
        return HttpResponseForbidden() """
    requirement = None
    description = request.POST.get("description")
    weight = request.POST.get("weight")

    if description and weight:
        requirement = Requirement.objects.create(
            description=description, weight=weight)
        advert.requirements.add(requirement)
        messages.success(request, "Requirement added successfully")
    return render(request, "adverts/partials/requirement.html", {"advert": advert})


@login_required
def advert_requirements(request, id):
    advert = get_object_or_404(Advert, pk=id)
    """ if not request.user.is_staff and not request.user.is_admin:
        return HttpResponseForbidden() """
    return render(request, "adverts/advert_requirements.html", {"advert": advert})


class NewApplication(View):
    @method_decorator(is_active)
    def get(self, request, id, *args, **kwargs):
        if request.user.profile.get_profile_completion() < 75 or request.user.references.count() < 3:
            messages.error(
                request, 'Please Note that your profile should be over 75% and provide at lease 3 references')
            return redirect("accounts:dashboard")
        advert = get_object_or_404(Advert, pk=id)
        form = ApplicationForm()
        context = {
            "form": form,
            "advert": advert
        }
        return render(request, "adverts/apply.html", context)

    @method_decorator(is_active)
    def post(self, request, id, *args, **kwargs):
        advert = get_object_or_404(Advert, pk=id)
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                subject = "Congratulations on Your Successful Job Application at Midlands State University!!"
                html_message = render_to_string(
                    'adverts/application_success_email.html', {"protocol": 'https' if request.is_secure() else 'http', 'domain': get_current_site(request).domain})
                send_html_email(subject, html_message, [request.user.email])
                application = form.save(commit=False)
                application.applicant = request.user
                application.advert = advert
                application.save()

                messages.success(
                    request, "Your application was submitted successfully!")
            except:
                messages.error(
                    request, "Failed to send your application please try again!")
            return redirect('adverts:requirements_met', advert.id, application.id)
        context = {
            "form": form,
            "advert": advert
        }
        return render(request, "adverts/apply.html", context)


# adverts functionality


@is_active
def requirements_met(request, id, pk):
    advert = get_object_or_404(Advert, pk=id)
    application = get_object_or_404(Application, pk=pk)

    if request.method == "POST":
        requirements = request.POST.getlist("requirements")
        for requirement in advert.requirements.all():
            for req in requirements:
                if requirement.id == int(req):
                    application.requirements_met.add(requirement)

        if len(requirements) == len(advert.requirements.all()):
            application.status = "shortlisted"
            application.save()
            messages.success(request, "Application submitted successfully")
        return redirect("adverts:applied_jobs")

    return render(request, "adverts/requirements_met.html", {"advert": advert})


@is_admin
def application_detail(request, id, pk):
    advert = get_object_or_404(Advert, pk=id)
    """ if not request.user.is_staff:
        return HttpResponseForbidden() """
    form = InterviewForm()
    application = get_object_or_404(Application, pk=pk)
    email_referees = [referee.referee_id for referee in EmailReferee.objects.filter(
        application_id=application.id).all()]
    if not application in advert.applications.all():
        return HttpResponse("There is no such application for this adevert")
    interview = Interview.objects.filter(
        job=advert, candidate=application.applicant).first()
    is_recorded = False
    if interview:
        is_recorded = True

    context = {
        "application": application,
        "advert": advert,
        "interview": interview,
        "form": form,
        "is_recorded": is_recorded,
        "email_referees": email_referees
    }
    return render(request, "adverts/application_detail.html", context)


@is_admin
def advert_delete(request, id):
    advert = get_object_or_404(Advert, pk=id)
    if not request.user.is_admin:
        return HttpResponseForbidden()
    advert.delete()
    adverts = Advert.objects.all()
    context = {
        "adverts": adverts
    }
    messages.success(request, "Advert deleted successfully!")
    return render(request, "adverts/partials/adverts.html", context)


@login_required
def advert_detail(request, id):
    advert = get_object_or_404(Advert, pk=id)
    user = request.user
    application = Application.objects.filter(
        advert=advert, applicant=user).first()
    if application:
        has_applied = True
    else:
        has_applied = False
    context = {
        "advert": advert,
        "has_applied": has_applied
    }
    return render(request, "adverts/advert_detail.html", context)


@is_admin
def edit_advert(request, id):
    advert = get_object_or_404(Advert, pk=id)
    if request.method == 'POST':
        form = NewAdvertForm(request.POST, instance=advert)
        if form.is_valid():
            form.save()
            messages.success(request, "Advert is updated successfully")
            return redirect("adverts:advert_detail", id=advert.id)
    form = NewAdvertForm(instance=advert)
    context = {
        "form": form,
        "button_text": "Update",
        "legend": f"Update Advert '{advert.title}'"
    }
    return render(request, "adverts/new_advert.html", context)


class AdvertListView(ListView):
    model = Advert
    template_name = 'adverts/main.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'adverts'
    ordering = ['-date_created']
    paginate_by = 5

    def get_queryset(self):
        if self.request.user.is_staff and self.request.user.is_admin:
            return Advert.objects.all()
        elif self.request.user.is_staff:
            return Advert.objects.filter(advert_type="Internal").all()
        return Advert.objects.filter(advert_type="External").all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Jobs"
        context['department_names'] = Department.objects.values_list(
            'name', flat=True)
        return context


def filter_adverts(request):
    department_name = request.GET.get("department_name")
    if request.user.is_staff:
        adverts = Advert.objects.filter(
            advert_type="Internal", department__name=department_name
        )
    else:
        adverts = Advert.objects.filter(
            advert_type="External", department__name=department_name
        )
    return render(request, "adverts/partials/adverts.html", {"adverts": adverts})


""" def adverts(request):
    adverts = Advert.objects.all()
    department_names = Department.objects.values_list('name', flat=True)
    page = request.GET.get('page', 1)
    paginator = Paginator(adverts, page)
    adverts = paginator.page(paginator.num_pages)
    context = {
        "adverts": adverts,
        "title": "Jobs",
        "department_names": department_names
    }
    if request.htmx:
        department_name = request.GET.get("department_name")
        adverts = Advert.objects.filter(department__name=department_name)
        return render(request, "adverts/partials/adverts.html", {"adverts": adverts})
    return render(request, "adverts/main.html", context)
 """


def search_adverts(request):
    query = request.GET.get('advert_title')
    adverts = Advert.objects.filter(title__icontains=query)
    # print("You typed something hey")
    return render(request, "adverts/partials/adverts.html", {"adverts": adverts})


@login_required
def applied_jobs(request):
    user = request.user
    adverts = Advert.objects.filter(applications__applicant=user)
    return render(request, "adverts/applied_jobs.html", {"adverts": adverts})


class NewAdvert(View):
    @method_decorator(is_admin)
    def get(self, request, *args, **kwargs):
        form = NewAdvertForm()
        context = {
            "form": form,
            "button_text": "Save & Next",
            "legend": "Create New Advert"
        }
        return render(request, "adverts/new_advert.html", context)

    @method_decorator(is_admin)
    def post(self, request, *args, **kwargs):
        form = NewAdvertForm(request.POST, request.FILES)
        if form.is_valid():
            advert = form.save()
            messages.success(request, "the advert is created successfully")
            return redirect("adverts:advert_requirements", advert.id)
        else:
            messages.error(request, "Invalid form submission!!")
        context = {
            "form": form,
            "button_text": "Save & Next",
            "legend": "Create New Advert"
        }
        return render(request, "adverts/new_advert.html", context)


# requirement functionality


@login_required
def requirement_delete(request, id, pk):
    advert = get_object_or_404(Advert, pk=id)
    requirement = get_object_or_404(Requirement, pk=pk)
    if not request.user.is_staff:
        return HttpResponseForbidden()
    advert.requirements.remove(requirement)
    requirement.delete()
    context = {
        "advert": advert,
    }
    return render(request, "adverts/partials/requirement.html", context)


@login_required
def edit_requirement(request, id, pk):
    advert = get_object_or_404(Advert, pk=id)
    requirement = get_object_or_404(Requirement, pk=pk)
    if not request.user.is_staff:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = NewRequirementForm(request.POST, instance=requirement)
        if form.is_valid():
            form.save()
            messages.success(request, "requirement is updated successfully")
            return render(request, "adverts/partials/requirement.html", {"advert": advert})
    form = NewRequirementForm(instance=requirement)
    context = {
        "form": form,

    }
    return render(request, "adverts/partials/edit_requirement.html", context)


@is_admin
def new_requirement(request):
    if request.method == "POST":
        form = NewAdvertForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, "The requirement is created successfully")
            return redirect("adverts:adverts")
    form = NewRequirementForm()
    context = {
        "form": form
    }
    return render(request, "adverts/new_requirement.html", context)

# department functionality


@is_admin
def department_delete(request, id):
    department = get_object_or_404(Department, pk=id)
    if not request.user.is_staff:
        return HttpResponseForbidden()
    department.delete()
    return HttpResponse("Department is successfully Deleted ")


@is_admin
def edit_department(request, id):
    department = get_object_or_404(Department, pk=id)
    if not request.user.is_staff:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = NewDepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, "Advert is updated successfully")
            return redirect("adverts:advert_detail", id=department.id)
    form = NewDepartmentForm(instance=department)
    context = {
        "form": form,
    }
    return render(request, "adverts/new_department.html", context)


@is_admin
def new_department(request):
    if request.method == "POST":
        form = NewDepartmentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, "You have successfully created the department")
            return redirect("adverts:new_advert")

    form = NewDepartmentForm()

    context = {
        "form": form
    }

    return render(request, "adverts/new_department.html", context)


@is_admin
def applications(request, id):
    """ if not request.user.is_staff:
        return HttpResponseForbidden() """
    advert = get_object_or_404(Advert, pk=id)
    statuses = Application.StatusChoices.values
    # print(statuses)

    applications = advert.applications.all()
    if request.htmx:
        status = request.GET.get("status")

        if status == '':
            applications = advert.applications.all()
        else:
            applications = Application.objects.filter(status=status)
        context = {
            "advert": advert,
            "applications": applications,
            "selected_status": status,
            "statuses": statuses,
        }
        return render(request, "adverts/partials/application.html", context)
    context = {
        "advert": advert,
        "applications": applications,
        "statuses": statuses,
    }
    return render(request, "adverts/applications.html", context)


def update_application_status(request, id, pk):
    advert = get_object_or_404(Advert, pk=id)
    application = get_object_or_404(Application, pk=pk)
    status = request.GET.get('status')
    statuses = Application.StatusChoices.values

    application.status = status
    application.save()
    return render(request, "adverts/partials/application.html", {
        "applications": advert.applications.all(),
        "advert": advert,
        "statuses": statuses
    })


@is_admin
def interview_scores(request, id):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    advert = get_object_or_404(Advert, pk=id)
    interview_scores = Interview.objects.filter(job=advert)
    context = {
        'advert': advert,
        "interview_scores": interview_scores
    }
    return render(request, "adverts/interview_scores.html", context)


@is_admin
def application_interview_score(request, id, pk):
    advert = get_object_or_404(Advert, pk=id)
    application = get_object_or_404(Application, pk=pk)
    interview_mark = Interview.objects.filter(
        job=advert, candidate=application.applicant).first()
    # print(interview_mark)
    context = {
        "interview_mark": interview_mark,
    }
    return render(request, 'adverts/partials/interview-mark.html', context)


@login_required
def application_feedback(request, id):
    advert = get_object_or_404(Advert, pk=id)
    user = request.user
    application = Application.objects.filter(
        applicant=user, advert=advert).first()
    if application:
        if application.status == "shorlisted":
            return HttpResponse("Congratulations you have been shortlisted")
        elif application.status == "interview_invite":
            interview = Interview.objects.filter(
                job=advert, candidate=application.applicant).first()
            if interview:
                if interview.offered_job:
                    job_offer = JobOffer.objects.filter(
                        advert=advert, interview=interview).first()
                context = {
                    "interview": interview,
                    "advert": advert,

                }
                return render(request, "adverts/application_feedback.html", context)
            else:
                interview_invitation = InterviewInvitation.objects.filter(
                    advert=advert,
                    candidate=user
                ).first()

                return render(request, "adverts/interview_invitation.html", {
                    "interview_invitation": interview_invitation
                })
        else:
            return HttpResponse("No feedback yet")
    else:
        return HttpResponse("You havent applied for this post")


@login_required
def job_offer_reply(request, id, pk):
    job_offer = get_object_or_404(JobOffer, pk=pk)
    advert = get_object_or_404(Advert, pk=id)
    if request.method == "POST":
        form = JobOfferReplyForm(request.POST, request.FILES)
        if form.is_valid():
            job_offer_reply = form.save(commit=False)
            job_offer_reply.job_offer = job_offer
            job_offer_reply.save()
            messages.success(request, "you have successfully replied!")
    form = JobOfferReplyForm()

    context = {
        "form": form,
        "advert": advert,
        "job_offer": job_offer
    }
    return render(request, "adverts/partials/job_offer_reply.html", context)


@login_required
def view_reply(request, id, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    interview = get_object_or_404(Interview, pk=pk)
    advert = get_object_or_404(Advert, pk=id)
    job_offer = interview.job_offer.first()
    # print(job_offer)
    return render(request, "adverts/view_reply.html", {"job_offer": job_offer, "advert": advert})


@login_required
def add_experience(request):
    user = request.user
    if request.method == "POST":
        title = request.POST["job_title"]
        checkbox = request.POST.get("checkbox")
        company = request.POST["company"]
        location = request.POST["location"]
        start_date = request.POST["start_date"]
        exp = Experience.objects.create(
            user=user, job_title=title,
            company=company, location=location,
            start_year=start_date
        )
        if not checkbox == 'on':
            print("checkbox is onn")
            exp.description = request.POST["description"]
            exp.end_year = request.POST["end_date"]
            exp.currently_working_in_this_role = False
            exp.save()
        context = {
            "experience": Experience.objects.filter(user=user)
        }
        return render(request, 'adverts/partials/experience.html', context)

    form = ExperienceForm()
    context = {
        "form": form
    }
    return render(request, "adverts/partials/add_experience.html", context)


class AddAcademicQualification(View):
    def get(self, request, *args, **kwargs):
        form = AcademicQualificationForm()
        context = {
            "e_form": form
        }
        return render(request, "adverts/partials/add_academic_qualification.html", context)

    def post(self, request, *args, **kwargs):
        form = AcademicQualificationForm(request.POST, request.FILES)
        if form.is_valid():
            qualification = form.save(commit=False)
            qualification.employee = request.user
            qualification.save()
            qualifications = AcademicQualification.objects.filter(
                employee=request.user)
            # print("success")
            messages.success(request, "Qualification added successfully")

            return render(request, "adverts/partials/qualifications.html", {"qualifications": qualifications})
        # form = AcademicQualificationForm()
        context = {
            "e_form": form,
            "qualifications": request.user.academic_qualifications.all()
        }
        return render(request, "adverts/partials/add_academic_qualification.html", context)


@login_required
def experience_and_qualifications(request):
    user = request.user
    qualifications = AcademicQualification.objects.filter(employee=user)
    experience = Experience.objects.filter(user=user)
    form = AcademicQualificationForm()
    print(experience)
    context = {
        "qualifications": qualifications,
        "experience": experience,
        "form": form
    }
    return render(request, "adverts/experience_and_qualifications.html", context)


@is_admin
def summary_table(request, id):
    advert = get_object_or_404(Advert, pk=id)
    applications = Application.objects.filter(advert=advert)
    context = {
        "applications": applications,
        "advert": advert
    }
    return render(request, "adverts/summary_table.html", context)


@is_admin
def export_summary_table(request, id):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    advert = get_object_or_404(Advert, pk=id)
    queryset = Application.objects.filter(advert=advert)
    resource = SummaryTableResource()
    dataset = resource.export(queryset)
    data_format = dataset.csv
    response = HttpResponse(data_format, content_type=f"text/{format}")
    response["Content-Disposition"] = f"attachment; filename={advert.title}_summary_table.csv"
    return response


class EditQualification(View, LoginRequiredMixin):
    def get(self, request, pk, *args, **kwargs):
        qualification = get_object_or_404(AcademicQualification, pk=pk)
        form = AcademicQualificationForm(instance=qualification)
        context = {
            "qualification": qualification,
            "form": form
        }
        return render(request, 'adverts/partials/edit_qualification.html', context)

    def post(self, request, pk, *args, **kwargs):
        qualification = get_object_or_404(AcademicQualification, pk=pk)
        form = AcademicQualificationForm(
            request.POST, request.FILES, instance=qualification)
        if form.is_valid():
            form.save()
            # print("form is valid ")
            return render(request, 'adverts/partials/qualifications.html')
        context = {
            "qualification": qualification,
            "form": form
        }
        return render(request, 'adverts/partials/edit_qualification.html', context)


""" def edit_qualification(request, pk):
    qualification = get_object_or_404(AcademicQualification, pk=pk)
    if request.method == "POST":
        form = AcademicQualificationForm(
            request.POST, request.FILES, instance=qualification)
        if form.is_valid():
            form.save()
            # print("form is valid ")
            return render(request, 'adverts/partials/qualifications.html')
    form = AcademicQualificationForm(instance=qualification)
    context = {
        "qualification": qualification,
        "form": form
    }
    return render(request, 'adverts/partials/edit_qualification.html', context) """


class EditExperience(View, LoginRequiredMixin):
    def get(self, request, pk, *args, **kwargs):
        experience = get_object_or_404(Experience, pk=pk)
        form = ExperienceForm(
            instance=experience)
        context = {
            "exp": experience,
            "form": form
        }
        return render(request, 'adverts/partials/edit_experience.html', context)

    def post(self, request, pk, *args, **kwargs):
        experience = get_object_or_404(Experience, pk=pk)
        form = ExperienceForm(
            request.POST, request.FILES, instance=experience)
        if form.is_valid():
            form.save()
            # print("form is valid ")
            return render(request, 'adverts/partials/experience.html')
        context = {
            "exp": experience,
            "form": form
        }
        return render(request, 'adverts/partials/edit_experience.html', context)
