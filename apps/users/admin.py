from django.contrib import admin
from .models import User, WorkDay, EmployeeShift


admin.site.register(User)
admin.site.register(WorkDay)
admin.site.register(EmployeeShift)