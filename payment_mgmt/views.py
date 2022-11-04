from django.shortcuts import render

class GenerateToken(APIVIEW):
    data={
    "username":
    "password"
    "accesstoken"
    "status"
    "expiresin"
    "token_type"
    "walllet_balance"
    }
    res=GenerateToken({access_token})
    retur
Response({'data':res},status=200)

class WalletBalance(APIVIEW):
    data:{
    "transaction_id"
    "username"
    "response"
    }
    res=WalletBalance ({'id':'JHJKJKKHJ'})
    retur
Response({'data':res},status=200)


class Transaction_Report(APIVIEW):
    data:{
    "from_date"
    "to_date"
    }
    res=Transaction_Report({'id':'JHJKJKKHJ'})
    retur 
Response({'data':res},status=200)

class Find_my_transaction_id(APIVIEW):
    data:{
        "transaction_id"
        "transaction_status"
    } 
    res=Find_my_transaction_id({'id':'JHJKJKKHJ'})
    retur 
Response({'data':res},status=200)

class All_Pending_Transaction(APIVIEW):
    data:{
        "from_date"
        "to_date"
    } 
    res=All_Pending_Transaction   ({'id':'JHJKJKKHJ'})
    retur
Response({'data':res},status=200)

class Process_Pending_Payment(APIVIEW):
    data:{
        "uniqueid"
        "transactionid"
    }
    res=Process_Pending_Payment   ({'id':'JHJKJKKHJ'})
    retur
Response({'data':res},status=200)