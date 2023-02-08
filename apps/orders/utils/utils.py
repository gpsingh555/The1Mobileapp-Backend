from datetime import datetime
from random import randint

from django.conf import settings


def get_transaction_id():
    """
    The format of TransactionID is YYMMDDHHMMSSss+Randomnumber(0-9)+<KioskID>
    ex: if Kiosk ID Id is 2050,and the generated random number is 4 then the transaction
    ID will be 2011041320223242050 which generated 2020 November 4th 1.20 PM and 22 second 32 microseconds.
    """
    return datetime.now().strftime("%y%m%d%H%M%S%f")+str(randint(0, 9))+settings.MBME_MERCHANT_ID
