import json
import requests
from requests.auth import HTTPBasicAuth

def auth_token_payload(**kwargs):
    payload = {
        "responseCode": "000",
        "status": "SUCCESS",
        "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTE2MywibWVyY2hhbnRJZCI6InRoZTFhcHAiLCJpYXQiOjE2Njc2NDQ1NDIsImV4cCI6MTY2NzY0NDg0Mn0.rtrAOz_8OjC_hKlY52caU_mGTRNjAN861uDpEfpI4K4",
        "expiresIn": "300",
        "tokenType": "Bearer",
        "walletBalance": 200000
}

def balance_and_Payment(**kwargs):
    payload = { 
        "responseCode": "999",
        "responseMessage": "Service not available"
}
    

def merchant_transaction_report(**kwargs):
    payload = {
        "transaction_from_date"
        "transaction_to_date"
    }

def merchant_pending_transaction(**kwargs):
    payload = {
    "responseCode": "000",
    "responseMessage"
    "status": "PendingTransaction"
    "transactionid"
    }

def merchant_check_status_transactionid(**kwargs):
    payload = {
    "responseCode"
    "responseMessage"
    "transactionstatus"
    "transactionid"
    }

def repost_pending_transaction_payload(**kwargs):
    payload = {
    "responseCode"
    "RepostPendingTransaction"
    "status"
}
    

def merchant_balance_check_payload(**kwargs):
    payload = {
        "balance_check"
            "amount"
        }
    

def transaction_list_payload(**kwargs):
    payload = {
        "transaction_list_fromdate"
        "transaction_list_todate"
    }





