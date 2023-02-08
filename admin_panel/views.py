from django.core.checks import messages
from django.http import request
from django.shortcuts import redirect, render
from rest_framework.views import APIView
from .models import *
from account.models import *
from django.contrib.auth import login, authenticate, logout
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, timedelta
from django.utils.crypto import get_random_string
from django.http import HttpResponse
from rest_framework.response import Response
import re
from django.db.models import Q
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
import json
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .serializers import *
from account.api.serializers import *
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_204_NO_CONTENT,
    HTTP_201_CREATED,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_404_NOT_FOUND,
)

from rest_framework import status
from rest_framework import generics
from rest_framework.generics import *
import requests
from urllib.parse import urlencode


# Create your views here.
def check_password(password):
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    pat = re.compile(reg)
    mat = re.search(pat, password)
    if mat:
        return True
    else:
        return False


def check_user_valid(user):
    if user.is_staff == True:
        return True
    else:
        return False


def check_blank_or_null(data):
    status = True
    for x in data:
        if x == "" or x == None:
            status = False
            break
        else:
            pass
    return status


class login_view(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if User.objects.filter(email=email).exists():
            u = User.objects.get(email=email).username
            user = authenticate(username=u, password=password)
            if user is not None:
                if user.is_staff == True:
                    token, created = Token.objects.get_or_create(user=user)
                    token.save()
                    returnMessage = {"status": "success", "message": "You are successfully login", 'token': token.key, }
                    return HttpResponse(json.dumps(returnMessage), content_type='application/javascript; charset=utf8',
                                        status=HTTP_200_OK)
                else:
                    return Response({"status": "fail", 'message': 'you are not authorized'},
                                    status=HTTP_400_BAD_REQUEST)
            else:
                return Response({"status": "fail", 'message': 'Email and password is incorrect'},
                                status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "fail", 'messages': 'Email Id Does not exists'}, status=HTTP_400_BAD_REQUEST)


