import razorpay
from django.conf import settings
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from datetime import date
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CourseForm, LessonForm, QuizForm, LiveClassForm, AssignmentForm,  AssignmentSubmissionForm
from .models import Course, Enrollment
from accounts.models import Profile
from django.contrib import messages
from .models import Lesson, LessonProgress, Assignment, AssignmentSubmission
from .models import Quiz, QuizResult, Certificate, LiveClass, Attendance, Payment
# Create your views here.
@login_required
def add_course(request):

    if request.method == "POST":

        form = CourseForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            course = form.save(commit=False)

            course.teacher = Profile.objects.get(
                user=request.user
            )

            course.save()

            return redirect("teacher_dashboard")

    else:

        form = CourseForm()

    return render(
        request,
        "courses/add_course.html",
        {
            "form": form
        }
    )

@login_required
def my_courses(request):

    profile = Profile.objects.get(
        user=request.user
    )

    courses = Course.objects.filter(
        teacher=profile
    )

    return render(
        request,
        "courses/my_courses.html",
        {
            "courses": courses
        }
    )
@login_required
def edit_course(request, course_id):
    if request.user.is_superuser:

        course = get_object_or_404(
            Course,
            id=course_id
        )
    else:
        profile = Profile.objects.get(
            user=request.user
        )

        course = get_object_or_404(
            Course,
            id=course_id,
            teacher=profile
        )

    if request.method == "POST":

        form = CourseForm(
            request.POST,
            request.FILES,
            instance=course
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Course updated successfully."
            )

            return redirect(
                "course_detail",
                course_id=course.id
            )

    else:

        form = CourseForm(
            instance=course
        )

    return render(
        request,
        "courses/edit_course.html",
        {
            "form": form,
            "course": course
        }
    )
@login_required
def delete_course(request, course_id):
    if request.user.is_superuser:

        course = get_object_or_404(
            Course,
            id=course_id
        )

    else:
        profile = Profile.objects.get(
            user=request.user
        )

        course =  get_object_or_404(
            Course,
            id=course_id,
            teacher=profile
        )
    if request.method == "POST":
        course.delete()
        messages.success(
            request,
            "Course deleted successfully."
        )
        return redirect("my_courses")
    return render(
        request,
        "courses/delete_course.html",
        {
            "course": course
        }
    )
def course_list(request):

    courses = Course.objects.filter(
        status="published"
    )

    return render(
        request,
        "courses/course_list.html",
        {
            "courses": courses
        }
    )
@login_required
def course_detail(request, course_id):

    course = Course.objects.get(id=course_id)
    lessons = Lesson.objects.filter(course=course)
    profile = Profile.objects.get(user=request.user)
    if profile.role == "teacher":

        if course.teacher != profile:

            messages.error(
                request,
                "You are not allowed to view this course."
            )

            return redirect("course_list")
    enrolled = False

    if profile.role == "student":
        enrolled = Enrollment.objects.filter(
            student=profile,
            course=course
        ).exists()
    
    progress_percentage = 0
    completed_lessons = 0
    total_lessons = lessons.count()

    if profile.role == "student":

        completed_lessons = LessonProgress.objects.filter(
            student=request.user,
            lesson__course=course,
            completed=True
        ).count()

        if total_lessons > 0:

            progress_percentage = int(
                (completed_lessons / total_lessons) * 100
            )
    live_classes = LiveClass.objects.filter(
        course=course
    ).order_by(
        "scheduled_date",
        "scheduled_time"
    )
    assignments = Assignment.objects.filter(
    course=course
    ).order_by(
    "-created_at"
    )
    student_submissions = {}

    if profile.role == "student":

        submissions = AssignmentSubmission.objects.filter(
            student=request.user,
            assignment__course=course
        )

        for submission in submissions:

            student_submissions[
                submission.assignment.id
            ] = submission
    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,
            "lessons": lessons,
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
            "progress_percentage": progress_percentage,
            "live_classes": live_classes,
            "assignments": assignments,
            "student_submissions": student_submissions,
            "enrolled": enrolled,
            "profile": profile,
        }
    )
