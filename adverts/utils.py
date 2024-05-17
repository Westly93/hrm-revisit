from django.core.mail import send_mail
from reportlab.pdfgen import canvas
from io import BytesIO
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags


def send_html_email(subject, html_message, receipients):
    plain_message = strip_tags(html_message)
    message = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=None,
        to=receipients
    )

    message.attach_alternative(html_message, 'text/html')
    message.send()
    
    
def send_email(subject, message, recipient_list):
    from_email = 'mufudzaweston@gmail.com'

    send_mail(subject, message, from_email, [recipient_list])


def generate_job_offer_pdf(advert_title, candidate_name):
    # Create a BytesIO buffer to store the PDF content
    buffer = BytesIO()

    # Create the PDF object
    p = canvas.Canvas(buffer)

    # Write PDF content using ReportLab
    p.drawString(100, 750, "Job Offer")
    p.drawString(100, 700, f"Advert Title: {advert_title}")
    p.drawString(100, 650, f"Candidate Name: {candidate_name}")
    # Add more content as needed

    # Save the PDF content
    p.showPage()
    p.save()

    # Rewind the buffer to the beginning
    buffer.seek(0)

    return buffer
