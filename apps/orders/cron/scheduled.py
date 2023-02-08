from apps.orders.utils.general_service import GeneralAPIService
from apps.orders.utils.order_place_service import ProcessPendingOrders


def refresh_access_token():
    GeneralAPIService().save_access_token()

def process_pending_orders():
    ProcessPendingOrders().process()