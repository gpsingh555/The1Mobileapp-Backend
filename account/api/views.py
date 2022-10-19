import logging
from curses.ascii import US
import json
import random
import re
from datetime import date, datetime, timedelta
from account.cron import upload_news
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core import paginator
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from requests.api import post
from rest_framework import generics, request, serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import *
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from ..models import *
from .serializers import *
from .serializers import ChangePasswordSerializer
from admin_panel.serializers import *
from admin_panel.models import *


import os
from azure.communication.identity import CommunicationIdentityClient, CommunicationUserIdentifier

connection_string = os.environ["connection_string"]

logger = logging.getLogger('accounts')


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


def check_email(email):
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if (re.search(regex, email)):
        return True
    else:
        return False


def check_password(password):
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    pat = re.compile(reg)
    mat = re.search(pat, password)
    if mat:
        return True
    else:
        return False


class signup(APIView):
    def post(self, request):
        serializer = signupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(email=request.data['email'].lower())
            profileO = Userprofile.objects.get(user=user)
            data = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'mobile_number': user.username,
                'dob': profileO.dob,
                'code': profileO.code,
                'image': profileO.image.url,
                'country': profileO.country,
                'state': profileO.state,
                'city': profileO.city,
                'user_bio': profileO.role,
                'device_type': profileO.device_type,
                'device_token': profileO.device_token,
                "latitude": profileO.location.x,
                "longitude": profileO.location.y
            }
            token, created = Token.objects.get_or_create(user=user)
            return Response({'message': 'success', 'data': data, 'token': token.key}, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class verify_signup_otp(APIView):
    def post(self, request):
        mobile_number = request.data['mobile_number']
        otp = request.data['otp']
        if check_blank_or_null([mobile_number]) and User.objects.filter(username=mobile_number).exists():
            user = User.objects.get(username=mobile_number)
            print(user)
            profileO = Userprofile.objects.get(user=user)
            print(profileO)
            if profileO.isotp_verified == False:
                if signup_otp.objects.filter(user=user, expire__gte=datetime.now(), otp=otp).exists():
                    sotp = signup_otp.objects.get(
                        user=user, expire__gte=datetime.now(), otp=otp)
                    if sotp.attempt < 5:
                        sotp = profileO.isotp_verified = True
                        profileO.save()
                        sotp = signup_otp.objects.get(
                            user=user, expire__gte=datetime.now(), otp=otp)
                        sotp.is_used = True
                        print(sotp)
                        sotp.save()
                        token, created = Token.objects.get_or_create(user=user)
                        return Response({'message': 'Account has been successfully verified', 'token': token.key}, status=HTTP_200_OK)
                    else:
                        return Response({'message': 'Your ALl Attempt is done please resend the verification otp'}, status=HTTP_200_OK)
                else:
                    sotp = signup_otp.objects.get(user=user)
                    sotp.attempt += 1
                    sotp.save()
                    return Response({'message': 'incorrect otp please resend the otp again'}, status=HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Account Is already verified'}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Mobile Number is not exists'}, status=HTTP_400_BAD_REQUEST)


class resend_otp(APIView):
    def post(self, request):
        mobile_number = request.data['mobile_number']
        if check_blank_or_null([mobile_number]) and User.objects.filter(username=mobile_number).exists():
            user = User.objects.get(username=mobile_number)
            profileO = Userprofile.objects.get(user=user)
            if profileO.isotp_verified == False:
                if signup_otp.objects.filter(user=user).exists():
                    fo = signup_otp.objects.get(user=user)
                    fo.delete()
                # otp=random.randint(100000,1000000)
                otp = 123456
                fo = signup_otp.objects.create(
                    user=user, expire=datetime.now()+timedelta(minutes=1440), otp=otp)

                fo.save()
                return Response({'message': 'Otp has been sent to your mobile number successfull'}, status=HTTP_200_OK)
            else:
                return Response({'message': 'Account Is already verified'}, status=HTTP_400_BAD_REQUEST)

        return Response({'message': "Mobile Number Is not exists"}, status=HTTP_400_BAD_REQUEST)


