from django.db import models
from accounts.models import Profile
# Create your models here.
from django.db import models
from accounts.models import Profile
from django.contrib.auth.models import User

CATEGORY_CHOICES = [
    ('programming', 'Programming'),
    ('web', 'Web Development'),
    ('mobile', 'Mobile Development'),
    ('database', 'Database'),
    ('ai', 'Artificial Intelligence'),
    ('design', 'Design'),
]


LEVEL_CHOICES = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
]


STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('published', 'Published'),
]


class Course(models.Model):

    teacher = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'}
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )

    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES
    )

    course_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    duration = models.CharField(
        max_length=100
    )

    course_image = models.ImageField(
        upload_to="courses/",
        blank=True,
        null=True
    )

    maximum_students = models.PositiveIntegerField(
        default=100
    )

    language = models.CharField(
        max_length=50,
        default="English"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title
class Enrollment(models.Model):

    student = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    enrolled_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        unique_together = ['student', 'course']

    def __str__(self):

        return f"{self.student.user.username} - {self.course.title}"
class Lesson(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )
    lesson_video = models.FileField(
    upload_to="lesson_videos/",
    max_length=255,
    blank=True,
    null=True
    )
    lesson_pdf = models.FileField(
    upload_to="lesson_pdfs/",
    blank=True,
    null=True
    )

    duration = models.CharField(
    max_length=50,
    blank=True
    )
    lesson_order = models.PositiveIntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.title

    class Meta:

        ordering = ["lesson_order"]
class LessonProgress(models.Model):

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE
    )

    completed = models.BooleanField(
        default=False
    )

    completed_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        unique_together = ("student", "lesson")

    def __str__(self):

        return f"{self.student.username} - {self.lesson.title}"
class Quiz(models.Model):

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE
    )

    question = models.TextField()

    option1 = models.CharField(
        max_length=255
    )

    option2 = models.CharField(
        max_length=255
    )

    option3 = models.CharField(
        max_length=255
    )

    option4 = models.CharField(
        max_length=255
    )

    correct_answer = models.CharField(
        max_length=255
    )

    def __str__(self):

        return self.question
class QuizResult(models.Model):

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE
    )

    selected_answer = models.CharField(
        max_length=255
    )

    is_correct = models.BooleanField(
        default=False
    )

    attempted_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        unique_together = ("student", "quiz")

    def __str__(self):

        return f"{self.student.username} - {self.quiz.question}"
class Certificate(models.Model):

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    issue_date = models.DateField(
        auto_now_add=True
    )

    class Meta:

        unique_together = (
            "student",
            "course"
        )

    def __str__(self):

        return f"{self.student.username} - {self.course.title}"
class LiveClass(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="live_classes"
    )

    title = models.CharField(
        max_length=200
    )

    meeting_link = models.URLField()

    scheduled_date = models.DateField()

    scheduled_time = models.TimeField()

    duration = models.PositiveIntegerField(
        help_text="Duration in minutes"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.course.title} - {self.title}"
class Attendance(models.Model):

    live_class = models.ForeignKey(
        LiveClass,
        on_delete=models.CASCADE,
        related_name="attendance"
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    joined_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        unique_together = (
            "live_class",
            "student"
        )

    def __str__(self):

        return f"{self.student.username} - {self.live_class.title}"
class Assignment(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    due_date = models.DateField()

    maximum_marks = models.PositiveIntegerField(
        default=100
    )

    attachment = models.FileField(
        upload_to="assignments/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.title
class AssignmentSubmission(models.Model):

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions"
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    submission_file = models.FileField(
        upload_to="assignment_submissions/"
    )

    comments = models.TextField(
        blank=True,
        null=True
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    marks = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    feedback = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):

        return f"{self.assignment.title} - {self.student.username}"
class Payment(models.Model):

    PAYMENT_STATUS = [

        ("Pending", "Pending"),
        ("Success", "Success"),
        ("Failed", "Failed"),

    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    razorpay_order_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    razorpay_payment_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    razorpay_signature = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="Pending"
    )

    payment_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.student.username} - {self.course.title}"