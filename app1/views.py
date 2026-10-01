from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .models import Class, Subject, SubjectCombination
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from .models import Class
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

def is_admin_user(user):
    return user.is_authenticated and user.is_superuser


from decimal import Decimal

def index(request):
    student_id = request.GET.get("student_id", "").strip()
    notices = Notice.objects.all().order_by("-created_at")[:6]

    context = {
        "searched": bool(student_id),
        "search_student_id": student_id,
        "student": None,
        "student_results": [],
        "subject_count": 0,
        "total_marks": 0,
        "total_max": 0,
        "percentage": 0,
        "status": "",
        "notices": notices,
    }

    if student_id:
        try:
            student = Student.objects.get(student_id=student_id)

            results = Result.objects.filter(
                student=student
            ).select_related("subject").order_by("subject__subject_name")

            total_marks = Decimal("0")
            total_max = Decimal("0")
            result_rows = []

            for result in results:
                marks = result.marks
                max_marks = result.max_marks

                subject_percentage = (
                    (marks / max_marks) * Decimal("100")
                    if max_marks else Decimal("0")
                )

                result.subject_percentage = round(subject_percentage, 2)
                result.subject_status = (
                    "Pass" if subject_percentage >= 40 else "Fail"
                )

                result_rows.append(result)

                total_marks += marks
                total_max += max_marks

            percentage = (
                round((total_marks / total_max) * Decimal("100"), 2)
                if total_max else Decimal("0")
            )

            context.update({
                "student": student,
                "student_results": result_rows,
                "subject_count": len(result_rows),
                "total_marks": total_marks,
                "total_max": total_max,
                "percentage": percentage,
                "status": "Pass" if percentage >= 40 else "Fail",
            })

        except Student.DoesNotExist:
            pass

    return render(request, "index.html", context)
def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        authenticated_user = authenticate(request, username=username, password=password)

        if authenticated_user is not None and authenticated_user.is_superuser:
            login(request, authenticated_user)
            return redirect('admin_dashboard')
        else:
            error_message = "Invalid credentials or not an admin user."
    return render(request, 'admin_login.html',locals())


from .models import Class, Subject, Student, Result, Notice


@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def admin_dashboard(request):
    context = {
        "student_count": Student.objects.count(),
        "class_count": Class.objects.count(),
        "subject_count": Subject.objects.count(),
        "result_count": Result.objects.count(),
        "notice_count": Notice.objects.count(),
    }

    return render(request, "admin_dashboard.html", context)

@login_required
def create_class(request):
    if request.method == 'POST':
        try:
            class_name = request.POST.get('class_name')
            section = request.POST.get('section')
            academic_year = request.POST.get('academic_year')
            status = request.POST.get('status')

            # Create a new Class instance
            new_class = Class(
                class_name=class_name,
                section=section,
                academic_year=academic_year,
                status=status
            )
            new_class.save()
            messages.success(request, "Class created successfully!")
            return redirect('create_class')  # Redirect to the same page or any other page after successful creation
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
    return render(request, 'create_class.html')


def admin_logout(request):
    
    from django.contrib.auth import logout
    logout(request)
    return redirect('admin_login')
    
