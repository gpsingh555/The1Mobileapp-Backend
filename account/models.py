from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models
import datetime
from datetime import datetime
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
import pytz
from rest_framework.fields import BooleanField

ENGLISH, ARABIC = "1", "2"
LANGUAGES_CHOICES = (
    (ENGLISH, "ENGLISH"),
    (ARABIC, "ARABIC")
)
USER_TYPE = (('0','Normal'),('1','Admin'),('2','SubAdmin'),('3','IndividualRestaurant'),('4','Supplier'),('5','ProcurementOfficer'))
GENDER_TYPE = (('1', 'MALE'),('2','FEMALE'),('3','OTHER'),("4","Not Selected"))
ACCOUNT_TYPE = (('1','normal'),('2','google'),('3','twitter'),('4','apple'))
DEVICE_TYPE = (('1','android'),('2','ios'),('3','web'))


class country(models.Model):
    name = models.CharField(default="", max_length=50)

    def __str__(self):
        return self.name


class state(models.Model):
    name = models.CharField(default="", max_length=255)
    country = models.ForeignKey(country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class city(models.Model):
    name = models.CharField(default="", max_length=500)
    state = models.ForeignKey(state, on_delete=models.CASCADE)
    country_id = models.ForeignKey(country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Userprofile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_profile")
    mobile_number = models.CharField(max_length=50, default="", blank=True, null=True)
    code = models.CharField(max_length=5, default="", blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    sampledate = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    image = models.ImageField(upload_to='Profile', default='profile/no-image.png', blank=True, null=True)
    # gender = models.CharField(max_length=100,default="Nogender",blank=True, null=True)
    role = models.CharField(max_length=100, blank=True, null=True)
    country = models.ForeignKey(country, on_delete=models.SET_NULL, null=True)
    state = models.CharField(default="", max_length=50)
    city = models.CharField(default="", max_length=50)
    device_type = models.CharField(max_length=10, default="", blank=True, null=True)
    device_token = models.CharField(max_length=500, blank=True, null=True)
    referral_code = models.CharField(max_length=100, blank=True, null=True)
    isotp_verified = models.BooleanField(default=False)
    is_profile_complete = models.BooleanField(default=False)
    user_bio = models.CharField(default="", blank=True, null=True, max_length=500)
    is_subadmin = models.BooleanField(default=False)
    location = models.PointField(null=True)
    quickblox_id = models.CharField(max_length=20, default="", blank=True, null=True)
    language = models.CharField(blank=True, null=True, choices=LANGUAGES_CHOICES, max_length=20)
    # social_id=models.CharField(max_length=200,blank=True,null=True)
   
    
    

    def __str__(self):
        return self.user.email


class signup_otp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=10, blank=True)
    expire = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    attempt = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email


class forget_otp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=10, blank=True)
    expire = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    secret_key = models.CharField(max_length=50, default="")
    attempt = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email




class SubAdminPermission(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sub_admin_permission')
    dashboard = models.BooleanField(default=False)
    user_mgmt = models.BooleanField(default=False)
    subadmin_mgmt = models.BooleanField(default=False)
    geolocation_mgmt = models.BooleanField(default=False)
    order_mgmt_per = models.BooleanField(default=False)
    chats_mgmt = models.BooleanField(default=False)
    news_mgmt = models.BooleanField(default=False)
    lottery_mgmt = models.BooleanField(default=False)
    payment_mgmt = models.BooleanField(default=False)
    credit_pts_mgmt = models.BooleanField(default=False)
    report_mgmt = models.BooleanField(default=False)
    promotion_mgmt = models.BooleanField(default=False)
    issue_mgmt = models.BooleanField(default=False)
    notification_mgmt = models.BooleanField(default=False)
    social_media_mgmt = models.BooleanField(default=False)
    report_mgmt = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + '--' + str(self.user.id)


class savecountry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_address")
    country = models.CharField(max_length=30, default="", blank=True, null=True)
    state = models.CharField(max_length=30, default="", blank=True, null=True)
    city = models.CharField(max_length=30, default="", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.id) + '-' + str(self.country)


class Region(models.Model):
    country = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    radius = models.IntegerField(default=0)
    lat = models.CharField(max_length=30)
    lng = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.city + '-' + str(self.radius)


class news_keyword(models.Model):
    keyword = models.CharField(default="", max_length=1000)


class News(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    block = models.BooleanField(default=False)
    title = models.CharField(default="", max_length=1000)
    author = models.CharField(default="", max_length=1000)
    description = models.TextField()
    publishedAt = models.DateTimeField(null=True)
    content = models.TextField(null=True)
    url = models.TextField(null=True)
    urlToImage = models.CharField(default="", max_length=10000, null=True)
    keyword = models.CharField(default="", max_length=1000)
    when_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CommentNews(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    news = models.ForeignKey(News, on_delete=CASCADE)
    feedback = models.TextField()
    comment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.feedback


class LikeNews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    like_date = models.DateTimeField(auto_now_add=True)

    @property
    def user_count(self):
        return self.news.count


STATUS_CHOICES = (

    ("Approved", "Approved"),
    ("Reject", "Reject"),

)


class UserReguest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request_id = models.CharField(default="", blank=True, null=True, max_length=100)
    name = models.CharField(default="", blank=True, null=True, max_length=100)
    service_provider = models.CharField(default="", blank=True, null=True, max_length=100)
    description = models.CharField(default="", blank=True, null=True, max_length=1000)
    status = models.CharField(max_length=50, default='Pending')
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.id) + '-' + str(self.name)
    
class UserAccount(models.Model):
    User=models.OneToOneField(User,on_delete=models.CASCADE)
    first_name=models.CharField(max_length=70)
    last_name=models.CharField(max_length=70,blank=True,null=True)
    email=models.CharField(max_length=200)
    Account_id=models.CharField(default="",max_length=20)
    user_type = models.CharField(max_length=10, choices=USER_TYPE)
    gender=models.CharField(max_length=10,choices=GENDER_TYPE)
    country_code=models.CharField(max_length=5,blank=True,null=True)
    date_of_birth=models.DateField(null=True,blank=True)
    mobile_number=models.CharField(max_length=15,default="")
    account_type =models.CharField(max_length=10,choices=ACCOUNT_TYPE)
    device_type = models.CharField(max_length=10,choices=DEVICE_TYPE)
    profile_image=models.ImageField(upload_to='User/profile_image',default='User/profile_image/default.jpg',null=True)
    allergic_to=models.CharField(max_length=500,default='None',blank=True,null=True)
    is_block=models.BooleanField(default=False)
    is_verified=models.BooleanField(default=False)
    location = models.PointField(null=True)
    when_add = models.DateTimeField(auto_now_add = True)
    loyalty_points=models.IntegerField(default=0)
    device_token=models.CharField(max_length=200,blank=True,null=True)
    social_id=models.CharField(max_length=200,blank=True,null=True)
    
    def __str__(self):
    	return self.mobile_number
