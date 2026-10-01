
# Student Result Management System

A web application built with Django and Bootstrap to manage student records, classes, subjects, examination results, and notices.

## Features
- Class Management
- Subject Management
- Student Management
- Subject Combination Management
- Student Result Management
- Notice Management
- Django Admin Panel

## Technologies Used
- Python
- Django
- HTML5
- CSS3
- Bootstrap 5
- SQLite

## Installation

### 1. Clone the Repository
```bash
git clone YOUR_REPOSITORY_URL
cd project_2
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
```

### 3. Activate the Environment
Windows:
```bash
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
python -m pip install django
```

If `requirements.txt` is available:
```bash
python -m pip install -r requirements.txt
```

### 5. Apply Migrations
```bash
python manage.py migrate
```

### 6. Create an Admin Account
```bash
python manage.py createsuperuser
```

### 7. Start the Server
```bash
python manage.py runserver
```

Open the application at http://127.0.0.1:8000/

Django Admin: http://127.0.0.1:8000/admin/

## Project Structure
```text
project_2/
├── app1/
│   ├── migrations/
│   ├── models.py
│   ├── admin.py
│   ├── views.py
│   └── urls.py
├── manage.py
└── db.sqlite3
```

## Learning Outcomes
- Django models and database relationships
- Database migrations
- CRUD operations
- Django Admin configuration
- Bootstrap-based UI development

## Future Improvements
- Student search and filtering
- Result calculation and percentage generation
- Improved form validation
- Role-based access for students and administrators

## Author
Rohit Navale

GitHub: https://github.com/rohitnavale2