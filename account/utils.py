
# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']

def Send_SMS_User(otp,phonenumber):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
                     body=f"Your OTP {otp} has been successfully registered",
                     from_='+14179893980',
                     to='+91'+phonenumber
                 )
    return message             

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

