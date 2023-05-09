from copy import error
import re

from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db.models.aggregates import Count
from django.db.models.base import Model
from django.db.models import fields
from requests.api import request
from rest_framework.serializers import ModelSerializer, FloatField, Serializer, CharField, ImageField, \
    SerializerMethodField, EmailField, DateField
from ..models import *
import random
from rest_framework.fields import EmailField
from rest_framework.exceptions import APIException

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point

from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from admin_panel.models import *


class APIException400(APIException):
    status_code = 400


class APIException401(APIException):
    status_code = 401


USER_TYPE = (('0','Normal'),('1','Admin'))
GENDER_TYPE = (('1', 'MALE'),('2','FEMALE'),('3','OTHER'))
ACCOUNT_TYPE = (('1','normal'),('2','google'),('3','twitter'),('4','apple'))
DEVICE_TYPE = (('1','android'),('2','ios'),('3','web'))

class UserRegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(allow_blank=True)
    country_code=serializers.CharField(allow_blank=True)
    mobile = serializers.CharField(allow_blank=True)
    email = serializers.CharField(allow_blank=True, style={'input_type':'email'})
    password = serializers.CharField(allow_blank=True,write_only=True,style={'input_type':'password'})
    account_type = serializers.CharField(allow_blank=True)
    social_id = serializers.CharField(allow_blank=True)
    device_type = serializers.CharField(allow_blank=True)
    user_type = serializers.CharField(allow_blank=True)
    class Meta:
        model=UserAccount
        fields=['name', 'country_code', 'mobile', 'email', 'password', 'account_type', 'social_id',
        'device_type', 'device_token', 'user_type', 'when_add','is_verified']
    def validate(self, data):
        name=data['name']
        
        country_code=data['country_code']
        mob=data['mobile']
        email=data['email']
        password=data['password']
        account_type=data['account_type']
        social_id=data['social_id']
        device_type=data['device_type']
        device_token=data['device_token']
        user_type=data['user_type']

        if not account_type or account_type=='':
            raise APIException400({
                'success':'False',
                'message':'Please provide Account type',
            })
        if account_type not in ('1','2','3','4'):
            raise APIException400({
                'success':'False',
                'message':'Please provide a valid login type',
            })
        if account_type in ('2','3','4',2,3,4):
            if not social_id or social_id=="" :
                raise APIException400({
                    'success':'False',
                    'message':'Please provide social id'
                })
        
            if email:
                    user_t=User.objects.filter(email__iexact=email).first()
                    if user_t:
                        raise APIException400({
                            'success':"False",
                            'message':'This email is already registered',
                            })
                        
            ruser_qs = UserAccount.objects.filter(social_id__exact=social_id)
            if ruser_qs.exists() and ruser_qs.count()==1:
                ruser_obj=ruser_qs.first()

                user_obj=ruser_obj.user
                # payload = jwt_payload_handler(user_obj)
                # token = jwt_encode_handler(payload)
                # token = 'JWT '+ token

                # data['email']=user_obj.email
                # data['token']=token
                if ruser_obj.user.last_name:
                    data['name']=ruser_obj.user.first_name+' '+ruser_obj.user.last_name
                else:
                    data['name']=ruser_obj.user.first_name
                # data['mobile']=ruser_obj.mobile
                data['device_type']=ruser_obj.device_type
                data['device_token']=ruser_obj.device_token
                raise APIException400({
                    'success':'True',
                    'message':'Social id already exists',
                    'data':data,
                })
        if not device_type or device_type=='':
            raise APIException400({
                'success':'False',
                'message':'device_type is required',
            })
        if not user_type or user_type=='':
            raise APIException({
                'success':'False',
                'message':'user_type is required',
            })
        allowedDomains = [
        "aol.com", "att.net", "comcast.net", "facebook.com", "gmail.com", "gmx.com", "googlemail.com",
        "google.com", "hotmail.com", "hotmail.co.uk", "mac.com", "me.com", "mail.com", "msn.com",
        "live.com", "sbcglobal.net", "verizon.net", "yahoo.com", "yahoo.co.uk",
        "email.com", "games.com" , "gmx.net", "hush.com", "hushmail.com", "icloud.com", "inbox.com",
        "lavabit.com", "love.com" , "outlook.com", "pobox.com", "rocketmail.com",
        "safe-mail.net", "wow.com", "ygm.com" , "ymail.com", "zoho.com", "fastmail.fm",
        "yandex.com","iname.com","fluper.in","xyz63.com","yopmail.com"
        ]
        if account_type=='4' or account_type==4:
            if not email:
                email=social_id+'@xyz63.com'
                password='12345678'
                
        if '@' not in email:
            raise APIException400({
                'success':'False',
                'message':'Please provide a valid email',
            })
        else:
            if not email.split('@')[1] or email.split('@')[1]=="":
                raise APIException400({
                    'success':'False',
                    'message':'Please provide a valid email',
                })
            else:
                temp=email.split('@')[1]
                if '.' in temp:
                    if (not temp.split('.')[0] or temp.split('.')[0]=="") or (not temp.split('.')[1] or temp.split('.')[1]==""):
                        raise APIException400({
                            'success':'False',
                            'message':'Please provide a valid email',
                        })
                else:
                    raise APIException400({
                        'success':'False',
                        'message':'Please provide a valid email',
                    })
            domain = email.split('@')[1]
        # device type varification
        if device_type not in ['1','2','3']:
            raise APIException400({
                'success':'False',
                'message':'Please enter correct format of device_type',
            })
        if user_type not in ['0',0]:
            raise APIException400({
                'success':'False',
                'message':'Please enter correct format of user_type',
            })
        data['email']=email
        data['mobile']=mob
        data['country_code']=country_code
        data['password']=password
        return data
    def create(self, validated_data):
        social_id = ''
        name = validated_data['name']
        email = validated_data['email']
        password = validated_data['password']
        user_type = validated_data['user_type']
        account_type = validated_data['account_type']
        mobile = validated_data['mobile']
        is_approved=False
    


        first_name=name.split(' ')[0]
        last_name=' '.join(name.split(' ')[1:])

        user_obj = User(
            username = email.split('@')[0]+mobile,
            email = email,
            first_name=first_name,
            last_name=last_name,
            # is_active=is_active,
        )
        user_obj.set_password(password)
        user_obj.save()

        country_code = validated_data['country_code']
        mobile = validated_data['mobile']
        device_type = validated_data['device_type']
        device_token = validated_data['device_token']
        account_type = validated_data['account_type']
        if account_type in ('2','3','4'):
            social_id = validated_data['social_id']

        if social_id:
            ruser_obj = UserAccount(
                first_name=first_name,
                last_name=last_name,
                country_code=country_code,
                mobile_number=mobile,
                email=email,
                account_type = account_type,
                social_id = social_id,
                device_type = device_type,
                device_token = device_token,
                user_type = user_type,
                
                # is_email_verified=True,
                # is_mobile_verified=True,
                # is_approved=is_approved,
            
            )
            ruser_obj.User = user_obj
            ruser_obj.save()
        validated_data['token']=''
        if account_type in ('2','3','4') and user_type=='0':
            # payload = jwt_payload_handler(user_obj)
            # token = jwt_encode_handler(payload)
            # token = 'JWT '+token
            # validated_data['token'] = token
            return validated_data

