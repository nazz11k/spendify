from django.db import models
from users.models import CustomUser


class Category(models.Model):
    class CategoryType(models.TextChoices):
        INCOME = 'INCOME', 'Income'
        EXPENSE = 'EXPENSE', 'Expense'

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=7, choices=CategoryType.choices)

    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='categories',
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ('name', 'type', 'owner')
        verbose_name_plural = "Categories"

    def __str__(self):
        owner_str = 'Standard' if self.owner is None else self.owner.email
        return f"{self.name} ({self.get_type_display()}) - {owner_str}"


class Transaction(models.Model):
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.owner.email} - {self.amount} on {self.date}"