def manage_classes(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')

    classes = Class.objects.all()  
    return render(request, 'manage_classes.html', {'classes': classes})

# --------------------------------------------------------------------------------
@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def edit_class(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)

    if request.method == "POST":
        class_name = request.POST.get("class_name", "").strip()
        section = request.POST.get("section", "").strip()
        academic_year = request.POST.get("academic_year", "").strip()
        status = request.POST.get("status", "").strip()

        if not class_name or not academic_year:
            messages.error(request, "Class name and academic year are required.")
            return render(request, "edit_class.html", {"class_obj": class_obj})

        class_obj.class_name = class_name
        class_obj.section = section
        class_obj.academic_year = academic_year
        class_obj.status = status
        class_obj.save()

        messages.success(request, "Class updated successfully!")
        return redirect("manage_classes")

    return render(request, "edit_class.html", {"class_obj": class_obj})


@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def delete_class(request, class_id):
    if request.method == "POST":
        get_object_or_404(Class, id=class_id).delete()
        messages.success(request, "Class deleted successfully!")

    return redirect("manage_classes")


@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def create_subject(request):
    classes = Class.objects.all().order_by("class_name")

    if request.method == "POST":
        subject_name = request.POST.get("subject_name", "").strip()
        subject_code = request.POST.get("subject_code", "").strip()
        class_id = request.POST.get("class_name")
        status = request.POST.get("status", "active")

        if not subject_name or not subject_code or not class_id:
            messages.error(request, "All required fields must be filled.")
            return render(request, "create_subject.html", {"classes": classes})

        if Subject.objects.filter(subject_code=subject_code).exists():
            messages.error(request, "Subject code already exists.")
            return render(request, "create_subject.html", {"classes": classes})

        Subject.objects.create(
            subject_name=subject_name,
            subject_code=subject_code,
            class_name_id=class_id,
            status=status
        )

        messages.success(request, "Subject created successfully!")
        return redirect("create_subject")

    return render(request, "create_subject.html", {"classes": classes})


@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def create_subject_combination(request):
    classes = Class.objects.all().order_by("class_name")
    subjects = Subject.objects.all().order_by("subject_name")

    if request.method == "POST":
        class_id = request.POST.get("class_name")
        subject_id = request.POST.get("subject")
        status = request.POST.get("status", "active")

        if not class_id or not subject_id:
            messages.error(request, "Class and subject are required.")
            return render(request, "create_subject_combination.html",
                          {"classes": classes, "subjects": subjects})

        if SubjectCombination.objects.filter(
            class_name_id=class_id, subject_id=subject_id
        ).exists():
            messages.error(request, "This subject combination already exists.")
            return render(request, "create_subject_combination.html",
                          {"classes": classes, "subjects": subjects})

        SubjectCombination.objects.create(
            class_name_id=class_id,
            subject_id=subject_id,
            status=status
        )

        messages.success(request, "Subject combination created successfully!")
        return redirect("create_subject_combination")

    return render(request, "create_subject_combination.html",
                  {"classes": classes, "subjects": subjects})

@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def manage_subjects(request):
    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    subjects = Subject.objects.select_related("class_name").all().order_by("-id")

    if search:
        subjects = subjects.filter(
            Q(subject_name__icontains=search) |
            Q(subject_code__icontains=search) |
            Q(class_name__class_name__icontains=search)
        )

    if status:
        subjects = subjects.filter(status=status)

    return render(request, "manage_subjects.html", {
        "subjects": subjects,
        "search": search,
        "status": status,
    })

@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def edit_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    classes = Class.objects.all().order_by("class_name")

    if request.method == "POST":
        subject_name = request.POST.get("subject_name", "").strip()
        subject_code = request.POST.get("subject_code", "").strip()
        class_id = request.POST.get("class_name")
        status = request.POST.get("status", "active")

        if not subject_name or not subject_code or not class_id:
            messages.error(request, "All required fields must be filled.")
            return render(request, "edit_subject.html", {
                "subject": subject, "classes": classes
            })

        if Subject.objects.filter(subject_code=subject_code).exclude(id=subject.id).exists():
            messages.error(request, "Subject code already exists.")
            return render(request, "edit_subject.html", {
                "subject": subject, "classes": classes
            })

        subject.subject_name = subject_name
        subject.subject_code = subject_code
        subject.class_name_id = class_id
        subject.status = status
        subject.save()

        messages.success(request, "Subject updated successfully!")
        return redirect("manage_subjects")

    return render(request, "edit_subject.html", {
        "subject": subject, "classes": classes
    })


@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def delete_subject(request, subject_id):
    if request.method == "POST":
        subject = get_object_or_404(Subject, id=subject_id)
        subject.delete()
        messages.success(request, "Subject deleted successfully!")

    return redirect("manage_subjects")


@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def manage_subject_combinations(request):
    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    combinations = SubjectCombination.objects.select_related(
        "class_name", "subject"
    ).all().order_by("-id")

    if search:
        combinations = combinations.filter(
            Q(class_name__class_name__icontains=search) |
            Q(subject__subject_name__icontains=search) |
            Q(subject__subject_code__icontains=search)
        )

    if status:
        combinations = combinations.filter(status=status)

    return render(request, "manage_subject_combinations.html", {
        "combinations": combinations,
        "search": search,
        "status": status,
    })

@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def edit_subject_combination(request, combination_id):
    combination = get_object_or_404(SubjectCombination, id=combination_id)
    classes = Class.objects.all().order_by("class_name")
    subjects = Subject.objects.all().order_by("subject_name")

    if request.method == "POST":
        class_id = request.POST.get("class_name")
        subject_id = request.POST.get("subject")
        status = request.POST.get("status", "active")

        if not class_id or not subject_id:
            messages.error(request, "Class and subject are required.")
            return render(request, "edit_subject_combination.html", {"combination": combination, "classes": classes, "subjects": subjects})

        subject = get_object_or_404(Subject, id=subject_id)

        if subject.class_name_id != int(class_id):
            messages.error(request, "Selected subject does not belong to the selected class.")
            return render(request, "edit_subject_combination.html", {"combination": combination, "classes": classes, "subjects": subjects})

        if SubjectCombination.objects.filter(class_name_id=class_id, subject_id=subject_id).exclude(id=combination.id).exists():
            messages.error(request, "This subject combination already exists.")
            return render(request, "edit_subject_combination.html", {"combination": combination, "classes": classes, "subjects": subjects})

        combination.class_name_id = class_id
        combination.subject_id = subject_id
        combination.status = status
        combination.save()

        messages.success(request, "Subject combination updated successfully!")
        return redirect("manage_subject_combinations")

    return render(request, "edit_subject_combination.html", {"combination": combination, "classes": classes, "subjects": subjects})


@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def delete_subject_combination(request, combination_id):
    if request.method == "POST":
        get_object_or_404(SubjectCombination, id=combination_id).delete()
        messages.success(request, "Subject combination deleted successfully!")
    return redirect("manage_subject_combinations")

@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def add_student(request):
    classes = Class.objects.all().order_by("class_name")

    if request.method == "POST":
        student_id = request.POST.get("student_id", "").strip()
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        class_id = request.POST.get("class_name")
        roll_number = request.POST.get("roll_number", "").strip()
        date_of_birth = request.POST.get("date_of_birth")
        gender = request.POST.get("gender")
        address = request.POST.get("address", "").strip()
        status = request.POST.get("status", "active")

        if not all([student_id, full_name, email, phone, class_id,
                    roll_number, date_of_birth, gender]):
            messages.error(request, "All required fields must be filled.")
            return render(request, "add_student.html", {"classes": classes})

        if Student.objects.filter(student_id=student_id).exists():
            messages.error(request, "Student ID already exists.")
            return render(request, "add_student.html", {"classes": classes})

        if Student.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "add_student.html", {"classes": classes})

        Student.objects.create(
            student_id=student_id,
            full_name=full_name,
            email=email,
            phone=phone,
            class_name_id=class_id,
            roll_number=roll_number,
            date_of_birth=date_of_birth,
            gender=gender,
            address=address,
            status=status
        )

        messages.success(request, "Student added successfully!")
        return redirect("add_student")

    return render(request, "add_student.html", {"classes": classes})

