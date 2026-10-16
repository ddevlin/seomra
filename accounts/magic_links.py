from django.core.mail import send_mail
from django.urls import reverse


def send_magic_link(request, link):
    """Email the sign-in URL. With the console email backend this prints to the terminal."""
    url = request.build_absolute_uri(reverse("accounts:login_verify", args=[link.token]))
    send_mail(
        subject="Your Seomra sign-in link",
        message=(
            "Click the link below to sign in to Seomra. It works once and expires in 15 minutes.\n\n"
            f"{url}\n"
        ),
        from_email=None,
        recipient_list=[link.user.email],
    )
    return url
