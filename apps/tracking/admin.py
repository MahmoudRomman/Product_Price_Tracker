from django.contrib import admin
from .models import UserProductTracking, Notification, EmployeeTask
# Register your models here.


admin.site.register(UserProductTracking)
admin.site.register(Notification)
admin.site.register(EmployeeTask)