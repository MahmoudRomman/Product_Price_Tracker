from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
# from django.contrib.postgres.fields import ArrayField
import uuid

class User(AbstractUser):
    class RoleChoices(models.TextChoices):
        CLIENT = 'CLIENT', 'Client'
        EMPLOYEE = 'EMPLOYEE', 'Employee'
        ADMIN = 'ADMIN', 'Admin'
        
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=10, 
        choices=RoleChoices.choices, 
        default=RoleChoices.CLIENT 
    )

    email = models.EmailField(unique=True)

    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.RoleChoices.ADMIN
        elif self.is_staff and self.role == self.RoleChoices.CLIENT:
            self.role = self.RoleChoices.EMPLOYEE
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username



class WorkDay(models.Model):
    class DayChoices(models.TextChoices):
        SATURDAY = 'SAT', 'Saturday'
        SUNDAY = 'SUN', 'Sunday'
        MONDAY = 'MON', 'Monday'
        TUESDAY = 'TUE', 'Tuesday'
        WEDNESDAY = 'WED', 'Wednesday'
        THURSDAY = 'THU', 'Thursday'
        FRIDAY = 'FRI', 'Friday'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=3, choices=DayChoices.choices, unique=True)

    def __str__(self):
        return self.get_code_display()


class EmployeeShift(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    employee = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='shifts', 
        limit_choices_to=Q(role='EMPLOYEE') | Q(role='ADMIN')
    )
    
    days = models.ManyToManyField(WorkDay, related_name='shifts', help_text="Select your working days:")
    
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        days_list = ", ".join([d.code for d in self.days.all()])
        return f"{self.employee.username} - Days: [{days_list}] ({self.start_time} to {self.end_time})"