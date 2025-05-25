from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
def main(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        linkedin = request.POST.get("linkedin", "") 
        message = request.POST.get("message")

        full_message = f"""
            Received message below from {email}, {first_name} {last_name}.
            LinkedIn: {linkedin}
            ________________________

            {message}
            """

        try:
            send_mail(
                subject="Received contact form submission",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.NOTIFY_EMAIL],
            )
        except Exception as e:
            return HttpResponse("There was an error sending your message. Please try again later", status=500)

        return redirect('success')

    return render(request, 'main_page/main_page.html')


from django.views.generic import TemplateView

class SuccessView(TemplateView):
    template_name = "main_page/success.html"