class Logout(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logout Successlly...'}, status=HTTP_200_OK)


class cms(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        totaluser = User.objects.all().count()
        totalactiveuser = User.objects.filter(is_active=True).count()
        totalandroiduser = Userprofile.objects.filter(device_type=1).count()
        totaliphoneuser = Userprofile.objects.filter(device_type=2).count()

        data = {
            'totaluser': totaluser,
            'totalactiveuser': totalactiveuser,
            'totalandroiduser': totalandroiduser,
            'totaliphoneuser': totaliphoneuser,

        }
        return Response({'message': 'Success', 'data': data}, status=HTTP_200_OK)


class view_users(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              user_mgmt=True).exists():
            context = {}
            noti = Userprofile.objects.filter(is_subadmin=False).order_by("-id")
            page = request.data.get('page', 1)
            paginator = Paginator(noti, 500)
            try:
                notiO = paginator.page(page)
            except PageNotAnInteger:
                notiO = paginator.page(1)
            except EmptyPage:
                notiO = paginator.page(paginator.num_pages)
            serializer = UserprofileSerializer(notiO, many=True)
            context['Userprofile'] = serializer.data
            context['page_limit'] = len(list(notiO.paginator.page_range))
            return Response(context, status=HTTP_200_OK)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class BlockUserAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              user_mgmt=True).exists():
            user_id = request.data.get('user_id')
            try:
                user = User.objects.get(id=user_id)
            except:
                return Response({
                    'success': 'False',
                    'message': 'No user to block'
                }, status=HTTP_400_BAD_REQUEST)

            if user.is_active == True:
                user.is_active = False
                user.save()
                return Response({
                    'success': 'True',
                    'message': 'User blocked successfully'
                }, status=HTTP_200_OK)
            else:
                return Response({
                    'success': 'False',
                    'message': 'Already Blocked'
                }, status=HTTP_400_BAD_REQUEST)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class UnblockUserAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              user_mgmt=True).exists():
            user_id = request.data.get('user_id')
            try:
                user = User.objects.get(id=user_id)
            except:
                return Response({
                    'success': 'False',
                    'message': 'No user to unblock'
                }, status=HTTP_400_BAD_REQUEST)

            if user.is_active == False:
                user.is_active = True
                user.save()
                return Response({
                    'success': 'True',
                    'message': 'User unblocked successfully'
                }, status=HTTP_200_OK)
            else:
                return Response({
                    'success': 'False',
                    'message': 'Already unblocked'
                }, status=HTTP_400_BAD_REQUEST)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class DeleteUserAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              user_mgmt=True).exists():
            user_id = request.data.get('user_id')
            print('user_id', user_id)
            try:
                obj = User.objects.get(id=user_id)
            except:
                return Response({
                    'success': 'False',
                    'message': 'No user to delete'
                }, status=HTTP_400_BAD_REQUEST)

            obj.delete()
            return Response({
                'success': 'True',
                'message': 'User deleted successfully',
            }, status=HTTP_200_OK)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class UserProfileDetailsAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              user_mgmt=True).exists():
            user_id = request.data.get('user_id')
            try:
                obj = Userprofile.objects.get(user__id=user_id)
            except:
                return Response({
                    'success': 'False',
                    'message': 'No user found',
                }, status=HTTP_404_NOT_FOUND)

            serializer = UserprofileSerializer(obj, many=False)
            data = serializer.data
            return Response({
                'success': 'True',
                'message': 'Data retrieved successfully',
                'data': data
            }, status=HTTP_200_OK)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class datefilter(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              user_mgmt=True).exists():
            fromdate = request.data.get('fromdate')
            todate = request.data.get('todate')
            try:
                dob = fromdate.split("/")
                dobO1 = dob[2] + "-" + dob[1] + "-" + dob[0]
                print(dobO1)
                dobO = datetime.strptime(dobO1, "%Y-%m-%d")

            except:
                raise ValidationError("Date Formte not correct")

            try:
                dob = todate.split("/")
                dobO1 = dob[2] + "-" + dob[1] + "-" + dob[0]
                dob1 = datetime.strptime(dobO1, '%Y-%m-%d')
            except:
                raise ValidationError("Date Formte not correct")

            obj = Userprofile.objects.filter(Q(sampledate__gte=dobO) & Q(sampledate__lte=dob1))

            serializer = UserprofileSerializer(obj, many=True)
            data = serializer.data
            return Response({
                'success': 'True',
                'message': 'Data retrieved successfully',
                'data': data
            }, status=HTTP_200_OK)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():

            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',

            }
            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class send_otp_foget(APIView):
    def post(self, request):
        email = request.data['email']
        print("first", email)
        if check_blank_or_null([email]) and User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            print(user)
            if forget_otp.objects.filter(user=user).exists():
                fo = forget_otp.objects.get(user=user)
                print(fo)
                fo.delete()
            otp = 123456
            print(otp)
            fo = forget_otp.objects.create(user=user)
            print(fo)
            fo.otp = otp
            fo.secret_key = get_random_string(45)
            fo.expire = datetime.now() + timedelta(minutes=1440)
            fo.save()
            return Response({'message': 'Otp has been sent to your Email Id successfull'}, status=HTTP_200_OK)
        return Response({'message': "Email does not exists"}, status=HTTP_400_BAD_REQUEST)