class login(APIView):
    def post(self, request):
        logger.debug("*******************login api called*******************")
        logger.debug(datetime.now())
        password = request.data.get("password")
        mobile_number = request.data.get("mobile_number")
        device_type = request.data.get('device_type')
        device_token = request.data.get('device_token')
        code = request.data.get('code')
        quickblox_id = request.data.get('quickblox_id')
        logger.debug(self.request.data)

        if mobile_number is None or password is None:
            logger.debug('Please provide both mobile and password')
            return Response({'message': 'Please provide both mobile and password '},
                            status=HTTP_400_BAD_REQUEST)
        user = authenticate(username=mobile_number, password=password)
        if not user:
            logger.debug('Invalid Credentials')
            returnMessage = {'message': 'Invalid Credentials'}
            return HttpResponse(
                json.dumps(returnMessage),
                content_type='application/javascript; charset=utf8',
                status=HTTP_400_BAD_REQUEST
            )
        profileO = Userprofile.objects.get(user=user)
        if profileO.isotp_verified == False:
            if signup_otp.objects.filter(user=user).exists():
                fo = signup_otp.objects.get(user=user)
                fo.delete()
                # otp=random.randint(1000,10000)
            otp = 123456
            fo = signup_otp.objects.create(
                user=user, expire=datetime.now()+timedelta(minutes=1440), otp=otp)
            fo.save()
            token, created = Token.objects.get_or_create(user=user)
            token.save()
            profileO = Userprofile.objects.get(user=user)
            profileO.device_type = device_type
            profileO.device_token = device_token
            profileO.save()
            data = {'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'mobile_number': user.username,
                    'country': profileO.country,
                    'state': profileO.state,
                    'city': profileO.city,
                    'image': profileO.image.url,
                    'device_type': profileO.device_type,
                    'device_token': profileO.device_token,
                    'isotp_verified': profileO.isotp_verified,
                    'code': profileO.code,
                    # 'mobile_number':User.username,
                    }
            logger.debug('Your account is not verified')
            returnMessage = {
                'message': 'Your account is not verified', 'token': token.key}
            return HttpResponse(
                json.dumps(returnMessage),
                content_type='application/javascript; charset=utf8',
                status=HTTP_400_BAD_REQUEST

            )
        if device_type in ['1', '2'] and len(device_token) < 500:
            user.device_token = device_token
            user.device_type = device_type
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
            token.save()
            profileO = Userprofile.objects.get(user=user)
            profileO.quickblox_id = quickblox_id
            profileO.save()
            if profileO.code == code:
                data = {'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'mobile_number': user.username,
                        'country': profileO.country,
                        'state': profileO.state,
                        'city': profileO.city,
                        'image': profileO.image.url,
                        'device_type': profileO.device_type,
                        'device_token': profileO.device_token,
                        'isotp_verified': profileO.isotp_verified,
                        'code': profileO.code,
                        'quickblox_id': profileO.quickblox_id,
                        # 'mobile_number':User.username,

                        }
                logger.debug('Responce data for Login User ')
                logger.debug(data)
                returnToken = {'token': token.key,
                               "message": "success", 'data': data}
                return HttpResponse(
                    json.dumps(returnToken),
                    content_type='application/javascript; charset=utf8',
                    status=HTTP_200_OK
                )
            else:
                logger.debug('country code not match')
                returnToken = {"message": "country code not match"}
                return HttpResponse(
                    json.dumps(returnToken),
                    content_type='application/javascript; charset=utf8',
                    status=HTTP_400_BAD_REQUEST
                )

        else:
            logger.debug('Device type and device token is incorrect')
            returnMessage = {
                'message': 'Device type and device token is incorrect'}
            return HttpResponse(
                json.dumps(returnMessage),
                content_type='application/javascript; charset=utf8',
                status=HTTP_400_BAD_REQUEST
            )


class send_forgetpassword_otp(APIView):
    def post(self, request):
        mobile_number = request.data['mobile_number']
        code = request.data['code']
        print("first", mobile_number)
        if check_blank_or_null([mobile_number, code]) and User.objects.filter(username=mobile_number).exists():
            user = User.objects.get(username=mobile_number)
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
            fo.expire = datetime.now()+timedelta(minutes=1440)
            fo.save()
            return Response({'message': 'Otp has been sent to your Mobile Number successfull'}, status=HTTP_200_OK)
        return Response({'message': "Mobile Number  Is not exists"}, status=HTTP_400_BAD_REQUEST)


