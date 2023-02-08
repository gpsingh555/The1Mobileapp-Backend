from random import randint

from django.utils import timezone


def get_unique_order_id():
    return "ORD"+timezone.now().strftime("%y%m%d%H%M%S")+str(randint(100, 999))


def get_unique_trans_id():
    return "TRANS"+timezone.now().strftime("%y%m%d%H%M%S")+str(randint(100, 999))