class verify_forget_otp(APIView):
    def post(self, request):
        email = request.data['email']
        otp = request.data['otp']
        if check_blank_or_null([email, otp]) and User.objects.filter(email=email).exists() and User.objects.filter(
                email=email).exists():
            user = User.objects.get(email=email)
            if forget_otp.objects.filter(user=user, expire__gte=datetime.now(), otp=otp).exists():
                fo = forget_otp.objects.get(user=user, expire__gte=datetime.now(), otp=otp)
                data = {'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        }
                if fo.attempt < 5:
                    return Response({'secret_key': fo.secret_key, "message": "otp is verified", 'data': data},
                                    status=HTTP_200_OK)
                else:
                    return Response({"message": "Your have completed all attempt.Please send otp again"},
                                    status=HTTP_400_BAD_REQUEST)
            else:
                fo = forget_otp.objects.get(user=user)
                fo.attempt += 1
                fo.save()
                return Response({"message": "Incorrect Otp"}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Email Id is not exists"}, status=HTTP_400_BAD_REQUEST)


class forget_password_admin(APIView):
    def post(self, request):
        password = request.data['password']
        secret_key = request.data['secret_key']
        if check_blank_or_null([password]):
            if password.isalpha() == False and check_password(password):
                if forget_otp.objects.filter(expire__gte=datetime.now(), secret_key=secret_key).exists():
                    fo = forget_otp.objects.get(expire__gte=datetime.now(), secret_key=secret_key)
                    user = User.objects.get(email=fo.user.email)
                    user.set_password(password)
                    user.save()
                    return Response({"message": "Password has been successfully changed"}, status=HTTP_200_OK)
                else:
                    return Response({"message": "secret key is not exists"}, status=HTTP_400_BAD_REQUEST)
            else:
                return Response({
                                    'message': 'Password must alpha numeric.Pasword Should have at least one number.Password Should have at least one uppercase and one lowercase character.Password Should have at least one special symbol.Password Should be between 6 to 20 characters long.'},
                                status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "secret key can not empty"}, status=HTTP_400_BAD_REQUEST)


class CreateSubAdminApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        qs = Userprofile.objects.filter(is_subadmin=True).order_by('-id')
        data = UserprofileSerializer(qs, many=True).data
        return Response({'data': data, 'message': 'sub admin list'}, status=HTTP_200_OK)

    def post(self, request):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              subadmin_mgmt=True).exists():
            serializer = CreateSubAdminSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                user = User.objects.get(email=request.data['email'].lower())
                token, created = Token.objects.get_or_create(user=user)

                return Response(
                    {'data': serializer.data, 'message': 'Sub Admin Created Successfully', 'Token': token.key},
                    status=HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class UpdateSubAdminPermission(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              subadmin_mgmt=True).exists():
            user_id = request.data.get("user_id")
            first_name = request.data.get("first_name")
            country = request.data.get("country")
            password = request.data.get("password")
            dashboard = request.data.get('dashboard', False)
            user_mgmt = request.data.get('user_mgmt', False)
            subadmin_mgmt = request.data.get('subadmin_mgmt', False)
            news_mgmt = request.data.get('news_mgmt', False)
            geolocation_mgmt = request.data.get('geolocation_mgmt', False)

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

            if news_mgmt == "true":
                news_mgmt = True
            else:
                news_mgmt = False

            if geolocation_mgmt == "true":
                geolocation_mgmt = True
            else:
                geolocation_mgmt = False

            if check_blank_or_null([user_id]) and User.objects.filter(pk=user_id).exists():
                user = User.objects.get(pk=user_id)
                user.first_name = first_name
                user.set_password(password)
                user.save()
                profileO = Userprofile.objects.get(user=user)
                profileO.country = country
                profileO.isotp_verified = True
                profileO.save()
                obj, created = SubAdminPermission.objects.get_or_create(user=user)
                print(obj)
                obj.dashboard = dashboard
                obj.user_mgmt = user_mgmt
                obj.subadmin_mgmt = subadmin_mgmt
                obj.news_mgmt = news_mgmt
                obj.geolocation_mgmt = geolocation_mgmt
                obj.save()
                return Response({'message': 'Subadmin And Subadmin Permissions Updated Successfully'},
                                status=HTTP_200_OK)
            else:
                context['error'] = "User is not exists"
                context['status'] = "fail"
                return Response(context, status=HTTP_400_BAD_REQUEST)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class subadmin_permission(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context = {}
        user_id = request.data.get("user_id")
        if check_blank_or_null([user_id]) and User.objects.filter(pk=user_id).exists():
            user = User.objects.get(pk=user_id)
            sap = SubAdminPermission.objects.get(user=user)
            context['permission'] = SubAdminPermissionSerializer(sap, many=False).data
        return Response(context, status=HTTP_200_OK)

    def get(self, request):
        qs = SubAdminPermission.objects.filter(subadmin_mgmt=True).order_by('-id')
        data = SubAdminPermissionSerializer(qs, many=True).data
        return Response({'data': data, 'message': 'sub admin list'}, status=HTTP_200_OK)


class view_country(APIView):
    def get(self, request):
        addr = country.objects.all().order_by("name")
        serializer = countrySerializer(addr, many=True)
        return Response({'data': serializer.data}, status=HTTP_200_OK)


class view_state(APIView):
    def get(self, request):
        pk = request.GET['id']
        if country.objects.filter(pk=pk).exists():
            c = country.objects.get(pk=pk)
            addr = state.objects.filter(country=c).order_by("name")
            serializer = stateSerializer(addr, many=True)
            return Response({'data': serializer.data}, status=HTTP_200_OK)
        else:
            return Response({'error': 'Country Id is not exists'}, status=HTTP_400_BAD_REQUEST)


class view_city(APIView):
    def get(self, request):
        pk = request.GET['id']
        if state.objects.filter(pk=pk).exists():
            c = state.objects.get(pk=pk)
            addr = city.objects.filter(state=c).order_by("name")
            serializer = citySerializer(addr, many=True)
            return Response({'data': serializer.data}, status=HTTP_200_OK)
        else:
            return Response({'error': 'State Id is not exists'}, status=HTTP_400_BAD_REQUEST)


class setupallcity(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        file = request.FILES['file']
        data_set = file.read().decode('UTF-8')
        for column in data_set.split("\n"):
            data = column.split(",")
            try:
                print(data)
                if len(data) > 0:
                    c, __ = country.objects.get_or_create(name=data[1])
                    c.save()
                    s, __ = state.objects.get_or_create(name=data[2], country=c)
                    s.save()
                    cc, __ = city.objects.get_or_create(name=data[0], state=s)
                    cc.save()
                else:
                    print(data)
            except:
                print("errorerror")
                print(data)
                print("errrorerror")
        return Response({'data': "success"}, status=HTTP_200_OK)


class CreateRegionApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        qs = Region.objects.all().order_by('country')
        data = RegionListSerializer(qs, many=True).data
        return Response({'data': data, 'message': 'Region list'}, status=HTTP_200_OK)

    def post(self, request):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              subadmin_mgmt=True).exists():
            serializer = CreateRegionSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({'data': serializer.data, 'message': 'Region Created Successfully'}, status=HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class UpdateRegionApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              subadmin_mgmt=True).exists():
            region_id = request.data.get("region_id")
            country = request.data.get("country")
            state = request.data.get('state')
            city = request.data.get('city')
            lat = request.data.get('lat')
            lng = request.data.get('lng')
            radius = request.data.get('radius')

            if check_blank_or_null([region_id]) and Region.objects.filter(pk=region_id).exists():
                user = Region.objects.get(pk=region_id)
                user.country = country
                user.state = state
                user.city = city
                user.radius = radius
                user.lat = lat
                user.lng = lng
                user.save()

                return Response({'message': 'Region Updated Successfully'}, status=HTTP_200_OK)
            else:
                context['error'] = "Region is not exists"
                context['status'] = "fail"
                return Response(context, status=HTTP_400_BAD_REQUEST)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class DeleteRegionAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              user_mgmt=True).exists():
            region_id = request.data.get('region_id')
            print('user_id', region_id)
            try:
                obj = Region.objects.get(id=region_id)
            except:
                return Response({
                    'success': 'False',
                    'message': 'No region to delete'
                }, status=HTTP_400_BAD_REQUEST)

            obj.delete()
            return Response({
                'success': 'True',
                'message': 'Region deleted successfully',
            }, status=HTTP_200_OK)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class BlockRegionAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              user_mgmt=True).exists():
            region_id = request.data.get('region_id')
            try:
                user = Region.objects.get(id=region_id)
            except:
                return Response({
                    'success': 'False',
                    'message': 'No user to block'
                }, status=HTTP_400_BAD_REQUEST)

            if user.is_active == True:
                user.is_active = False
                user.save()
                return Response({
                    'success': 'True',
                    'message': 'Region blocked successfully'
                }, status=HTTP_200_OK)
            else:
                return Response({
                    'success': 'False',
                    'message': 'Already Blocked'
                }, status=HTTP_400_BAD_REQUEST)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class UnblockRegionAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              user_mgmt=True).exists():
            region_id = request.data.get('region_id')
            try:
                user = Region.objects.get(id=region_id)
            except:
                return Response({
                    'success': 'False',
                    'message': 'No user to unblock'
                }, status=HTTP_400_BAD_REQUEST)

            if user.is_active == False:
                user.is_active = True
                user.save()
                return Response({
                    'success': 'True',
                    'message': 'Region unblocked successfully'
                }, status=HTTP_200_OK)
            else:
                return Response({
                    'success': 'False',
                    'message': 'Already unblocked'
                }, status=HTTP_400_BAD_REQUEST)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class finduser(APIView):
    def post(self, request):
        city = request.data.get('city')
        if check_blank_or_null([city]) and Userprofile.objects.filter(city=city).exists():
            profileO = Userprofile.objects.filter(city=city)
            data = {

                'total user': profileO.count(),
                "users": UserprofileSerializer(profileO, many=True).data
            }
            return Response({'message': 'suceess', 'data': data}, status=HTTP_200_OK)
        else:
            return Response({'message': 'not founds '}, status=HTTP_200_OK)


