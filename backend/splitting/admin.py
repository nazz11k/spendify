from django.contrib import admin
from .models import SharedSpent, SharedSpentMember

admin.site.register(SharedSpent)
admin.site.register(SharedSpentMember)
