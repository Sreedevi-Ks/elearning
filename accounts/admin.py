from django.contrib import admin
from .models import Profile
# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "role",
        "is_teacher_approved"
    )

    list_filter = (
        "role",
        "is_teacher_approved"
    )

    list_editable = (
        "is_teacher_approved",
    )