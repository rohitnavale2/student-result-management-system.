from django.contrib import admin

from django.contrib import admin
from .models import Class, Subject, Student, SubjectCombination, Result, Notice

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'class_name', 'section', 'academic_year', 'status', 'created_at')
    list_filter = ('status', 'academic_year')
    search_fields = ('class_name', 'section')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject_name', 'subject_code', 'class_name', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('subject_name', 'subject_code')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student_id', 'full_name', 'email', 'class_name', 'roll_number', 'status')
    list_filter = ('status', 'gender')
    search_fields = ('student_id', 'full_name', 'email', 'roll_number')

@admin.register(SubjectCombination)
class SubjectCombinationAdmin(admin.ModelAdmin):
    list_display = ('id', 'class_name', 'subject', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('class_name__class_name', 'subject__subject_name')

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'subject', 'marks', 'max_marks', 'exam_type', 'created_at')
    list_filter = ('exam_type',)
    search_fields = ('student__student_id', 'student__full_name', 'subject__subject_name')

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'posted_by', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'message')
