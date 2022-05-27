from django.urls import path
from .views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('signup',signup.as_view()),
    path('verify_signup_otp',verify_signup_otp.as_view()),
    path("resend_otp",resend_otp.as_view()),
    path('login',login.as_view()),
    path('forget_password_otp',send_forgetpassword_otp.as_view()),
    path('verify_foget_otp',verify_forgetpassword_otp.as_view()),
    path('forget_password',forget_password.as_view()),
    path('change-password', ChangePasswordView.as_view()),
    path('contect',Contect.as_view()),
    path('savecountry',UserAddressListApiView.as_view()),
    path('delete_country',delete_country.as_view()),
    path('BitcoinNews',BitcoinNews.as_view()),
    path('userrequestnews',UserRequestNews.as_view()),
    path('view_name',view_name.as_view()),
    path('likenewsapi',LikeNewsApi.as_view()),
    path('commentnews',CommentNewsApi.as_view()),
    path('commentnewsview',CommentNewsViewApi.as_view()),
    path('listkeyword',ListKeyword.as_view()),
    path('UpdateProfile',UpdateProfile.as_view()),
    path('EmailUpdate',EmailUpdate.as_view()),
    path('MobileUpdate',MobileUpdate.as_view()),
    path('DeleteAccount',DeleteAccount.as_view()),
    path('delete_otp',deleteaccount_otp.as_view()),
    path('GetTokenAzure',GetTokenAzure.as_view()),
    
    path('groupmemberview',GroupMemberView.as_view()),
    path('CreateGroupAPIView',CreateGroupAPIView.as_view()),
    path('AddGroupMemberAPI',AddGroupMemberAPI.as_view()),
    path('ShowAllUser',ShowAllUser.as_view()),
    
    

]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


