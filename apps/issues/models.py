from django.db import models
from django.contrib.auth.models import User


OPEN, CLOSED = "1", "2"
QUERY_STATUS = (
    (OPEN, "open"),
    (CLOSED, "closed"),
)


# Create your models here.
class UserQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_query')
    subject = models.CharField(max_length=500)
    desc = models.TextField()
    ticket_id = models.CharField(unique=True, max_length=100)

    comment = models.TextField(blank=True)

    status = models.CharField(max_length=2, choices=QUERY_STATUS, default=OPEN)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_query'

    def __str__(self):
        return str(self.user.id) + '-' + str(self.ticket_id)
