# Employee Management System (HRIS Backend API)

A robust, production-grade Human Resource Information System (HRIS) REST API built with Django REST Framework (DRF) and PostgreSQL, configured for serverless deployment on Vercel.

## 🚀 Key Modules & Features

* **Employee Management:** Employee profiles, departments, designations, and document tracking.
* **Attendance & Geofencing:** Clock-in / clock-out logging, automated status tracking, and location validation logic.
* **Shift Management:** Shift rosters, scheduling, and operational coverage tracking.
* **Leave Management:** Leave requests, balance tracking, and approval workflows.
* **Payroll & Expense Processing:** Expense claim verification and payroll breakdowns.
* **Performance & Recruitment:** Performance appraisals, job requisitions, and applicant tracking.
* **Audit & Notifications:** Real-time log tracking and automated alerts.

---

## 🛠️ Tech Stack & Dependencies

* **Framework:** Python 3.12+, Django 5.0.4, Django REST Framework 3.15.1
* **Filtering & Search:** `django-filter`
* **Static Assets:** `whitenoise`
* **Database:** PostgreSQL (Supabase / Neon) with `psycopg2-binary`
* **Deployment Platform:** Vercel (Serverless Functions via WSGI)

---

## 💻 Local Setup & Development

### 1. Prerequisites
Ensure you have **Python 3.10+** and **Git** installed.

### 2. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git)
cd employee_management2

