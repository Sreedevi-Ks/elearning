from django.contrib import admin
from .models import Course, Enrollment, Lesson, LessonProgress, Quiz, QuizResult, Certificate, LiveClass, Attendance, Assignment, AssignmentSubmission, Payment
# Register your models here.

admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Lesson)
admin.site.register(LessonProgress)
admin.site.register(Quiz)
admin.site.register(QuizResult)
admin.site.register(Certificate)
admin.site.register(LiveClass)
admin.site.register(Attendance)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)
admin.site.register(Payment)