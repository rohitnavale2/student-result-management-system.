from django.db import models


class Class(models.Model):
    class_name = models.CharField(max_length=100)
    section = models.CharField(max_length=20, blank=True, null=True)
    academic_year = models.CharField(max_length=20)
    status = models.CharField(max_length=10, choices=[('active','Active'),('inactive','Inactive')], default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.class_name} - {self.section} ({self.academic_year})"

class Subject(models.Model):
    subject_name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=20, unique=True)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('active','Active'),('inactive','Inactive')], default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject_name} ({self.subject_code})"

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Male','Male'),('Female','Female'),('Other','Other')])
    address = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=[('active','Active'),('inactive','Inactive')], default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_id} - {self.full_name}"

class SubjectCombination(models.Model):
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('active','Active'),('inactive','Inactive')], default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.class_name} - {self.subject}"

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    exam_type = models.CharField(max_length=30, default='Final Exam')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.marks}"

class Notice(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    posted_by = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=[('active','Active'),('inactive','Inactive')], default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title