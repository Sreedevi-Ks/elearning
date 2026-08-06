from django import forms
from django.contrib.auth.models import User
from .models import Profile
class RegisterForm(forms.ModelForm):

    username = forms.CharField(max_length=100)

    email = forms.EmailField()

    password = forms.CharField(
        widget=forms.PasswordInput()

    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:

        model = Profile

        fields = [
            'role',
            'phone',
            'gender',
            'date_of_birth',
            'address',
            'city',
            'state',
            'country',
            'profile_image',
            'bio'
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Bootstrap style for all fields
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control"
            })

        # Dropdown fields
        self.fields["role"].widget.attrs.update({
            "class": "form-select"
        })

        self.fields["gender"].widget.attrs.update({
            "class": "form-select"
        })

        # Password placeholder
        self.fields["password"].widget.attrs.update({
            "placeholder": "Enter Password"
        })
class LoginForm(forms.Form):

     username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class":"form-control",
            "placeholder":"Enter Username"
        })
    )

     password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class":"form-control",
            "placeholder":"Enter Password"
        })
    )
class ProfileForm(forms.ModelForm):

    class Meta:

        model = Profile

        fields = [
            "phone",
            "gender",
            "date_of_birth",
            "address",
            "city",
            "state",
            "country",
            "profile_image",
            "bio",
        ]

        widgets = {

            "phone": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "gender": forms.Select(
                attrs={"class": "form-select"}
            ),

            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "city": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "state": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "country": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "profile_image": forms.FileInput(
                attrs={"class": "form-control"}
            ),

            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

        }