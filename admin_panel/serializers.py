from copy import error
import re
#from typing_extensions import Required
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from rest_framework import fields
from rest_framework.serializers import ModelSerializer, FloatField,Serializer, CharField, ImageField, SerializerMethodField,EmailField,DateField
import random
from rest_framework.fields import EmailField, Field, IntegerField
from rest_framework.exceptions import APIException
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from account.models import *
from .models import *

class APIException400(APIException):
    status_code = 400
class APIException401(APIException):
    status_code = 401
from rest_framework import serializers
from django.contrib.auth.models import User



def check_password(password):
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    pat = re.compile(reg)
    mat = re.search(pat, password)
    if mat:
        return True
    else:
        return False


class UserprofileSerializer(ModelSerializer):
  username=SerializerMethodField()
  first_name=SerializerMethodField()
  last_name=SerializerMethodField()
  email=SerializerMethodField()
  latitude=SerializerMethodField()
  longitude=SerializerMethodField()
  is_active=SerializerMethodField()
  date_joined=SerializerMethodField()
  subadmin_permission=SerializerMethodField()
  
  user_id=SerializerMethodField()
  def get_user_id(self,instance):
    return instance.user.id

  def get_username(self,instance):
    return instance.user.username
  def get_first_name(self,instance):
    return instance.user.first_name
  def get_last_name(self,instance):
    return instance.user.last_name
  def get_email(self,instance):
    return instance.user.email      
  def get_latitude(self,instance):
    if instance.location == None:
      return 0.0
    else:
      return instance.location.x
  def get_longitude(self,instance):
    
    if instance.location == None:
      return 0.0
    else:
      return instance.location.y

  def get_is_active(self,instance):
    return instance.user.is_active
  
  def get_date_joined(self,instance):
    return instance.user.date_joined

  def get_subadmin_permission(self,instance):
    try:
        obj= SubAdminPermission.objects.filter(user=instance)
        data= SubAdminPermissionSerializer(obj,many=True).data
        print("hello Permission",data)
        return data   
    except:
        print('hello khan')
        return None

  class Meta:
    model = Userprofile
    fields = [
          "id",
          'user_id',
          "username",
          "first_name",
          "last_name",
          "email",
          "latitude",
          "longitude",
          "mobile_number",
          "code",
          "dob",
          "image",
          "country",
          "state",
          "city",
          "device_type",
          "referral_code",
          "isotp_verified",
          "is_profile_complete",
          "is_subadmin",
          "is_active",
         "date_joined",
         "subadmin_permission",
          ]


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
            raise ValidationError('Pasword Should have at least one number.Password Should have at least one uppercase and one lowercase character.Password Should have at least one special symbol.Password Should be between 6 to 20 characters long.')

        return data
            

