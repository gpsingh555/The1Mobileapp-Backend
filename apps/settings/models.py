from django.db import models

from rest_framework.authtoken.admin import User

GOOGLE_DRIVE, GOOGLE_ACCOUNT, WIFI = "1", "2", "3"

CHAT_BACKUP = (
    (GOOGLE_DRIVE, "GOOGLE_DRIVE"),
    (GOOGLE_ACCOUNT, "GOOGLE_ACCOUNT"),
    (WIFI, "WIFI")
)

SMALL, MEDIUM, LARGE = "1", "2", "3"

FONT_SIZE = (
    (SMALL, "SMALL"),
    (MEDIUM, "MEDIUM"),
    (LARGE, "LARGE")
)


class ChatSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_settings')
    chat_backup = models.CharField(max_length=50, default="1", choices=CHAT_BACKUP)
    font_size = models.CharField(max_length=50, default="2", choices=FONT_SIZE)
    media_visibility = models.BooleanField(default=True)

    class Meta:
        db_table = 'chat_settings'

    def __str__(self):
        return str(self.user)