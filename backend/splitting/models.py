from django.db import models

from users.models import CustomUser
from transactions.models import Category


class SharedSpent(models.Model):
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='owned_shared_spents'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Загальна сума чека"
    )
    date = models.DateField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shared spent by {self.owner.email} on {self.date}"


class SharedSpentMember(models.Model):
    shared_spent = models.ForeignKey(
        SharedSpent,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shared_parts'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Members part"
    )
    is_owner_part = models.BooleanField(
        default=False,
        help_text="Owner part"
    )

    class Meta:
        unique_together = ('shared_spent', 'user')

    def __str__(self):
        return f"{self.user.email}'s share ({self.amount})"
