from django.db import models
from django.contrib.auth.models import User
# Create your models here.
ROLE_CHOICES = [
    ('teacher', 'Teacher'),
    ('student', 'Student'),
]

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
]


class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    state = models.CharField(
        max_length=100,
        blank=True
    )

    country = models.CharField(
        max_length=100,
        default="India"
    )

    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    bio = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )
    is_teacher_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username