@login_required
def lesson_detail(request, lesson_id):

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )

    previous_lesson = Lesson.objects.filter(
        course=lesson.course,
        lesson_order__lt=lesson.lesson_order
    ).order_by("-lesson_order").first()

    next_lesson = Lesson.objects.filter(
        course=lesson.course,
        lesson_order__gt=lesson.lesson_order
    ).order_by("lesson_order").first()
    progress = LessonProgress.objects.filter(
    student=request.user,
    lesson=lesson,
    completed=True).first()
    quiz = Quiz.objects.filter(
        lesson=lesson
    ).first()
    quiz_result = QuizResult.objects.filter(
    student=request.user,
    quiz=quiz
    ).first()
    return render(
        request,
        "courses/lesson_detail.html",
        {
            "lesson": lesson,
            "previous_lesson": previous_lesson,
            "next_lesson": next_lesson,
            "progress": progress,
            "quiz": quiz,
            "quiz_result": quiz_result,
        }
    )
@login_required
def mark_complete(request, lesson_id):

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )

    progress, created = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson
    )

    progress.completed = True
    progress.save()

    messages.success(
        request,
        "Lesson marked as completed."
    )

    return redirect(
        "lesson_detail",
        lesson_id=lesson.id
    )
@login_required
def enroll_course(request, course_id):

    profile = Profile.objects.get(
        user=request.user
    )

    if profile.role != "student":

        messages.error(
            request,
            "Only students can enroll in courses."
        )

        return redirect("course_detail", course_id=course_id)

    course = Course.objects.get(
        id=course_id
    )

    if Enrollment.objects.filter(
        student=profile,
        course=course
    ).exists():

        messages.warning(
            request,
            "You are already enrolled in this course."
        )

    else:

        Enrollment.objects.create(
            student=profile,
            course=course
        )

        messages.success(
            request,
            "Enrollment Successful!"
        )

    return redirect(
        "course_detail",
        course_id=course.id
    )
@login_required
def my_learning(request):

    profile = Profile.objects.get(
        user=request.user
    )

    enrollments = Enrollment.objects.filter(
        student=profile
    )

    return render(
        request,
        "courses/my_learning.html",
        {
            "enrollments": enrollments
        }
    )
@login_required
def add_lesson(request, course_id):

    course = Course.objects.get(
        id=course_id
    )

    if request.method == "POST":

        form = LessonForm(request.POST,request.FILES)

        if form.is_valid():

            lesson = form.save(commit=False)

            lesson.course = course

            lesson.save()

            messages.success(
                request,
                "Lesson added successfully."
            )

            return redirect(
                "course_detail",
                course_id=course.id
            )

    else:

        form = LessonForm()

    return render(
        request,
        "courses/add_lesson.html",
        {
            "form": form,
            "course": course
        }
    )
@login_required
def edit_lesson(request, lesson_id):

    profile = Profile.objects.get(
        user=request.user
    )

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id,
        course__teacher=profile
    )

    if request.method == "POST":

        form = LessonForm(
            request.POST,
            request.FILES,
            instance=lesson
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Lesson updated successfully."
            )

            return redirect(
                "course_detail",
                course_id=lesson.course.id
            )

    else:

        form = LessonForm(
            instance=lesson
        )

    return render(
        request,
        "courses/edit_lesson.html",
        {
            "form": form,
            "lesson": lesson
        }
    )
@login_required
def delete_lesson(request, lesson_id):

    profile = Profile.objects.get(
        user=request.user
    )

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id,
        course__teacher=profile
    )

    if request.method == "POST":

        course_id = lesson.course.id

        lesson.delete()

        messages.success(
            request,
            "Lesson deleted successfully."
        )

        return redirect(
            "course_detail",
            course_id=course_id
        )

    return render(
        request,
        "courses/delete_lesson.html",
        {
            "lesson": lesson
        }
    )
@login_required
def add_quiz(request, lesson_id):

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )

    if request.user != lesson.course.teacher.user:

        messages.error(
            request,
            "You are not allowed to add quizzes."
        )

        return redirect(
            "course_detail",
            course_id=lesson.course.id
        )

    if request.method == "POST":

        form = QuizForm(request.POST)

        if form.is_valid():

            quiz = form.save(commit=False)
            quiz.lesson = lesson
            quiz.save()

            messages.success(
                request,
                "Quiz added successfully."
            )

            return redirect(
                "lesson_detail",
                lesson_id=lesson.id
            )

    else:

        form = QuizForm()

    return render(
        request,
        "courses/add_quiz.html",
        {
            "form": form,
            "lesson": lesson,
        }
    )
