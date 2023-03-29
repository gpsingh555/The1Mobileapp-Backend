from django.contrib import admin

from apps.chat.models import ChatGroup, MemberInChatGroup, UserAudioVideoCallHistory, UserChatHistory

# Register your models here.
admin.site.register(ChatGroup)
admin.site.register(MemberInChatGroup)
admin.site.register(UserAudioVideoCallHistory)
admin.site.register(UserChatHistory)