class CreateSubAdminSerializer(Serializer):
    dashboard = serializers.BooleanField(required=False)
    user_mgmt = serializers.BooleanField(required=False)
    subadmin_mgmt = serializers.BooleanField(required=False)
    geolocation_mgmt = serializers.BooleanField(required=False)
    news_mgmt = serializers.BooleanField(required=False)
    country = CharField(required=False,max_length=400)
    #city = CharField(required=False,max_length=400)
    mobile_number = CharField(required=False,max_length=20)
    email = serializers.CharField(allow_blank=True)
    #email = EmailField(allow_blank=True,required=False)
    password=CharField(required=False)
    admin_id=CharField(required=False,max_length=5000)
	#last_name=CharField(error_messages={'required':'last_name is required', 'blank':'last_name is required'},max_length=5000)
	
    first_name=CharField(required=False,max_length=100)
    #role=CharField(required=False,max_length=100)
  
    def validate(self, data):
        email = data.get('email').lower()
        password = data.get("password")
        #first_name = data.get("first_name")
        mobile_number=data.get('mobile_number')
        admin_id=data.get('country_id')
        country=data.get('country')
        dashboard =data.get('dashboard',False)
        user_mgmt=data.get('user_mgmt',False)
        subadmin_mgmt=data.get('subadmin_mgmt',False)
        geolocation_mgmt=data.get('geolocation_mgmt',False)
        news_mgmt=data.get('news_mgmt',False)
        
        #city=data.get('city)

        if dashboard == "true":
            dashboard = True
        else:
            dashboard = False

        if user_mgmt == "true":
            user_mgmt = True
        else:
            user_mgmt = False

        if subadmin_mgmt == "true":
            subadmin_mgmt = True
        else:
            subadmin_mgmt = False

        if geolocation_mgmt == "true":
            geolocation_mgmt = True
        else:
            geolocation_mgmt = False

        if news_mgmt == "true":
            news_mgmt = True
        else:
            news_mgmt = False


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
      
         
        if User.objects.filter(email=email).exists():
            raise APIException400({
                            'success':"False",
                            'message':'This email is already registered',
                            })

        if User.objects.filter(username=mobile_number).exists():
            raise APIException400({
                            'success':"False",
                            'message':'Mobile Number is already registered',
                            })

        if password.isalpha() == True:
            raise ValidationError('Password must be alpha numeric')
        #if gender not in ['male','female']:
            #raise ValidationError('Gender must be male and female') 
        if len(password) < 8:
            raise APIException400({
                'success':"False",
                'message':'Password should 8 charcters long',
                })
        if check_password(password) == False:
            raise APIException400({
                'success':'False',
                'message':'Pasword Should have at least one number.Password Should have at least one uppercase and one lowercase character.Password Should have at least one special symbol.Password Should be between 6 to 20 characters long.',
                })
        
        return data

    def create(self,validated_data):
        
        first_name=self.validated_data['first_name']
        mobile_number=self.validated_data['mobile_number']
        email = self.validated_data['email'].lower()
        dashboard =self.validated_data['dashboard']
        user_mgmt=self.validated_data['user_mgmt']
        subadmin_mgmt=self.validated_data['subadmin_mgmt']
        geolocation_mgmt=self.validated_data['geolocation_mgmt']
        news_mgmt=self.validated_data['news_mgmt']

        #username=self.validated_data['username']
        password = self.validated_data['password']
        #code = self.validated_data['code']
        user=User.objects.create_superuser(username=mobile_number,email=email,first_name=first_name,password=password)
        user.save()
        code=random.randint(0000,9999)
        profileO=Userprofile.objects.create(user=user,code=code)
        #profileO.mobile_number=self.validated_data['mobile_number']
        #profileO.city=self.validated_data['city']
        #profileO.role=self.validated_data['role']
        #code=random.randint(0000,9999)
        #profileO.code=self.validated_data['admin_id']
        #profileO.device_token=self.validated_data['device_token']
        #profileO.device_type=self.validated_data['device_type']
        profileO.country=self.validated_data['country']
        profileO.is_subadmin=True
        profileO.isotp_verified=True
        #profileO.notification_key=get_random_string(random.randint(50,60))
        profileO.save()
        obj,created=SubAdminPermission.objects.get_or_create(user=user)
        print(obj)
        obj.dashboard = dashboard
        obj.user_mgmt = user_mgmt
        obj.subadmin_mgmt = subadmin_mgmt
        obj.geolocation_mgmt = geolocation_mgmt
        obj.news_mgmt = news_mgmt
        obj.save()
        return validated_data


class SubAdminPermissionSerializer(ModelSerializer):
    class Meta:
        model=SubAdminPermission
        fields='__all__'


class countrySerializer(ModelSerializer):
    class Meta:
        model = country
        fields = '__all__'


class stateSerializer(ModelSerializer):
    class Meta:
        model = state
        fields = '__all__'        


class citySerializer(ModelSerializer):
    class Meta:
        model = city
        fields = '__all__'


