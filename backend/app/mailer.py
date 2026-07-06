import resend

from app.config import settings

resend.api_key = settings.RESEND_API_KEY


def send_verification_email(to_email: str, full_name: str, token: str) -> None:
    verify_link = f"{settings.cors_origins_list[0]}/verify-email?token={token}"
    expire_hours = settings.EMAIL_VERIFICATION_EXPIRE_MINUTES // 60
    resend.Emails.send({
        "from": settings.EMAIL_FROM,
        "to": [to_email],
        "subject": "Verify your Placement Journal account",
        "html": (
            f"<p>Hi {full_name},</p>"
            f"<p>Click the link below to verify your email and activate your account:</p>"
            f'<p><a href="{verify_link}">{verify_link}</a></p>'
            f"<p>This link expires in {expire_hours} hours.</p>"
        ),
    })
