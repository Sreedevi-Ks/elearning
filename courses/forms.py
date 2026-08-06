from django import forms
from .models import Course, Lesson, Quiz, LiveClass, Assignment, AssignmentSubmission


class CourseForm(forms.ModelForm):

    class Meta:

        model = Course

        exclude = ['teacher']
class LessonForm(forms.ModelForm):

    class Meta:

        model = Lesson

        fields = [
            "title",
            "description",
            "lesson_video",
            "lesson_pdf",
            "duration",
            "lesson_order",
        ]
class QuizForm(forms.ModelForm):

    class Meta:

        model = Quiz

        fields = [
            "question",
            "option1",
            "option2",
            "option3",
            "option4",
            "correct_answer",
        ]

        widgets = {

            "question": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),

            "option1": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "option2": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "option3": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "option4": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "correct_answer": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter the correct option exactly"
                }
            ),

        }
class LiveClassForm(forms.ModelForm):

    class Meta:

        model = LiveClass

        fields = [
            "title",
            "meeting_link",
            "scheduled_date",
            "scheduled_time",
            "duration",
        ]

        widgets = {

            "scheduled_date": forms.DateInput(
                attrs={"type": "date"}
            ),

            "scheduled_time": forms.TimeInput(
                attrs={"type": "time"}
            ),

        }
class AssignmentForm(forms.ModelForm):

    class Meta:

        model = Assignment

        fields = [
            "title",
            "description",
            "due_date",
            "maximum_marks",
            "attachment",
        ]

        widgets = {

            "due_date": forms.DateInput(
                attrs={"type": "date"}
            ),

        }
class AssignmentSubmissionForm(forms.ModelForm):

    class Meta:

        model = AssignmentSubmission

        fields = [
            "submission_file",
            "comments",
        ]