@login_required
def edit_quiz(request, quiz_id):

    profile = Profile.objects.get(
        user=request.user
    )

    quiz = get_object_or_404(
        Quiz,
        id=quiz_id,
        lesson__course__teacher=profile
    )

    if request.method == "POST":

        form = QuizForm(
            request.POST,
            instance=quiz
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Quiz updated successfully."
            )

            return redirect(
                "lesson_detail",
                lesson_id=quiz.lesson.id
            )

    else:

        form = QuizForm(
            instance=quiz
        )

    return render(
        request,
        "courses/edit_quiz.html",
        {
            "form": form,
            "quiz": quiz
        }
    )
@login_required
def delete_quiz(request, quiz_id):

    profile = Profile.objects.get(
        user=request.user
    )

    quiz = get_object_or_404(
        Quiz,
        id=quiz_id,
        lesson__course__teacher=profile
    )

    if request.method == "POST":

        lesson_id = quiz.lesson.id

        quiz.delete()

        messages.success(
            request,
            "Quiz deleted successfully."
        )

        return redirect(
            "lesson_detail",
            lesson_id=lesson_id
        )

    return render(
        request,
        "courses/delete_quiz.html",
        {
            "quiz": quiz
        }
    )
@login_required
def submit_quiz(request, quiz_id):

    quiz = get_object_or_404(
        Quiz,
        id=quiz_id
    )

    # Check whether the student has already attempted this quiz
    if QuizResult.objects.filter(
        student=request.user,
        quiz=quiz
    ).exists():

        messages.warning(
            request,
            "You have already attempted this quiz."
        )

        return redirect(
            "lesson_detail",
            lesson_id=quiz.lesson.id
        )

    if request.method == "POST":

        selected_answer = request.POST.get("answer")

        is_correct = (
            selected_answer == quiz.correct_answer
        )

        QuizResult.objects.create(
            student=request.user,
            quiz=quiz,
            selected_answer=selected_answer,
            is_correct=is_correct
        )

        if is_correct:

            messages.success(
                request,
                "Correct Answer! 🎉"
            )

        else:

            messages.error(
                request,
                f"Wrong Answer! Correct Answer: {quiz.correct_answer}"
            )

    return redirect(
        "lesson_detail",
        lesson_id=quiz.lesson.id
    )
@login_required
def quiz_history(request):

    results = QuizResult.objects.filter(
        student=request.user
    ).select_related(
        "quiz",
        "quiz__lesson"
    )

    return render(
        request,
        "courses/quiz_history.html",
        {
            "results": results
        }
    )
