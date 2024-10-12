from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('vendor', 'Vendor'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')

    def __str__(self):
        return f"{self.user.email} - {self.get_user_type_display()}"

    def is_student(self):
        return self.user_type == 'student'

    def is_vendor(self):
        return self.user_type == 'vendor'

