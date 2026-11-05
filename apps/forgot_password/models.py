from django.db import models


class ForgotPasswordRequest(models.Model):
    email = models.EmailField()
    otp_hash = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"ForgotPasswordRequest(email={self.email}, is_used={self.is_used}, created_at={self.created_at})"