class view_stateby_country(APIView):
    def get(self, request):
        name = request.GET['name']
        if country.objects.filter(name=name).exists():
            c = country.objects.get(name=name)
            addr = state.objects.filter(country=c).order_by("name")
            serializer = stateSerializer(addr, many=True)
            return Response({'data': serializer.data}, status=HTTP_200_OK)
        else:
            return Response({'error': 'Country Name is not exists'}, status=HTTP_400_BAD_REQUEST)


class view_cityby_state(APIView):
    def get(self, request):
        name = request.GET['name']
        if state.objects.filter(name=name).exists():
            c = state.objects.get(name=name)
            addr = city.objects.filter(state=c).order_by("name")
            serializer = citySerializer(addr, many=True)
            return Response({'data': serializer.data}, status=HTTP_200_OK)
        else:
            return Response({'error': 'State Name is not exists'}, status=HTTP_400_BAD_REQUEST)


class View_News(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              user_mgmt=True).exists():
            context = {}
            noti = News.objects.all().order_by("-id")
            page = request.data.get('page', 1)
            paginator = Paginator(noti, 500)
            try:
                notiO = paginator.page(page)
            except PageNotAnInteger:
                notiO = paginator.page(1)
            except EmptyPage:
                notiO = paginator.page(paginator.num_pages)
            serializer = NewsListSerializer(notiO, many=True)
            context['News'] = serializer.data
            context['page_limit'] = len(list(notiO.paginator.page_range))
            return Response(context, status=HTTP_200_OK)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class DeleteNewsAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              user_mgmt=True).exists():
            news_id = request.data.get('news_id')
            print('user_id', news_id)
            try:
                obj = UserReguest.objects.get(id=news_id)
            except:
                return Response({
                    'success': 'False',
                    'message': 'No News Request to delete'
                }, status=HTTP_400_BAD_REQUEST)

            obj.delete()
            return Response({
                'success': 'True',
                'message': 'News Request deleted successfully',
            }, status=HTTP_200_OK)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class BlockNewsAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              user_mgmt=True).exists():
            news_id = request.data.get('news_id')
            try:
                user = News.objects.get(id=news_id)
            except:
                return Response({
                    'success': 'False',
                    'message': 'No News to block'
                }, status=HTTP_400_BAD_REQUEST)

            if user.block == False:
                user.block = True
                user.save()
                return Response({
                    'success': 'True',
                    'message': 'News blocked successfully'
                }, status=HTTP_200_OK)
            else:
                return Response({
                    'success': 'False',
                    'message': 'Already Blocked'
                }, status=HTTP_400_BAD_REQUEST)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class UnblockNewsAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              user_mgmt=True).exists():
            news_id = request.data.get('news_id')
            try:
                user = News.objects.get(id=news_id)
            except:
                return Response({
                    'success': 'False',
                    'message': 'No news to unblock'
                }, status=HTTP_400_BAD_REQUEST)

            if user.block == True:
                user.block = False
                user.save()
                return Response({
                    'success': 'True',
                    'message': 'news unblocked successfully'
                }, status=HTTP_200_OK)
            else:
                return Response({
                    'success': 'False',
                    'message': 'Already unblocked'
                }, status=HTTP_400_BAD_REQUEST)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class ViewNewsRequest(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              user_mgmt=True).exists():
            context = {}
            noti = UserReguest.objects.all().order_by("-id")
            page = request.data.get('page', 1)
            paginator = Paginator(noti, 500)
            try:
                notiO = paginator.page(page)
            except PageNotAnInteger:
                notiO = paginator.page(1)
            except EmptyPage:
                notiO = paginator.page(paginator.num_pages)
            serializer = NewsRequestSerializer(notiO, many=True)
            context['NewsRequest'] = serializer.data
            context['page_limit'] = len(list(notiO.paginator.page_range))
            return Response(context, status=HTTP_200_OK)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class NewsAprroveAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              user_mgmt=True).exists():
            news_id = request.data.get('news_id')
            try:
                user = UserReguest.objects.get(id=news_id)
            except:
                return Response({
                    'success': 'False',
                    'message': 'No user to block'
                }, status=HTTP_400_BAD_REQUEST)

            if user.status == 'Pending' or 'Rejected':
                user.status = 'Approved'
                user.save()
                return Response({
                    'success': 'True',
                    'message': 'Approved  successfully'
                }, status=HTTP_200_OK)
            else:
                return Response({
                    'success': 'False',
                    'message': 'Already Approved'
                }, status=HTTP_400_BAD_REQUEST)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class NewsRejectAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              user_mgmt=True).exists():
            news_id = request.data.get('news_id')
            try:
                user = UserReguest.objects.get(id=news_id)
            except:
                return Response({
                    'success': 'False',
                    'message': 'No user to block'
                }, status=HTTP_400_BAD_REQUEST)

            if user.status == 'Pending' or 'Approved':
                user.status = 'Rejected'
                user.save()
                return Response({
                    'success': 'True',
                    'message': 'Rejected  successfully'
                }, status=HTTP_200_OK)
            else:
                return Response({
                    'success': 'False',
                    'message': 'Already Rejected'
                }, status=HTTP_400_BAD_REQUEST)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class SendUserChatSingle(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        massage = request.data.get('massage')
        attechment = request.data.get('attechment')
        # try:
        dr = UserChat.objects.create(sender=request.user, massage=massage, attechment=attechment)
        print(dr)
        dr.save()
        return Response({'data': 'Massage Send successfully'})
        # except:
        #     return Response({'data':'Massage Not Send'})


# class SendUserChat(APIView):
#     def post(self,request):
#         try:
#             mem=ChatGroupMember.objects.get(member=request.user,chat_group_id=request.data.get('chat_group_id'),is_accept=True)
#         except:
#             return Response('invalid credentials')
#         try:

#             dr=UserChat.objects.create(chat_group_id=request.data.get('chat_group_id'),sender=mem,massage=request.data['massage'],attechment=request.data['attechment'])
#             dr.save()
#             return Response({'data':'Create data successfully'})


#         except :
#             return Response({'error':'something wrong'})


def search_place(value, location):
    print(location)
    place_endpoint = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    place_params = {
        'key': google_api_key,
        'query': value,
        'location': location
    }
    urlencode_param = urlencode(place_params)
    place_url = f'{place_endpoint}?{urlencode_param}'
    r = requests.get(place_url)
    if r.status_code not in range(200, 299):
        return Response({
            'success': 'False',
            'message': 'No matched record found'
        }, status=HTTP_400_BAD_REQUEST)
    python_data = json.loads(r.text)
    return python_data


# class newsmgmtview(APIView):
#     def post(self,request):
#         try:
#             news_image = request.FILES['news_image']
#         except:
#             news_image =""
#         news_title=request.data.get('news_title')
#         imp_content=request.data.get('imp_content')
#         category=request.data.get('category')
#         description=request.data.get('description')
# class User_detailsAPIView):
#     permission_classes = (IsAdminUser,)
#     def get(self,request,*args,**kwargs):
#         context={}
#         user_id=request.GET.get("user_id")
#         noti=Userprofile.objects.all().order_by("-id")
#         page = request.GET.get('page', 1)
#         paginator = Paginator(noti, 20)
#         try:
#             notiO = paginator.page(page)
#         except PageNotAnInteger:
#             notiO = paginator.page(1)
#         except EmptyPage:
#             notiO = paginator.page(paginator.num_pages)
#         serializer=UserprofileSerializer(notiO,many=True)    
#         context['Userprofile']=serializer.data
#         context['page_limit']=len(list(notiO.paginator.page_range))
#         return Response(context,status=HTTP_200_OK)


class EditSubAdminAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        context = {}
        if request.user.is_staff == True or SubAdminPermission.objects.filter(user=request.user,
                                                                              subadmin_mgmt=True).exists():
            user_id = request.data.get('user_id')
            first_name = request.data.get('first_name')
            country = request.data.get('country')
            mobile_number = request.data.get('mobile_number')
            admin_id = request.data.get('admin_id')
            email = request.data.get('email')
            password = request.data.get('password')

            if check_blank_or_null([first_name, country, password]):
                if User.objects.filter(pk=user_id).exists() == True:
                    user = User.objects.get(pk=user_id)
                    user.first_name = first_name
                    # user.username=mobile_number
                    # user.email=email
                    user.set_password(password)
                    user.save()
                    profileO = Userprofile.objects.get(user=user)
                    profileO.country = country
                    profileO.isotp_verified = True
                    user.save()
                    return Response({"message": "update  has been successfully "}, status=HTTP_200_OK)
                else:
                    return Response({"message": "User not founds"}, status=HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "Please fill details"}, status=HTTP_400_BAD_REQUEST)
        else:
            context['message'] = "You are not authorized for this operation"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class apply_permission(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        context = {}
        context['permission'] = ['dashboard', 'user_mgmt', "subadmin_mgmt"]
        return Response(context, status=HTTP_200_OK)

    def post(self, request):
        context = {}
        user_id = request.data.get("user_id")
        permission = request.data.get("permission")
        if check_blank_or_null([user_id]) and User.objects.filter(pk=user_id).exists():
            user = User.objects.get(pk=user_id)
            subadminpermissionO, __ = SubAdminPermission.objects.get_or_create(user=user)
            try:
                for x in permission:
                    if x == "dashboard":
                        subadminpermissionO.dashboard = True
                    if x == "user_mgmt":
                        subadminpermissionO.user_mgmt = True
                    if x == "subadmin_mgmt":
                        subadminpermissionO.subadmin_mgmt = True
                subadminpermissionO.save()
                context['message'] = "permission has been added successfully"
                context['status'] = "success"
                return Response(context, status=HTTP_200_OK)
            except:
                context['error'] = "permission format is not right"
                context['status'] = "fail"
                return Response(context, status=HTTP_400_BAD_REQUEST).data
        else:
            context['error'] = "User is not exists"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)

    def delete(self, request):
        context = {}
        user_id = request.data.get("user_id")
        permission = request.data.get("permission")
        if check_blank_or_null([user_id]) and User.objects.filter(pk=user_id).exists():
            user = User.objects.get(pk=user_id)
            subadminpermissionO, __ = SubAdminPermission.objects.get_or_create(user=user)
            try:
                for x in permission:
                    if x == "dashboard":
                        subadminpermissionO.dashboard = False
                    if x == "user_mgmt":
                        subadminpermissionO.user_mgmt = False
                    if x == "subadmin_mgmt":
                        subadminpermissionO.subadmin_mgmt = False
                subadminpermissionO.save()
                context['message'] = "permission has been remove successfully"
                context['status'] = "success"
                return Response(context, status=HTTP_200_OK)
            except:
                context['error'] = "permission format is not right"
                context['status'] = "fail"
                return Response(context, status=HTTP_400_BAD_REQUEST)
        else:
            context['error'] = "User is not exists"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)