class CreateRegionSerializer(Serializer):

    country = CharField(required=False,max_length=30)
    state = CharField(required=False,max_length=30)
    city = CharField(required=False,max_length=30)
    radius=IntegerField(required=False)
    lat=CharField(required=False,max_length=30)
    lng=CharField(required=False,max_length=30)
    
    def create(self,validated_data):
        
        country=self.validated_data['country']
        state=self.validated_data['state']
        city = self.validated_data['city']
        radius=self.validated_data['radius']
        lat=self.validated_data['lat']
        lng=self.validated_data['lng']

        profileO=Region.objects.create(country=country,state=state,city=city,radius=radius,lat=lat,lng=lng)
        profileO.save()
        
        return validated_data


class RegionListSerializer(ModelSerializer):
    class Meta:
        model=Region
        fields='__all__'


class NewsListSerializer(ModelSerializer):
    class Meta:
        model=News
        fields='__all__'




















'''     
class EditSubAdminSerializer(ModelSerializer):
    admin_id   = serializers.CharField(required=False,allow_blank=True)
    email    = serializers.CharField(required=False)
    mobile_number = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False,allow_blank=True)
    #city = serializers.CharField(error_messages={"required":"city key is required"})
    #role = serializers.CharField(error_messages={"required":"role key is required"})
    password = serializers.CharField(required=False)
    
    class Meta:
        model  = Userprofile
        fields = ['mobile_number','email','country','password','admin_id','first_name']


    def validate(self,data):
        email    = data['email']
        #username=data['username']
        mobile_number = data['mobile_number']
        country=data['country']
        #city         = data['city']
        password=data['password']
        admin_id=data['admin_id']
        
    
        
        # if not password or password =='':
        #     raise APIException400({
        # 'success' : 'False',
        # 'message' : 'password is required'
        # })    

        # if not mobile_number or mobile_number =='':
        #     raise APIException400({
        #         'success':'False',
        #         'message':'phone number is required'
        # })

        # if not email or email =='':
        #     raise APIException400({
        #         'success':'False',
        #         'message':'email is required'
        # })

        if password.isalpha() == True:
            raise ValidationError('Password must be alpha numeric')
        #if gender not in ['male','female']:
            #raise ValidationError('Gender must be male and female') 
        if len(password) < 8:
            raise ValidationError('Password should 8 charcters long')
        if check_password(password) == False:
            raise ValidationError('Pasword Should have at least one number.Password Should have at least one uppercase and one lowercase character.Password Should have at least one special symbol.Password Should be between 6 to 20 characters long.')
 

        # if User.objects.filter(email=email).exists()==False:
        #     user=request.user
        #     user.email=email
        #     raise APIException400({
        #                     'success':"False",
        #                     'message':'This email is already registered',
        #                     })

        # if User.objects.filter(username=username).exists():
        #     raise APIException400({
        #                     'success':"False",
        #                     'message':'Username is already registered',
        #                     })
        # if Userprofile.objects.filter(mobile_number=mobile_number).exists():
        #     raise APIException400({
        #                     'success':"False",
        #                     'message':'Mobile Number is already registered',
        #                     })

        return data 

    def create(self,validated_data):
        country   = validated_data['country']
        email    = validated_data['email']
        mobile_number      = validated_data['mobile_number']
        first_name         = validated_data['first_name']
        #username=validated_data['username']
        password=validated_data['password']
       #role=validated_data['role']
        admin_id=validated_data['admin_id']

        #state      = validated_data['state']
       
        #user      = self.context.get('user')
        user = User.objects.filter(id=admin_id)
        otherUser = Userprofile.objects.filter(user=user).first()
        if not otherUser:
            raise APIException({
        'success' : 'False',
        'message' : 'This user is not registerd'
        })

        user.username = mobile_number
        user.first_name=first_name
        user.email = email
        user.password=password
        user.save() 

        #otherUser.mobile_number = mobile_number
        #otherUser.city = city
        otherUser.country=country
        #otherUser.role=role
        otherUser.code=admin_id
        #otherUser.zipcode      = zipcode

        otherUser.save()

        return validated_data

'''