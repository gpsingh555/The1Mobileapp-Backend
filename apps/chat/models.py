from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class ChatGroup(models.Model):
    group_id = models.CharField(max_length=40, blank=True, null=True)
    name = models.CharField(max_length=40)
    admin_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_group")
    members = models.ManyToManyField(User, related_name='chat_group_members',
                                     through="chat.MemberInChatGroup")

    is_reported = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    group_id = models.CharField(blank=True, null=True, max_length=1000)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_group'

    def __str__(self):
        return self.name


class MemberInChatGroup(models.Model):
    chat_group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    is_accept = models.BooleanField(default=False)

    class Meta:
        db_table = 'members_in_chat_group'

    def __str__(self):
        return str(self.chat_group.name)


class UserChatHistory(models.Model):
    chat_init_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_chat_initiator')
    second_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_chat_second')
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)
    is_reported = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_chat_history'

    def __str__(self):
        return str(self.chat_group.name)


class UserAudioVideoCallHistory(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    receivers = models.ManyToManyField(User, blank=True, related_name='call_receiver')
    start_time = models.CharField(max_length=50, blank=True, null=True)
    end_time = models.CharField(max_length=50, blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True, null=True)
    group_id = models.ForeignKey(ChatGroup, blank=True, null=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_audio_video_call_history'