@login_required
def download_certificate(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    total_lessons = Lesson.objects.filter(
        course=course
    ).count()

    completed_lessons = LessonProgress.objects.filter(
        student=request.user,
        lesson__course=course,
        completed=True
    ).count()

    if total_lessons == 0 or completed_lessons < total_lessons:

        messages.error(
            request,
            "Complete all lessons before downloading the certificate."
        )

        return redirect(
            "course_detail",
            course_id=course.id
        )
    Certificate.objects.get_or_create(
        student=request.user,
        course=course
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{course.title}_certificate.pdf"'
    )

    pdf = canvas.Canvas(response)

    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(
        300,
        780,
        "CERTIFICATE OF COMPLETION"
    )

    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(
        300,
        720,
        "This is to certify that"
    )

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(
        300,
        680,
        request.user.get_full_name() or request.user.username
    )

    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(
        300,
        640,
        "has successfully completed"
    )

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(
        300,
        600,
        course.title
    )

    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(
        300,
        540,
        f"Date: {date.today()}"
    )

    pdf.save()

    return response
@login_required
def my_enrolled_courses(request):

    profile = Profile.objects.get(
        user=request.user
    )

    enrollments = Enrollment.objects.filter(
        student=profile
    ).select_related("course")

    return render(
        request,
        "courses/my_enrolled_courses.html",
        {
            "enrollments": enrollments
        }
    )
@login_required
def continue_learning(request, course_id):

    profile = Profile.objects.get(
        user=request.user
    )

    course = get_object_or_404(
        Course,
        id=course_id
    )

    next_lesson = Lesson.objects.exclude(
        lessonprogress__student=request.user,
        lessonprogress__completed=True
    ).filter(
        course=course
    ).order_by(
        "lesson_order"
    ).first()

    if next_lesson:

        return redirect(
            "lesson_detail",
            lesson_id=next_lesson.id
        )

    first_lesson = Lesson.objects.filter(
        course=course
    ).order_by(
        "lesson_order"
    ).first()

    if first_lesson:

        return redirect(
            "lesson_detail",
            lesson_id=first_lesson.id
        )

    messages.info(
        request,
        "No lessons available."
    )

    return redirect(
        "course_detail",
        course_id=course.id
    )
@login_required
def certificate_center(request):

    certificates = Certificate.objects.filter(
        student=request.user
    )

    return render(
        request,
        "courses/certificate_center.html",
        {
            "certificates": certificates
        }
    )
@login_required
def add_live_class(request, course_id):

    profile = get_object_or_404(
        Profile,
        user=request.user
    )

    course = get_object_or_404(
        Course,
        id=course_id,
        teacher=profile
    )

    if request.method == "POST":

        form = LiveClassForm(request.POST)

        if form.is_valid():

            live_class = form.save(commit=False)

            live_class.course = course

            live_class.save()

            messages.success(
                request,
                "Live class scheduled successfully."
            )

            return redirect(
                "course_detail",
                course_id=course.id
            )

    else:

        form = LiveClassForm()

    return render(
        request,
        "courses/add_live_class.html",
        {
            "form": form,
            "course": course,
        }
    )
@login_required
def edit_live_class(request, live_class_id):

    profile = get_object_or_404(
        Profile,
        user=request.user
    )

    live_class = get_object_or_404(
        LiveClass,
        id=live_class_id,
        course__teacher=profile
    )

    if request.method == "POST":

        form = LiveClassForm(
            request.POST,
            instance=live_class
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Live class updated successfully."
            )

            return redirect(
                "course_detail",
                course_id=live_class.course.id
            )

    else:

        form = LiveClassForm(
            instance=live_class
        )

    return render(
        request,
        "courses/edit_live_class.html",
        {
            "form": form,
            "live_class": live_class,
        }
    )
@login_required
def delete_live_class(request, live_class_id):

    profile = get_object_or_404(
        Profile,
        user=request.user
    )

    live_class = get_object_or_404(
        LiveClass,
        id=live_class_id,
        course__teacher=profile
    )

    if request.method == "POST":

        course_id = live_class.course.id

        live_class.delete()

        messages.success(
            request,
            "Live class deleted successfully."
        )

        return redirect(
            "course_detail",
            course_id=course_id
        )

    return render(
        request,
        "courses/delete_live_class.html",
        {
            "live_class": live_class,
        }
    )
@login_required
def join_live_class(request, live_class_id):

    live_class = get_object_or_404(
        LiveClass,
        id=live_class_id
    )

    profile = Profile.objects.get(
        user=request.user
    )

    if profile.role == "student":

        Attendance.objects.get_or_create(
            live_class=live_class,
            student=request.user
        )

    return redirect(
        live_class.meeting_link
    )
@login_required
def view_attendance(request, live_class_id):

    profile = get_object_or_404(
        Profile,
        user=request.user
    )

    live_class = get_object_or_404(
        LiveClass,
        id=live_class_id,
        course__teacher=profile
    )

    attendance = Attendance.objects.filter(
        live_class=live_class
    ).select_related(
        "student"
    )

    return render(
        request,
        "courses/view_attendance.html",
        {
            "live_class": live_class,
            "attendance": attendance,
        }
    )
@login_required
def add_assignment(request, course_id):

    profile = get_object_or_404(
        Profile,
        user=request.user
    )

    course = get_object_or_404(
        Course,
        id=course_id,
        teacher=profile
    )

    if request.method == "POST":

        form = AssignmentForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            assignment = form.save(commit=False)

            assignment.course = course

            assignment.save()

            messages.success(
                request,
                "Assignment added successfully."
            )

            return redirect(
                "course_detail",
                course_id=course.id
            )

    else:

        form = AssignmentForm()

    return render(
        request,
        "courses/add_assignment.html",
        {
            "form": form,
            "course": course,
        }
    )
@login_required
def submit_assignment(request, assignment_id):

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id
    )

    profile = get_object_or_404(
        Profile,
        user=request.user
    )

    if profile.role != "student":

        messages.error(
            request,
            "Only students can submit assignments."
        )

        return redirect(
            "course_detail",
            course_id=assignment.course.id
        )

    if request.method == "POST":

        form = AssignmentSubmissionForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            submission = form.save(commit=False)

            submission.assignment = assignment

            submission.student = request.user

            submission.save()

            messages.success(
                request,
                "Assignment submitted successfully."
            )

            return redirect(
                "course_detail",
                course_id=assignment.course.id
            )

    else:

        form = AssignmentSubmissionForm()

    return render(
        request,
        "courses/submit_assignment.html",
        {
            "form": form,
            "assignment": assignment,
        }
    )
