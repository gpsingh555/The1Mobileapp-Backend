# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = 'AC84e3fcec68ed594f5dd4f69b56ac3ea6'
print(account_sid)
auth_token = '8bb450c45a3261d3d0106471c47a2cf0'
print(auth_token)
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body="Your OTP has been successfully registered",
                     from_='+14179893980',
                     to='+919528344428'
                 )

print(message.sid)