class verify_forgetpassword_otp(APIView):
    def post(self, request):
        mobile_number = request.data['mobile_number']
        otp = request.data['otp']
        if check_blank_or_null([mobile_number, otp]) and User.objects.filter(username=mobile_number).exists() and User.objects.filter(username=mobile_number).exists():
            user = User.objects.get(username=mobile_number)
            if forget_otp.objects.filter(user=user, expire__gte=datetime.now(), otp=otp).exists():
                fo = forget_otp.objects.get(
                    user=user, expire__gte=datetime.now(), otp=otp)
                profileO = Userprofile.objects.get(user=user)
                data = {'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'device_token': profileO.device_token,
                        'device_type': profileO.device_type,
                        }
                if fo.attempt < 5:

                    return Response({'secret_key': fo.secret_key, "message": "otp is verified", 'data': data}, status=HTTP_200_OK)
                else:
                    return Response({"message": "Your have completed all attempt.Please send otp again"}, status=HTTP_400_BAD_REQUEST)
            else:
                fo = forget_otp.objects.get(user=user)
                fo.attempt += 1
                fo.save()
                return Response({"message": "Incorrect Otp"}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Mobile Number is not exists"}, status=HTTP_400_BAD_REQUEST)


class forget_password(APIView):
    def post(self, request):
        password = request.data['password']
        secret_key = request.data['secret_key']
        if check_blank_or_null([password]):
            if password.isalpha() == False and check_password(password):
                if forget_otp.objects.filter(expire__gte=datetime.now(), secret_key=secret_key).exists():
                    fo = forget_otp.objects.get(
                        expire__gte=datetime.now(), secret_key=secret_key)
                    user = User.objects.get(email=fo.user.email)
                    user.set_password(password)
                    user.save()
                    return Response({"message": "Password has been successfully changed"}, status=HTTP_200_OK)
                else:
                    return Response({"message": "secret key is not exists"}, status=HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Password must alpha numeric.Pasword Should have at least one number.Password Should have at least one uppercase and one lowercase character.Password Should have at least one special symbol.Password Should be between 6 to 20 characters long.'}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "secret key can not empty"}, status=HTTP_400_BAD_REQUEST)


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


class Contect(APIView):
    def post(self, request):
        mobile_number = request.data.get('mobile_number')
        if check_blank_or_null([mobile_number]) and User.objects.filter(username=mobile_number).exists():
            user = User.objects.get(username=mobile_number)
            profileO = Userprofile.objects.get(user=user)
            data = {
                'key found': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'mobile_number': user.username,
                'email': user.email,
                'code': profileO.code,
                # 'longitude':profileO.location.longitude,
                'country': profileO.country,
                'state': profileO.state,
                'city': profileO.city,
                'is_active': user.is_active,
                'date_joined': user.date_joined,
            }

    #     client = CommunicationIdentityClient.from_connection_string(connection_string)

        # # Create an identity
    #     identity = client.create_user()
    #     print("\nCreated an identity with ID: " + identity.properties['id'])

        # #Store the identity to issue access tokens later
    #     existingIdentity = identity

        # # Issue an access token with the "voip" scope for an identity
    #     token_result = client.get_token(identity, ["voip"])
    #     expires_on = token_result.expires_on.strftime("%d/%m/%y %I:%M %S %p")
    #     print("\nIssued an access token with 'voip' scope that expires at " + expires_on + ":")
    #     print(token_result.token)

        # # Create an identity and issue an access token within the same request
    #     identity_token_result = client.create_user_and_token(["voip"])
    #     identity = identity_token_result[0].properties['id']
    #     token = identity_token_result[1].token
    #     expires_on = identity_token_result[1].expires_on.strftime("%d/%m/%y %I:%M %S %p")
    #     #print("\nCreated an identity with ID: " + identity)
    #     #print("\nIssued an access token with 'voip' scope that expires at " + expires_on + ":")
    #     #print(token)

        return Response({'message': 'Token Get Success', 'data': data})


class UserAddressListApiView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        data = []
        if pk:
            qs = savecountry.objects.filter(id=pk, user=request.user)
            print(qs, 'qs.................')
            if qs.exists():
                data = UserCountrySerializer(
                    qs, context={'request': request}, many=True).data
        else:
            queryset = savecountry.objects.filter(
                user=request.user).order_by('-id')
            if queryset.exists():
                data = UserCountrySerializer(
                    queryset, context={'request': request}, many=True).data

        return Response({'data': data}, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = UserCountryCreateSerializer(
            data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(serializer.data)
        return Response(serializer.data, status=HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs.get('id')
        model = get_object_or_404(savecountry.objects.all(), pk=pk)
        model.delete()
        return Response({"message": "User Save Country has been deleted."}, status=HTTP_200_OK)


class delete_country(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        pk = request.data.get('pk')
        if check_blank_or_null([pk]) and savecountry.objects.filter(user=request.user, pk=pk).exists():
            addr = savecountry.objects.get(user=request.user, pk=pk)
            addr.delete()
            return Response({'data': "Country successfully delete"}, status=HTTP_200_OK)
        return Response({'message': "Country Is not exists"}, status=HTTP_400_BAD_REQUEST)


class UserRequestNews(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = NewsRequestCreateSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'Request has been successfully Send'}, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def get(self, request):
        addr = UserReguest.objects.filter(user=request.user)
        serializer = NewsRequestSerializer(addr, many=True)
        return Response({'data': serializer.data}, status=HTTP_200_OK)


class view_name(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            obj = User.objects.get(id=user.id)
        except:
            return Response({
                'success': 'False',
                'message': 'No user found',
            }, status=HTTP_400_BAD_REQUEST)

        serializer = UseSerializer(obj)
        data = serializer.data
        return Response({
            'success': 'True',
            'message': 'Data retrieved successfully',
            'data': data
        }, status=HTTP_200_OK)


class LikeNewsApi(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user
        id = request.data.get('id')
        try:
            news = News.objects.get(id=id)
        except:
            return Response({
                'success': 'False',
                'message': 'News Not found',
            }, status=HTTP_400_BAD_REQUEST)
        liked = False
        like = LikeNews.objects.filter(user=user, news=news)
        if like:
            like.delete()
        else:
            liked = True
            LikeNews.objects.create(user=user, news=news)

        resp = {
            'liked': liked,
            'count': LikeNews.objects.filter(news=news).count()
        }

        response = json.dumps(resp)
        return HttpResponse(response, content_type="application/json")


class CommentNewsApi(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user
        feedback = request.data.get('feedback')
        id = request.data.get('id')
        try:
            news = News.objects.get(id=id)
        except:
            return Response({
                'success': 'False',
                'message': 'No news found',
            }, status=HTTP_400_BAD_REQUEST)

        CommentNews.objects.create(user=user, news=news, feedback=feedback)

        resp = {
            'feedback': feedback,

            'count': CommentNews.objects.filter(news=news).count()
        }
        count = LikeNews.objects.all().count()
        response = json.dumps(resp)
        return HttpResponse(response, content_type="application/json")


class CommentNewsViewApi(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        id = request.data.get('id')
        news = News.objects.get(id=id)
        addr = CommentNews.objects.filter(news=news)
        serializer = CommentNewstSerializer(addr, many=True)
        return Response({'data': serializer.data, 'count_comment': CommentNews.objects.filter(news=news).count()}, status=HTTP_200_OK)


class ListKeyword(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        addr = news_keyword.objects.all()
        serializer = ListKeywordSerializer(addr, many=True)
        return Response({'data': serializer.data}, status=HTTP_200_OK)


class BitcoinNews(APIView):
    def post(self, request):
        context = {}
        keyword = request.data.get('keyword')
        if check_blank_or_null([keyword]) and News.objects.filter(keyword=keyword).exists():
            #newsO=News.objects.filter(keyword=keyword).order_by("-id") or News.objects.filter(block=False) [:30]
            newsO = News.objects.filter(
                keyword=keyword, block=False).order_by("-id")[:30]
            data = {
                "News": BitcoinNewsSerializer(newsO, many=True).data,
                "total_news": newsO.count(),
                "total_count": LikeNews.objects.all().count()
            }
            return Response({'message': 'suceess', 'data': data}, status=HTTP_200_OK)
        else:
            return Response({'message': 'KeyWord Not Find'}, status=HTTP_200_OK)


class UpdateProfile(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        context = {}
        first_name = request.data.get("first_name")
        dob = request.data.get("dob")
        user_bio = request.data.get("user_bio")
        last_name = request.data.get("last_name")
        if check_blank_or_null([first_name, last_name, user_bio, dob]):
            try:
                dob = dob.split("/")
                dobO1 = dob[2]+"-"+dob[1]+"-"+dob[0]
                dobO = datetime.strptime(dobO1, '%Y-%m-%d')
            except:
                return Response({"message": "Date format is not right"}, status=HTTP_400_BAD_REQUEST)

            user = request.user
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            profileO = Userprofile.objects.get(user=user)
            profileO.user_bio = user_bio
            profileO.dob = dobO
            profileO.save()
            data = {'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'mobile_number': user.username,
                    'dob': profileO.dob.strftime("%d/%m/%Y") if profileO.dob != None else "",
                    'country': profileO.country,
                    'state': profileO.state,
                    'city': profileO.city,
                    'image': profileO.image.url,
                    'user_bio': profileO.user_bio,


                    }
            return Response({"message": "Profile is successfully updated", "data": data}, status=HTTP_200_OK)

        else:
            context['error'] = "Fields are required"
            context['status'] = "fail"
            return Response(context, status=HTTP_400_BAD_REQUEST)


class EmailUpdate(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        old_email = request.data.get('old_email')
        new_email = request.data.get('new_email').lower()
        if check_blank_or_null([new_email, old_email]):
            if new_email == request.user.email:
                user = request.user
                user.save()
                data = {
                    'email': user.email

                }
                return Response({"message": "Email Id is successfully updated", "data": data}, status=HTTP_200_OK)

            else:
                if User.objects.filter(email=new_email).exists() == False:

                    user = request.user
                    user.email = new_email

                    user.save()

                    data = {
                        'email': user.email

                    }
                    return Response({"message": "Email Id is successfully updated", "data": data}, status=HTTP_200_OK)
                else:
                    return Response({"message": "Email is already exists"}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Enter New and Old Email Id'})


class MobileUpdate(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        mobile_number = request.data.get('mobile_number')
        if check_blank_or_null([mobile_number]):
            if mobile_number == request.user.username:
                user = request.user
                user.username = mobile_number
                data = {
                    'mobile_number': user.username
                }
                user.is_active = True
                user.save()
                profileO = Userprofile.objects.get(user=user)
                profileO.isotp_verified = False
                print("hello")
                profileO.save()
                if signup_otp.objects.filter(user=user).exists():
                    fo = signup_otp.objects.get(user=user)
                    fo.delete()
                    otp = 123456
                    fo = signup_otp.objects.create(
                        user=user, expire=datetime.now()+timedelta(minutes=1440), otp=otp)
                    fo.save()
                    return Response({'message': 'Otp has been sent to your mobile number successfull', 'data': data}, status=HTTP_200_OK)
                else:
                    return Response({'message': 'Account Is already verified'}, status=HTTP_400_BAD_REQUEST)

            else:
                if User.objects.filter(username=mobile_number).exists() == False:
                    user = request.user
                    user.username = mobile_number
                    data = {
                        'mobile_number': user.username
                    }
                    user.is_active = True
                    user.save()
                    profileO = Userprofile.objects.get(user=user)
                    profileO.isotp_verified = False
                    print("hello")
                    profileO.save()
                    if signup_otp.objects.filter(user=user).exists():
                        fo = signup_otp.objects.get(user=user)
                        fo.delete()
                        otp = 123456
                        fo = signup_otp.objects.create(
                            user=user, expire=datetime.now()+timedelta(minutes=1440), otp=otp)
                        fo.save()
                        return Response({'message': 'Otp has been sent to your mobile number successfull', 'data': data}, status=HTTP_200_OK)
                    else:
                        return Response({'message': 'Account Is already verified'}, status=HTTP_400_BAD_REQUEST)

                #     data={
                #         'mobile_number':user.username
                #     }
                #     return Response({'message':'mobile number update','data':data},status=HTTP_200_OK)
                else:
                    return Response({"message": "mobile is already exists"}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Enter Valid Mobile Number'})


class deleteaccount_otp(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        mobile_number = request.data['mobile_number']
        if check_blank_or_null([mobile_number]) and User.objects.filter(username=mobile_number).exists():
            user = User.objects.get(username=mobile_number)
           # profileO=Userprofile.objects.get(user=user)
           # if profileO.isotp_verified == False:
            if signup_otp.objects.filter(user=user).exists():
                fo = signup_otp.objects.get(user=user)
                fo.delete()
            # otp=random.randint(100000,1000000)
            otp = 123456
            fo = signup_otp.objects.create(
                user=user, expire=datetime.now()+timedelta(minutes=1440), otp=otp)

            fo.save()
            return Response({'message': 'Otp has been sent to your mobile number successfull'}, status=HTTP_200_OK)
        else:
            return Response({'message': 'Mobile Number Is not exist'}, status=HTTP_400_BAD_REQUEST)

       # return Response({'message':"Mobile Number Is not exists"}, status=HTTP_400_BAD_REQUEST)


class DeleteAccount(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        otp = request.data['otp']
        if signup_otp.objects.filter(user=user, expire__gte=datetime.now(), otp=otp).exists():
            sotp = signup_otp.objects.get(
                user=user, expire__gte=datetime.now(), otp=otp)
            if sotp.attempt < 5:
                sotp = signup_otp.objects.get(
                    user=user, expire__gte=datetime.now(), otp=otp)
                sotp.is_used = True
                print(sotp)
                sotp.save()
                user.delete()
                return Response({'message': 'Account has been Delete successfully', }, status=HTTP_200_OK)
            else:
                return Response({'message': 'Your ALl Attempt is done please resend the verification otp'}, status=HTTP_200_OK)
        else:
            return Response({"result": "Otp Is incorrect"})


class GroupMemberView(APIView):
    #permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        group_id = request.data.get('group_id')
        try:
            # ChatGroupMember.objects.get(member=request.user,chat_group=group_id,is_accept=True)
            qss = ChatGroupAdmin.objects.get(group_id=group_id)

        except:
            return Response('Invalid Group')
        try:
            stu = ChatGroupMember.objects.filter(chat_group_id=qss)
            serializer = GroupMemberSer(stu, many=True)
            return Response({'Group member': serializer.data})
        except:
            return Response({'error': 'something wrong'})


class CreateGroupAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = GroupCreateSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'Group has been successfully Created'}, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ShowAllUser(APIView):
    def get(self, request):
        addr = Userprofile.objects.filter(is_subadmin=False).order_by("-id")
        serializer = ShowUserSerializer(addr, many=True)
        return Response({'data': serializer.data}, status=HTTP_200_OK)


class AddGroupMemberAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        group_id = request.data.get('group_id')
        user_id = request.data.get('user_id')
        qss = ChatGroupAdmin.objects.get(group_id=group_id)
        user = User.objects.get(pk=user_id)
        ChatGroupMember.objects.get_or_create(
            chat_group=qss, member=user, is_accept=True)

        return Response({'message': 'User Added Successfully'})


class GetTokenAzure(APIView):
    def get(self, request):
        client = CommunicationIdentityClient.from_connection_string(
            connection_string)

        # Create an identity
        identity = client.create_user()
        print("\nCreated an identity with ID: " + identity.properties['id'])

        # Store the identity to issue access tokens later
        existingIdentity = identity

        # Issue an access token with the "voip" scope for an identity
        token_result = client.get_token(identity, ["voip"])
        expires_on = token_result.expires_on.strftime("%d/%m/%y %I:%M %S %p")
        print(
            "\nIssued an access token with 'voip' scope that expires at " + expires_on + ":")
        print(token_result.token)

        # Create an identity and issue an access token within the same request
        identity_token_result = client.create_user_and_token(["voip"])
        identity = identity_token_result[0].properties['id']
        token = identity_token_result[1].token
        expires_on = identity_token_result[1].expires_on.strftime(
            "%d/%m/%y %I:%M %S %p")
        #print("\nCreated an identity with ID: " + identity)
        #print("\nIssued an access token with 'voip' scope that expires at " + expires_on + ":")
        # print(token)

        return Response({'message': 'Token Get Success', 'Token': token, 'Identity': identity, 'expires_on': expires_on})