@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def manage_students(request):
    search = request.GET.get("search", "").strip()
    selected_class = request.GET.get("class_name", "").strip()
    status = request.GET.get("status", "").strip()

    students = Student.objects.select_related("class_name").all().order_by("-id")
    classes = Class.objects.all().order_by("class_name")

    if search:
        students = students.filter(
            Q(student_id__icontains=search) |
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(roll_number__icontains=search)
        )

    if selected_class:
        students = students.filter(class_name_id=selected_class)

    if status:
        students = students.filter(status=status)

    return render(request, "manage_students.html", {
        "students": students,
        "classes": classes,
        "search": search,
        "selected_class": selected_class,
        "status": status,
    })

@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def delete_student(request, student_id):
    if request.method == "POST":
        student = get_object_or_404(Student, id=student_id)
        student.delete()
        messages.success(request, "Student deleted successfully!")

    return redirect("manage_students")

@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    classes = Class.objects.all().order_by("class_name")

    if request.method == "POST":
        student_id_value = request.POST.get("student_id", "").strip()
        email = request.POST.get("email", "").strip()

        if not all([
            student_id_value,
            request.POST.get("full_name", "").strip(),
            email,
            request.POST.get("phone", "").strip(),
            request.POST.get("class_name"),
            request.POST.get("roll_number", "").strip(),
            request.POST.get("date_of_birth"),
            request.POST.get("gender")
        ]):
            messages.error(request, "All required fields must be filled.")
            return render(request, "edit_student.html", {
                "student": student,
                "classes": classes
            })

        if Student.objects.filter(student_id=student_id_value).exclude(id=student.id).exists():
            messages.error(request, "Student ID already exists.")
            return render(request, "edit_student.html", {
                "student": student,
                "classes": classes
            })

        if Student.objects.filter(email=email).exclude(id=student.id).exists():
            messages.error(request, "Email already exists.")
            return render(request, "edit_student.html", {
                "student": student,
                "classes": classes
            })

        student.student_id = student_id_value
        student.full_name = request.POST.get("full_name", "").strip()
        student.email = email
        student.phone = request.POST.get("phone", "").strip()
        student.class_name_id = request.POST.get("class_name")
        student.roll_number = request.POST.get("roll_number", "").strip()
        student.date_of_birth = request.POST.get("date_of_birth")
        student.gender = request.POST.get("gender")
        student.address = request.POST.get("address", "").strip()
        student.status = request.POST.get("status", "active")
        student.save()

        messages.success(request, "Student updated successfully!")
        return redirect("manage_students")

    return render(request, "edit_student.html", {
        "student": student,
        "classes": classes
    })