def check_email(email):
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if (re.search(regex, email)):
        return True
    else:
        return False


def check_length(data):
    status = True
    for x in data:
        if len(x[0]) <= x[1]:
            status = True
        else:
            pass
    return status


def check_blank_or_null(data):
    status = True
    for x in data:
        if x == "" or x == None:
            status = False
            break
        else:
            pass
    return status


def check_password(password):
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    pat = re.compile(reg)
    mat = re.search(pat, password)
    if mat:
        return True
    else:
        return False


class signupSerializer(Serializer):
    first_name = CharField(error_messages={'required': 'First name is required', 'blank': 'first name is required'},
                           max_length=400)
    last_name = CharField(error_messages={'required': 'Last name is required', 'blank': 'last name is required'},
                          max_length=400)
    mobile_number = CharField(
        error_messages={'required': 'mobile number is required', 'blank': 'mobile number is required'}, max_length=20)
    email = EmailField(max_length=400)
    # nationality = CharField(error_messages={'required':'nationality is required', 'blank':'nationality is required'},max_length=400)
    # gender = CharField(error_messages={'required':'Gender is required', 'blank':'Gender is required'},max_length=100)
    password = CharField(error_messages={'required': 'password is required', 'blank': 'password is required'})
    device_token = CharField(
        error_messages={'required': 'device_token is required', 'blank': 'device_token is required'}, max_length=5000)
    device_type = CharField(error_messages={'required': 'device_type is required', 'blank': 'device_type is required'},
                            max_length=10)
    code = CharField(error_messages={'required': 'Country code is required', 'blank': 'Country code is required'},
                     max_length=100)
    latitude = FloatField(error_messages={'required': 'latitude is required', 'blank': 'latitude is required'},
                          min_value=0.0)
    longitude = FloatField(error_messages={'required': 'longitude is required', 'blank': 'longitude is required'},
                           min_value=0.0)
    # dob=CharField(required=False,allow_blank=True)
    referral_code = CharField(required=False, allow_blank=True)

    # user_bio=CharField(required=False,allow_blank=True)
    def validate(self, data):
        email = data.get('email').lower()
        mobile_number = data.get('mobile_number')
        password = data.get("password")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        # referral_code =data.get('referral_code')
        # gender = data.get("gender")
        # dob=data.get("dob")
        # print(dob)
        if User.objects.filter(email=email).exists():
            raise APIException400({
                'success': "False",
                'message': 'This email is already registered',
            })
        if User.objects.filter(username=mobile_number).exists():
            raise APIException400({
                'success': "False",
                'message': 'This Mobile number is already registered',
            })
        if password.isalpha() == True:
            raise ValidationError('Password must be alpha numeric')
        # if gender not in ['male','female']:
        # raise ValidationError('Gender must be male and female')
        if len(password) < 8:
            raise ValidationError('Password should 8 charcters long')
        if check_password(password) == False:
            raise ValidationError(
                   'Pasword Should have at least one number.Password Should have at least one uppercase and one lowercase character.Password Should have at least one special symbol.Password Should be between 6 to 20 characters long.'
                 )
        try:
            latitude = float(latitude)
        except:
            return ValidationError("latitude must be float number")
        try:
            longitude = float(longitude)
        except:
            return ValidationError("longitude must be float number")

        # try:
        #     dob=dob.split("/")
        #     dobO1=dob[2]+"-"+dob[1]+"-"+dob[0]
        #     dobO=datetime.strptime(dobO1,'%Y-%m-%d')
        # except:
        #     raise ValidationError("Date format is not right")
        return data

    def create(self, validated_data):
        # dob=self.validated_data['dob']
        # user_bio=self.validated_data['user_bio']

        # dob=dob.split("/")
        # dobO1=dob[2]+"-"+dob[1]+"-"+dob[0]
        # dobO=datetime.strptime(dobO1,'%Y-%m-%d')

        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        email = self.validated_data['email'].lower()
        mobile_number = self.validated_data['mobile_number']
        password = self.validated_data['password']
        latitude = self.validated_data['latitude']
        longitude = self.validated_data['longitude']
        user = User.objects.create_user(username=mobile_number, email=email, password=password, first_name=first_name,
                                        last_name=last_name)
        user.save()
        profileO = Userprofile.objects.create(user=user)
        # profileO.mobile_number=self.validated_data['mobile_number']
        # profileO.nationality=self.validated_data['nationality']
        # profileO.gender=self.validated_data['gender']
        profileO.code = self.validated_data['code']
        profileO.device_token = self.validated_data['device_token']
        profileO.device_type = self.validated_data['device_type']
        profileO.referral_code = self.validated_data.get('referral_code', "")
        profileO.location = Point(latitude, longitude, srid=4326)
        # profileO.dob=dob
        # profileO.user_bio=user_bio
        # profileO.notification_key=get_random_string(random.randint(50,60))
        profileO.save()
        # otp=random.randint(1000,10000)
        otp = 123456
        sotp = signup_otp.objects.create(user=user, otp=otp)
        sotp.expire = datetime.now() + timedelta(minutes=1440)
        sotp.save()
        return validated_data


