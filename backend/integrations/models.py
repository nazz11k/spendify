from django.db import models
from users.models import CustomUser


class FinancialAdvice(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='financial_advice'
    )
    advices = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Advice for {self.user.email} at {self.created_at}"
