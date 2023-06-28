
# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

account_sid = 'AC84e3fcec68ed594f5dd4f69b56ac3ea6'
auth_token = '8bb450c45a3261d3d0106471c47a2cf0'

def Send_SMS_User(otp,phonenumber,code):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
                     body=f"{otp} is your one time password (OTP). Please enter the OTP to proceed.",
                     from_='+14179893980',
                     to=code + phonenumber
                 )
    return message             

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

