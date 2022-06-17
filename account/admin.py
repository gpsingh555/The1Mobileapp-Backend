from django.contrib import admin
from .models import *
from django.contrib.auth.models import User

# Register your models here.


@admin.register(country)
class countryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ("name",)


@admin.register(state)
class stateAdmin(admin.ModelAdmin):
    list_display = ('name','country')
    search_fields = ("name",)
    list_filter = ('country',)


@admin.register(city)
class cityAdmin(admin.ModelAdmin):
    list_display = ('name','state')
    search_fields = ("name",)
    list_filter = ('state',)


@admin.register(signup_otp)
class SignupAdmin(admin.ModelAdmin):
    list_display=['user','otp','expire','is_used']

@admin.register(forget_otp)
class ForgetAdmin(admin.ModelAdmin):
    list_display=['user','otp','expire','secret_key','attempt','is_used']

@admin.register(SubAdminPermission)
class subadminper(admin.ModelAdmin):
    list_display=['user','dashboard','user_mgmt','subadmin_mgmt','geolocation_mgmt','news_mgmt','payment_mgmt','lottery_mgmt','order_mgmt_per','chats_mgmt',]

@admin.register(savecountry)
class savecountryAdmin(admin.ModelAdmin):
    list_display=['user','country','state','city']

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display=['country','state','city','lat','lng','radius','is_active']

# @admin.register(Userprofile)
# class ProfileAdmin(admin.ModelAdmin):
#     list_display=['user','device_type','device_token','referral_code','code','is_profile_complete','is_subadmin','image','country','state','city','sampledate','mobile_number','role','dob']

admin.site.register(Userprofile)
admin.site.register(news_keyword)
admin.site.register(News)

@admin.register(UserReguest)
class UserNewsRequest(admin.ModelAdmin):
    list_display=['user','name','service_provider','description','created_on','request_id','status']

#admin.site.register(NewsComment)

@admin.register(LikeNews)
class LikeNewsAdmin(admin.ModelAdmin):
    list_display=['user','news','like_date']

@admin.register(CommentNews)
class LikeNewsAdmin(admin.ModelAdmin):
    list_display=['user','news','feedback','comment_date']

