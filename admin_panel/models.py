from django.db import models
from account.models import *
from django.contrib.auth.models import User
# Create your models here.



class ChatGroupAdmin(models.Model):
    group_id=models.CharField(max_length=40)
    name=models.CharField(max_length=40)
    admin_name=models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ChatGroupMember(models.Model):
    chat_group=models.ForeignKey(ChatGroupAdmin,on_delete=models.CASCADE)
    member=models.ForeignKey(User,on_delete=models.CASCADE)
    is_accept=models.BooleanField(default=False)

    def __str__(self):
        return str(self.chat_group.name)+' '+ str(self.member)


class UserChat(models.Model):
    chat_group=models.ForeignKey(ChatGroupAdmin,on_delete=models.CASCADE,null=True,blank=True)
    sender=models.ForeignKey(ChatGroupMember,on_delete=models.CASCADE,related_name='chat_sender')
    receiver=models.ManyToManyField(ChatGroupMember,related_name="chat_receiver")
    massage=models.CharField(max_length=1000)
    attechment=models.ImageField()
    on_date=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.chat_group.name ) + str(self.sender)


class UserAudioCall(models.Model):
    sender=models.ForeignKey(User,on_delete=models.CASCADE)
    receiver=models.ManyToManyField(User,blank=True,related_name='call_sender')
    massage=models.CharField(max_length=100,blank=True,null=True)
    start_tym=models.CharField(max_length=10,blank=True,null=True)
    end_tym=models.CharField(max_length=10,blank=True,null=True)
    created_date=models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.sender.username ) + str(self.sender)