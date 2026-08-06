from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm, ProfileForm
from .models import Profile
from django.shortcuts import render
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from courses.models import Enrollment, Lesson, LessonProgress, QuizResult, Course, Quiz, Certificate
# Create your views here.
def home(request):

    return render(
        request,
        'home.html'
    )
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm


def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST, request.FILES)

        if form.is_valid():

            # Get data from the form
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Check if username already exists
            if User.objects.filter(username=username).exists():

                messages.error(
                    request,
                    "Username already exists. Please choose another username."
                )

            else:

                # Create Django User
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                # Create Profile
                profile = form.save(commit=False)
                profile.user = user
                if profile.role == "teacher":
                    profile.is_teacher_approved = False
                profile.save()
                if profile.role == "teacher":

                    messages.success(
                        request,
                        "Teacher registration submitted successfully. Please wait for admin approval."
                    )

                else:
                    messages.success(
                    request,
                    "Registration Successful! Please Login."
                )

                return redirect('login')

    else:

        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form
        }
    )
def user_login(request):

    if request.method == "POST":

        form = LoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:

                # Super Admin
                if user.is_superuser:

                    login(request, user)

                    return redirect("admin_dashboard")

                profile = Profile.objects.get(user=user)

                # Teacher Approval Check
                if (
                    profile.role == "teacher"
                    and not profile.is_teacher_approved
                ):

                    messages.error(
                        request,
                        "Your teacher account is waiting for admin approval."
                    )

                    return redirect("login")

                login(request, user)

                if profile.role == "teacher":

                    return redirect("teacher_dashboard")

                else:

                    return redirect("student_dashboard")

            else:

                messages.error(
                    request,
                    "Invalid Username or Password"
                )

    else:

        form = LoginForm()

    return render(
        request,
        "accounts/login.html",
        {
            "form": form
        }
    )
def user_logout(request):

    logout(request)

    messages.success(
        request,
        "Logged out successfully."
    )

    return redirect('home')
@login_required
def teacher_dashboard(request):

    if request.user.is_superuser:
        return redirect("/admin/")

    profile = Profile.objects.get(
        user=request.user
    )

    if profile.role != "teacher":
        return redirect("student_dashboard")

    return render(
        request,
        "accounts/teacher_dashboard.html"
    )
@login_required
def student_dashboard(request):

    if request.user.is_superuser:
        return redirect("/admin/")

    profile = Profile.objects.get(
        user=request.user
    )

    if profile.role != "student":
        return redirect("teacher_dashboard")

    enrolled_courses = Enrollment.objects.filter(
        student=profile
    )

    total_courses = enrolled_courses.count()

    total_lessons = Lesson.objects.filter(
        course__enrollment__student=profile
    ).distinct().count()

    completed_lessons = LessonProgress.objects.filter(
        student=request.user,
        completed=True
    ).count()

    overall_progress = 0

    if total_lessons > 0:

        overall_progress = int(
            (completed_lessons / total_lessons) * 100
        )
    quiz_attempts = QuizResult.objects.filter(
        student=request.user
    )

    total_quizzes = quiz_attempts.count()

    correct_answers = quiz_attempts.filter(
        is_correct=True
    ).count()

    wrong_answers = total_quizzes - correct_answers

    quiz_accuracy = 0

    if total_quizzes > 0:

        quiz_accuracy = int(
            (correct_answers / total_quizzes) * 100
        )

    return render(
        request,
        "accounts/student_dashboard.html",
        {
            "total_courses": total_courses,
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
            "overall_progress": overall_progress,
            "total_quizzes": total_quizzes,
            "correct_answers": correct_answers,
            "wrong_answers": wrong_answers,
            "quiz_accuracy": quiz_accuracy,
        }
    )
@login_required
def profile(request):

    profile = Profile.objects.get(
        user=request.user
    )

    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile
        }
    )
@login_required
def edit_profile(request):

    profile = Profile.objects.get(
        user=request.user
    )

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile updated successfully."
            )

            return redirect("profile")

    else:

        form = ProfileForm(
            instance=profile
        )

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "form": form
        }
    )
@login_required
def change_password(request):

    if request.method == "POST":

        form = PasswordChangeForm(
            request.user,
            request.POST
        )

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(
                request,
                user
            )

            messages.success(
                request,
                "Password changed successfully."
            )

            return redirect("profile")

    else:

        form = PasswordChangeForm(
            request.user
        )

    return render(
        request,
        "accounts/change_password.html",
        {
            "form": form
        }
    )
@login_required
def admin_dashboard(request):

    if not request.user.is_superuser:

        return redirect("login")

    total_students = Profile.objects.filter(
        role="student"
    ).count()

    total_teachers = Profile.objects.filter(
        role="teacher"
    ).count()

    total_courses = Course.objects.count()

    total_enrollments = Enrollment.objects.count()

    total_lessons = Lesson.objects.count()

    total_quizzes = Quiz.objects.count()
    total_certificates = Certificate.objects.count()

    return render(
        request,
        "accounts/admin_dashboard.html",
        {
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_courses": total_courses,
            "total_enrollments": total_enrollments,
            "total_lessons": total_lessons,
            "total_quizzes": total_quizzes,
            "total_certificates": total_certificates,
        }
    )
@login_required
def manage_teachers(request):

    if not request.user.is_superuser:

        return redirect("login")

    teachers = Profile.objects.filter(
        role="teacher"
    ).select_related("user")

    return render(
        request,
        "accounts/manage_teachers.html",
        {
            "teachers": teachers
        }
    )
@login_required
def toggle_teacher_status(request, user_id):

    if not request.user.is_superuser:

        return redirect("login")

    user = get_object_or_404(
        User,
        id=user_id
    )

    user.is_active = not user.is_active

    user.save()

    messages.success(
        request,
        "Teacher status updated successfully."
    )

    return redirect("manage_teachers")
@login_required
def manage_students(request):

    if not request.user.is_superuser:

        return redirect("login")

    students = Profile.objects.filter(
        role="student"
    ).select_related("user")

    return render(
        request,
        "accounts/manage_students.html",
        {
            "students": students
        }
    )
@login_required
def toggle_student_status(request, user_id):

    if not request.user.is_superuser:

        return redirect("login")

    user = get_object_or_404(
        User,
        id=user_id
    )

    user.is_active = not user.is_active

    user.save()

    messages.success(
        request,
        "Student status updated successfully."
    )

    return redirect("manage_students")
@login_required
def manage_courses(request):

    if not request.user.is_superuser:

        return redirect("login")

    courses = Course.objects.select_related(
        "teacher__user"
    )

    return render(
        request,
        "accounts/manage_courses.html",
        {
            "courses": courses
        }
    )
@login_required
def enrollment_report(request):

    if not request.user.is_superuser:

        return redirect("login")

    enrollments = Enrollment.objects.select_related(
        "student__user",
        "course"
    )

    return render(
        request,
        "accounts/enrollment_report.html",
        {
            "enrollments": enrollments
        }
    )
@login_required
def pending_teachers(request):

    if not request.user.is_superuser:
        return redirect("home")

    teachers = Profile.objects.filter(
        role="teacher",
        is_teacher_approved=False
    )

    return render(
        request,
        "accounts/pending_teachers.html",
        {
            "teachers": teachers
        }
    )
@login_required
def approve_teacher(request, profile_id):

    if not request.user.is_superuser:
        return redirect("home")

    teacher = Profile.objects.get(id=profile_id)

    teacher.is_teacher_approved = True
    teacher.save()

    messages.success(request, "Teacher Approved Successfully.")

    return redirect("pending_teachers")



