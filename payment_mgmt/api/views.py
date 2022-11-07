from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (AllowAny,IsAuthenticated,)
from rest_framework_jwt.authentication import  JSONWebTokenAuthentication
from django.db import transaction
from django.db.models import Q
from .models import *


def auth_token():
	

	url = "https://qty.mbme.org:8080/v2/mbme/oauth/token"

	headers = {
		'Content-Type': 'application/json',
		'Accept': 'application/json'
	}
	payload = auth_token_payload()(responsecode=responsecode,accessToken=accessToken,expiresIn=expiresIn,tokentype=tokenType,wallletbalance=walletbalance)
	payload = json.dumps(payload)
	payload = json.loads(payload)
	# print(payload)
	# print(type(payload))
	try:
		resp = requests.post(url, json=payload, headers=headers)
		# Logger.objects.create(app_name='Rate Response Aramex.....',content=resp.json())
		resp = resp.json()
		if resp.get('token_key')['Value'] not in [0,0.00,'0','0.00']:
			MBMETokenKey.objects.create(responsecode=responsecode,status=token_key_success,accessToken=accessToken,expiresIn=expiresIn,tokentype=tokentype,walletBalance=walletBalance)
		return resp.get('token_key')['Value']
	except Exception as e:
		Logger.objects.create(app_name='mbme_auth.....',content=str(e))
		return ''

def balance_and_Payment(dd):
    
	url= "https://qty.mbme.org:8080/v2/api/payment"

	headers = {
		'Content-Type': 'application/json',
		'Accept': 'application/json'
	}
	payload = balance_and_payment_payload(transactionid=transactionid)
								            
	payload = json.dumps(payload)
	payload = json.loads(payload)
	# print(payload)
	# print(type(payload))
	try:
		resp = requests.post(url, json=payload, headers=headers)
		
		resp = resp.json()
		if resp.get('TotalAmount')['Value'] not in [0,0.00,'0','0.00']:
			MBMEBalanceAndPayment.objects.create()
		return resp.get('TotalAmount')['Value']
	except Exception as e:
		Logger.objects.create(app_name='Rate Response Error Aramex.....',content=str(e))
		return ''

def merchant_transaction_report(dd):
	
	url = "https://qty.mbme.org:8080/v2/mbme/merchantTransactions"

	headers = {
		'Content-Type': 'application/json',
		'Accept': 'application/json'
	}
	payload =merchant_ransaction_report_payload()
	payload = json.dumps(payload)
	payload = json.loads(payload)
	# print(payload)
	# print(type(payload))
	try:
		resp = requests.post(url, json=payload, headers=headers)
		# Logger.objects.create(app_name='Rate Response Aramex.....',content=resp.json())
		resp = resp.json()
		if resp.get('TotalAmount')['Value'] not in [0,0.00,'0','0.00']:
			MBMEMerchantTransactionReport.create(sender_city=dd.sender_detail.city,receiver_city=dd.receiver_detail.city,weight=round(float(dd.package_detail.actual_weight),2),rate=resp.get('TotalAmount')['Value'],company_id=1)
		return resp.get('TotalAmount')['Value']
	except Exception as e:
		Logger.objects.create(app_name='Rate Response Error Aramex.....',content=str(e))
		return ''


def merchant_pending_transaction(dd):
	
	url = "https://qty.mbme.org:8080/v2/mbme/merchantTransactions"

	headers = {
		'Content-Type': 'application/json',
		'Accept': 'application/json'
	}
	payload =merchant_pending_transaction(dd)(sender_region=sender_region,sender_city=sender_city,sender_postal_code=sender_postal_code,
										  receiver_region=receiver_region,receiver_city=receiver_city,receiver_postal_code=receiver_postal_code,
										  weight=weight)
	payload = json.dumps(payload)
	payload = json.loads(payload)
	# print(payload)
	# print(type(payload))
	try:
		resp = requests.post(url, json=payload, headers=headers)
		# Logger.objects.create(app_name='Rate Response Aramex.....',content=resp.json())
		resp = resp.json()
		if resp.get('TotalAmount')['Value'] not in [0,0.00,'0','0.00']:
			MBMEMerchantPendingTransaction.objects.create(sender_city=dd.sender_detail.city,receiver_city=dd.receiver_detail.city,weight=round(float(dd.package_detail.actual_weight),2),rate=resp.get('TotalAmount')['Value'],company_id=1)
		return resp.get('TotalAmount')['Value']
	except Exception as e:
		Logger.objects.create(app_name='Rate Response Error Aramex.....',content=str(e))
		return ''