@login_required
def view_submissions(request, assignment_id):

    profile = get_object_or_404(
        Profile,
        user=request.user
    )

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        course__teacher=profile
    )

    submissions = AssignmentSubmission.objects.filter(
        assignment=assignment
    ).select_related(
        "student"
    )

    return render(
        request,
        "courses/view_submissions.html",
        {
            "assignment": assignment,
            "submissions": submissions,
        }
    )
@login_required
def grade_submission(request, submission_id):

    profile = get_object_or_404(
        Profile,
        user=request.user
    )

    submission = get_object_or_404(
        AssignmentSubmission,
        id=submission_id,
        assignment__course__teacher=profile
    )

    if request.method == "POST":

        submission.marks = request.POST.get("marks")

        submission.feedback = request.POST.get("feedback")

        submission.save()

        messages.success(
            request,
            "Assignment graded successfully."
        )

        return redirect(
            "view_submissions",
            assignment_id=submission.assignment.id
        )

    return render(
        request,
        "courses/grade_submission.html",
        {
            "submission": submission,
        }
    )
@login_required
def course_payment(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    profile = get_object_or_404(
        Profile,
        user=request.user
    )

    if profile.role != "student":

        messages.error(
            request,
            "Only students can purchase courses."
        )

        return redirect(
            "course_detail",
            course_id=course.id
        )

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    amount = int(course.course_fee * 100)

    razorpay_order = client.order.create({

        "amount": amount,

        "currency": "INR",

        "payment_capture": 1

    })

    payment = Payment.objects.create(

        student=request.user,

        course=course,

        amount=course.course_fee,

        razorpay_order_id=razorpay_order["id"],

        status="Pending"

    )

    context = {

        "course": course,

        "payment": payment,

        "razorpay_order_id": razorpay_order["id"],

        "razorpay_key": settings.RAZORPAY_KEY_ID,

        "amount": amount,

    }

    return render(

        request,

        "courses/course_payment.html",

        context

    )
@login_required
def payment_verify(request):

    if request.method == "POST":

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_signature = request.POST.get("razorpay_signature")

        data = {

            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature

        }

        try:

            client.utility.verify_payment_signature(data)

            payment = Payment.objects.get(
                razorpay_order_id=razorpay_order_id
            )

            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = "Success"

            payment.save()

            profile = Profile.objects.get(
                user=request.user
            )

            Enrollment.objects.get_or_create(
                student=profile,
                course=payment.course
            )

            messages.success(
                request,
                "Payment Successful. You are now enrolled."
            )

            return redirect(
                "course_detail",
                course_id=payment.course.id
            )

        except:

            messages.error(
                request,
                "Payment verification failed."
            )

            return redirect("course_list")
def about(request):

    return render(
        request,
        "about.html"
    )
def contact(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        messages.success(
            request,
            "Thank you! Your message has been received."
        )

        return redirect("contact")

    return render(
        request,
        "contact.html"
    )
@login_required
def my_students(request):

    profile = Profile.objects.get(user=request.user)

    students = Enrollment.objects.filter(
        course__teacher=profile
    ).select_related(
        "student",
        "course"
    )

    return render(
        request,
        "courses/my_students.html",
        {
            "students": students
        }
    )
@login_required
def teacher_payments(request):

    profile = Profile.objects.get(user=request.user)

    payments = Payment.objects.filter(
        course__teacher=profile
    )

    return render(
        request,
        "courses/teacher_payments.html",
        {
            "payments": payments
        }
    )