class ChangePasswordSerializer(serializers.Serializer):
    model = User
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        new_password = data.get("new_password")
        if new_password.isalpha() == True:
            raise ValidationError('Password must be alpha numeric')
        if len(new_password) < 8:
            raise ValidationError('Password should 8 charcters long')
        if check_password(new_password) == False:
            raise ValidationError(
                'Pasword Should have at least one number.Password Should have at least one uppercase and one lowercase character.Password Should have at least one special symbol.Password Should be between 6 to 20 characters long.')
        return data


class UserCountrySerializer(ModelSerializer):
    class Meta:
        model = savecountry
        fields = '__all__'


class UserCountryCreateSerializer(Serializer):
    id = CharField(required=False)
    country = CharField(error_messages={'required': 'country key is required', 'blank': 'country is required'})
    state = CharField(error_messages={'required': 'state key is required', 'blank': 'state is required'})
    city = CharField(error_messages={'required': 'city key is required', 'blank': 'city is required'})

    def validate(self, data):
        request = self.context.get('request')
        data['user'] = request.user

        return data

    def create(self, validated_data):
        obj = savecountry.objects.create(**validated_data)
        validated_data['id'] = obj.id
        return validated_data


class NewsRequestCreateSerializer(Serializer):
    id = CharField(required=False)
    request_id = CharField(required=False)
    name = CharField(error_messages={'required': 'name is required', 'blank': 'name is required'}, max_length=400)
    service_provider = CharField(
        error_messages={'required': 'service_provider is required', 'blank': 'service_provider is required'},
        max_length=400)
    description = CharField(error_messages={'required': 'description is required', 'blank': 'description is required'},
                            max_length=400)

    def validate(self, data):

        if data.get("name") == "":
            raise ValidationError("name can not be empty")

        if data.get("description") == "":
            raise ValidationError("description can not be empty")

        if data.get("service_provider") == "":
            raise ValidationError("service_provider can not be empty")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        request_id = get_random_string(length=12, allowed_chars='ACTG1234567890')
        name = self.validated_data['name']
        description = self.validated_data['description']
        service_provider = self.validated_data['service_provider']
        user = UserReguest.objects.create(user=user, request_id=request_id, name=name, description=description,
                                          service_provider=service_provider)

        user.save()
        return validated_data