def merchant_check_status_transactionid(dd):
	
	url = "https://qty.mbme.org:8080/v2/mbme/checkTransaction"

	headers = {
		'Content-Type': 'application/json',
		'Accept': 'application/json'
	}
	payload = merchant_check_status_transactionid(dd)()
	payload = json.dumps(payload)
	payload = json.loads(payload)
	# print(payload)
	# print(type(payload))
	try:
		resp = requests.post(url, json=payload, headers=headers)
		# Logger.objects.create(app_name='Rate Response Aramex.....',content=resp.json())
		resp = resp.json()
		if resp.get('TotalAmount')['Value'] not in [0,0.00,'0','0.00']:
			MBMEMerchantCheckStatuTransaction.objects.create()
		return resp.get('TotalAmount')['Value']
	except Exception as e:
		Logger.objects.create(app_name='Rate Response Error Aramex.....',content=str(e))
		return ''

def repost_pending_transaction_(dd):
	
	url = "https://qty.mbme.org:8080/v2/mbme/processTransaction"

	headers = {
		'Content-Type': 'application/json',
		'Accept': 'application/json'
	}
	payload =repost_pending_transaction_payload(dd)()
	payload = json.dumps(payload)
	payload = json.loads(payload)
	# print(payload)
	# print(type(payload))
	try:
		resp = requests.post(url, json=payload, headers=headers)
		# Logger.objects.create(app_name='Rate Response Aramex.....',content=resp.json())
		resp = resp.json()
		if resp.get('TotalAmount')['Value'] not in [0,0.00,'0','0.00']:
			MBMERepostPendingTransaction.objects.create()
		return resp.get('TotalAmount')['Value']
	except Exception as e:
		Logger.objects.create(app_name='Rate Response Error Aramex.....',content=str(e))
		return ''

def merchant_balance_check(dd):
	
	url = "https://qty.mbme.org:8080/v2/mbme/merchantBalance"

	headers = {
		'Content-Type': 'application/json',
		'Accept': 'application/json'
	}
	payload = merchant_balance_check_payload(dd)()
	payload = json.dumps(payload)
	payload = json.loads(payload)
	# print(payload)
	# print(type(payload))
	try:
		resp = requests.post(url, json=payload, headers=headers)
		# Logger.objects.create(app_name='Rate Response Aramex.....',content=resp.json())
		resp = resp.json()
		if resp.get('TotalAmount')['Value'] not in [0,0.00,'0','0.00']:
			MBMEMerchantBalance.objects.create(sender_city=dd.sender_detail.city,receiver_city=dd.receiver_detail.city,weight=round(float(dd.package_detail.actual_weight),2),rate=resp.get('TotalAmount')['Value'],company_id=1)
		return resp.get('TotalAmount')['Value']
	except Exception as e:
		Logger.objects.create(app_name='Rate Response Error Aramex.....',content=str(e))
		return ''

def transaction_list(dd):
	'from_date'
	'to_date'
	
	url = "https://qty.mbme.org:8080/v2/mbme/merchantTransactions"

	headers = {
		'Content-Type': 'application/json',
		'Accept': 'application/json'
	}
	payload = transaction_list_payload(dd)()
	payload = json.dumps(payload)
	payload = json.loads(payload)
	# print(payload)
	# print(type(payload))
	try:
		resp = requests.post(url, json=payload, headers=headers)
		# Logger.objects.create(app_name='Rate Response Aramex.....',content=resp.json())
		resp = resp.json()
		if resp.get('TotalAmount')['Value'] not in [0,0.00,'0','0.00']:
			MBMETransaction.objects.create()
		return resp.get('TotalAmount')['Value']
	except Exception as e:
		Logger.objects.create(app_name='Rate Response Error Aramex.....',content=str(e))
		return ''