@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def add_notice(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        message = request.POST.get("message", "").strip()
        status = request.POST.get("status", "active")

        if not title or not message:
            messages.error(request, "Title and message are required.")
            return render(request, "add_notice.html")

        Notice.objects.create(
            title=title,
            message=message,
            status=status
        )

        messages.success(request, "Notice added successfully!")
        return redirect("add_notice")

    return render(request, "add_notice.html")


@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def manage_notices(request):
    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    notices = Notice.objects.all().order_by("-id")

    if search:
        notices = notices.filter(
            Q(title__icontains=search) |
            Q(message__icontains=search)
        )

    if status:
        notices = notices.filter(status=status)

    return render(request, "manage_notices.html", {
        "notices": notices,
        "search": search,
        "status": status,
    })

@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def edit_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        message = request.POST.get("message", "").strip()
        status = request.POST.get("status", "active")

        if not title or not message:
            messages.error(request, "Title and message are required.")
            return render(request, "edit_notice.html", {"notice": notice})

        notice.title = title
        notice.message = message
        notice.status = status
        notice.save()

        messages.success(request, "Notice updated successfully!")
        return redirect("manage_notices")

    return render(request, "edit_notice.html", {"notice": notice})

@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def delete_notice(request, notice_id):
    if request.method == "POST":
        notice = get_object_or_404(Notice, id=notice_id)
        notice.delete()
        messages.success(request, "Notice deleted successfully!")

    return redirect("manage_notices")


@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def add_result(request):
    students = Student.objects.all().order_by("full_name")
    subjects = Subject.objects.all().order_by("subject_name")

    if request.method == "POST":
        student_id = request.POST.get("student")
        subject_id = request.POST.get("subject")
        marks = request.POST.get("marks", "").strip()
        max_marks = request.POST.get("max_marks", "100").strip()
        exam_type = request.POST.get("exam_type", "Final Exam").strip()

        if not student_id or not subject_id or not marks:
            messages.error(request, "Student, subject and marks are required.")
            return render(request, "add_result.html", {
                "students": students, "subjects": subjects
            })

        if float(marks) > float(max_marks):
            messages.error(request, "Marks cannot be greater than maximum marks.")
            return render(request, "add_result.html", {
                "students": students, "subjects": subjects
            })

        Result.objects.create(
            student_id=student_id,
            subject_id=subject_id,
            marks=marks,
            max_marks=max_marks,
            exam_type=exam_type
        )

        messages.success(request, "Result added successfully!")
        return redirect("add_result")

    return render(request, "add_result.html", {
        "students": students,
        "subjects": subjects
    })


@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def manage_results(request):
    search = request.GET.get("search", "").strip()
    exam_type = request.GET.get("exam_type", "").strip()

    results = Result.objects.select_related("student", "subject").order_by(
        "student__full_name", "subject__subject_name"
    )

    if search:
        results = results.filter(
            Q(student__student_id__icontains=search) |
            Q(student__full_name__icontains=search) |
            Q(subject__subject_name__icontains=search) |
            Q(subject__subject_code__icontains=search)
        )

    if exam_type:
        results = results.filter(exam_type=exam_type)

    grouped_results = {}

    for result in results:
        student_id = result.student.id

        if student_id not in grouped_results:
            grouped_results[student_id] = {
                "student": result.student,
                "results": []
            }

        grouped_results[student_id]["results"].append(result)

    return render(request, "manage_results.html", {
        "grouped_results": grouped_results.values(),
        "search": search,
        "exam_type": exam_type
    })


@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def edit_result(request, result_id):
    result = get_object_or_404(Result, id=result_id)
    students = Student.objects.all().order_by("full_name")
    subjects = Subject.objects.all().order_by("subject_name")

    if request.method == "POST":
        student_id = request.POST.get("student")
        subject_id = request.POST.get("subject")
        marks = request.POST.get("marks", "").strip()
        max_marks = request.POST.get("max_marks", "100").strip()
        exam_type = request.POST.get("exam_type", "Final Exam").strip()

        if not student_id or not subject_id or not marks:
            messages.error(request, "Student, subject and marks are required.")
            return render(request, "edit_result.html", {
                "result": result, "students": students, "subjects": subjects
            })

        if float(marks) > float(max_marks):
            messages.error(request, "Marks cannot be greater than maximum marks.")
            return render(request, "edit_result.html", {
                "result": result, "students": students, "subjects": subjects
            })

        result.student_id = student_id
        result.subject_id = subject_id
        result.marks = marks
        result.max_marks = max_marks
        result.exam_type = exam_type
        result.save()

        messages.success(request, "Result updated successfully!")
        return redirect("manage_results")

    return render(request, "edit_result.html", {
        "result": result,
        "students": students,
        "subjects": subjects
    })


@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def delete_result(request, result_id):
    if request.method == "POST":
        result = get_object_or_404(Result, id=result_id)
        result.delete()
        messages.success(request, "Result deleted successfully!")

    return redirect("manage_results")


@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("change_password")

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect("change_password")

        if len(new_password) < 8:
            messages.error(request, "New password must be at least 8 characters.")
            return redirect("change_password")

        if current_password == new_password:
            messages.error(request, "New password must be different from the current password.")
            return redirect("change_password")

        request.user.set_password(new_password)
        request.user.save()

        update_session_auth_hash(request, request.user)

        messages.success(request, "Password changed successfully.")

        return redirect("change_password")

    return render(request, "change_password.html")


@user_passes_test(is_admin_user, login_url="admin_login", redirect_field_name=None)
def download_result(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    results = Result.objects.filter(
        student=student
    ).select_related("subject").order_by("subject__subject_name")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="Result_{student.student_id}.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
    )

    label_style = ParagraphStyle(
        "LabelStyle",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        fontName="Helvetica-Bold",
    )

    value_style = ParagraphStyle(
        "ValueStyle",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
    )

    cell_style = ParagraphStyle(
        "CellStyle",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=10,
    )

    elements = []

    # Header
    elements.append(Paragraph("STUDENT MANAGEMENT SYSTEM", title_style))
    elements.append(
        Paragraph("SECONDARY SCHOOL EXAMINATION RESULT", subtitle_style)
    )
    elements.append(Spacer(1, 5 * mm))

    # Student information
    student_data = [
        [
            Paragraph("PRN / STUDENT ID", label_style),
            Paragraph(str(student.student_id), value_style),
            Paragraph("CANDIDATE NAME", label_style),
            Paragraph(str(student.full_name), value_style),
        ],
        [
            Paragraph("DATE OF BIRTH", label_style),
            Paragraph(str(student.date_of_birth), value_style),
            Paragraph("GENDER", label_style),
            Paragraph(str(student.gender), value_style),
        ],
        [
            Paragraph("CLASS", label_style),
            Paragraph(str(student.class_name), value_style),
            Paragraph("ROLL NUMBER", label_style),
            Paragraph(str(student.roll_number), value_style),
        ],
        [
            Paragraph("EMAIL", label_style),
            Paragraph(str(student.email), value_style),
            Paragraph("PHONE", label_style),
            Paragraph(str(student.phone), value_style),
        ],
    ]

    student_table = Table(
        student_data,
        colWidths=[32 * mm, 55 * mm, 32 * mm, 55 * mm],
    )

    student_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f2f2f2")),
            ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#f2f2f2")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )

    elements.append(student_table)
    elements.append(Spacer(1, 7 * mm))

    # Result table
    result_data = [
        [
            Paragraph("S.CODE", label_style),
            Paragraph("SUBJECT", label_style),
            Paragraph("MARKS", label_style),
            Paragraph("MAX", label_style),
            Paragraph("%", label_style),
            Paragraph("STATUS", label_style),
        ]
    ]

    total_marks = 0
    total_max = 0

    for result in results:
        marks = float(result.marks or 0)
        max_marks = float(result.max_marks or 0)

        percentage = (
            (marks / max_marks) * 100
            if max_marks else 0
        )

        status = "PASS" if percentage >= 40 else "FAIL"

        total_marks += marks
        total_max += max_marks

        result_data.append([
            Paragraph(str(result.subject.subject_code), cell_style),
            Paragraph(str(result.subject.subject_name), cell_style),
            Paragraph(f"{marks:g}", cell_style),
            Paragraph(f"{max_marks:g}", cell_style),
            Paragraph(f"{percentage:.2f}%", cell_style),
            Paragraph(status, cell_style),
        ])

    overall_percentage = (
        (total_marks / total_max) * 100
        if total_max else 0
    )

    overall_status = "PASS" if overall_percentage >= 40 else "FAIL"

    result_table = Table(
        result_data,
        colWidths=[
            22 * mm,
            62 * mm,
            24 * mm,
            24 * mm,
            24 * mm,
            25 * mm,
        ],
        repeatRows=1,
    )

    result_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bbbbbb")),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9e9e9")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("ALIGN", (0, 2), (0, -1), "CENTER"),
            ("ALIGN", (2, 1), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ])
    )

    elements.append(result_table)
    elements.append(Spacer(1, 7 * mm))

    # Overall result
    summary_data = [
        [
            Paragraph("TOTAL MARKS", label_style),
            Paragraph(f"{total_marks:g} / {total_max:g}", value_style),
            Paragraph("PERCENTAGE", label_style),
            Paragraph(f"{overall_percentage:.2f}%", value_style),
            Paragraph("RESULT", label_style),
            Paragraph(overall_status, value_style),
        ]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[28 * mm, 35 * mm, 28 * mm, 30 * mm, 22 * mm, 25 * mm],
    )

    summary_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 0), "CENTER"),
            ("ALIGN", (3, 0), (3, 0), "CENTER"),
            ("ALIGN", (5, 0), (5, 0), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ])
    )

    elements.append(summary_table)
    elements.append(Spacer(1, 12 * mm))

    elements.append(
        Paragraph(
            "This is a computer-generated result document.",
            ParagraphStyle(
                "Footer",
                parent=styles["Normal"],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER,
            ),
        )
    )

    doc.build(elements)

    return response