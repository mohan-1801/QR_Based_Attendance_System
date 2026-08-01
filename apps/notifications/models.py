from django.db import models
from django.conf import settings

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        WARNING = 'WARNING', 'Warning / Alert'
        INFO = 'INFO', 'Information'
        SUCCESS = 'SUCCESS', 'Success'
        ATTENDANCE = 'ATTENDANCE', 'Attendance Update'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices, default=NotificationType.INFO)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} for {self.user.username}"
