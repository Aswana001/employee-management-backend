from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('employee.urls')),
    path('api/v1/attendance/', include('attendance.urls')),
    path('api/v1/shifts/', include('shift_management.urls')),   
    path('api/v1/leaves/', include('leave_management.urls')),   
    path('api/v1/payroll/', include('payroll_management.urls')),
    path('api/v1/expenses/', include('expense_management.urls')),
    path('api/v1/performance/', include('performance_management.urls')),
    path('api/v1/recruitment/', include('recruitment.urls')),
    path('api/v1/audit/', include('audit_notifications.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)