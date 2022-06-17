from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(ChatGroupAdmin)
admin.site.register(ChatGroupMember)
admin.site.register(UserChat)
admin.site.register(UserAudioCall)
admin.site.register(UserChatSingle)