class NewsRequestSerializer(ModelSerializer):
    created_on = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = UserReguest
        fields = ['id', 'request_id', 'name', 'service_provider', 'description', 'status', 'created_on', 'user']


class UseSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'username']


class ListKeywordSerializer(ModelSerializer):
    class Meta:
        model = news_keyword
        fields = '__all__'


from time import gmtime, strftime


class CommentNewstSerializer(ModelSerializer):
    first_name = SerializerMethodField()
    last_name = SerializerMethodField()
    comment_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    def get_first_name(self, instance):
        return instance.user.first_name

    def get_last_name(self, instance):
        return instance.user.last_name

    class Meta:
        model = CommentNews
        fields = [

            "first_name",
            "last_name",
            "feedback",
            "comment_date",

        ]


class LikeNewsSerializer(ModelSerializer):
    # likes = serializers.IntegerField()

    user_count = serializers.SerializerMethodField()

    def get_user_count(self, obj):
        return obj.title.count("news")

    class Meta:
        model = LikeNews
        fields = [
            'user',
            # 'news',
            'like_date',
            'user_count',
            #  'likes',
        ]


class BitcoinNewsSerializer(ModelSerializer):
    user_comment_count = SerializerMethodField()
    user_likes_count = SerializerMethodField()
    when_added = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    def get_user_likes_count(self, obj):
        return obj.likenews_set.count()

    def get_user_comment_count(self, obj):
        return obj.commentnews_set.count()

    class Meta:
        model = News
        fields = [
            'id',
            'block',
            'title',
            'author',
            'description',
            'publishedAt',
            'content',
            'url',
            'urlToImage',
            'keyword',
            'when_added',
            'user',
            'user_likes_count',
            'user_comment_count',

        ]


class GroupMemberSer(ModelSerializer):
    group_id = SerializerMethodField()
    mobile_number = SerializerMethodField()
    full_name = SerializerMethodField()
    mobile_number = SerializerMethodField()

    def get_group_id(self, obj):
        return obj.chat_group.group_id

    def get_mobile_number(self, obj):
        return obj.member.username

    def get_full_name(self, obj):
        return obj.member.first_name + " " + obj.member.last_name

    class Meta:
        model = ChatGroupMember
        fields = ('group_id', "mobile_number", 'full_name')


class GroupCreateSerializer(Serializer):
    id = CharField(required=False)
    group_id = CharField(error_messages={'required': 'group_id is required', 'blank': 'group_id is required'},
                         max_length=400)
    name = CharField(error_messages={'required': 'name is required', 'blank': 'name is required'}, max_length=400)

    def validate(self, data):
        group_id = data.get('group_id')
        name = data.get('name')

        if ChatGroupAdmin.objects.filter(group_id=group_id).exists():
            raise APIException400({
                'success': "False",
                'message': 'This group_id is already exists',
            })
        if ChatGroupAdmin.objects.filter(name=name).exists():
            raise APIException400({
                'success': "False",
                'message': 'This group name is already exists',
            })
        if data.get("name") == "":
            raise ValidationError("group name can not be empty")

        if data.get("group_id") == "":
            raise ValidationError("group_id can not be empty")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        name = self.validated_data['name']
        group_id = self.validated_data['group_id']
        user = ChatGroupAdmin.objects.create(admin_name=user, name=name, group_id=group_id)
        user.save()
        return validated_data


class ShowUserSerializer(ModelSerializer):
    mobile_number = SerializerMethodField()
    full_name = SerializerMethodField()
    email = SerializerMethodField()
    user_id = SerializerMethodField()

    user_id = SerializerMethodField()

    def get_user_id(self, instance):
        return instance.user.id

    def get_mobile_number(self, instance):
        return instance.user.username

    def get_full_name(self, instance):
        return instance.user.first_name + " " + instance.user.last_name

    def get_email(self, instance):
        return instance.user.email

    class Meta:
        model = Userprofile
        fields = [
            'user_id',
            "mobile_number",
            "full_name",
            "email",
        ]

