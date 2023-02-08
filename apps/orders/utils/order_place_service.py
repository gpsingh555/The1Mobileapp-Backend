import datetime

from django.conf import settings

from apps.orders.api_clients.du_postpaid import DUPostpaidAPIClient
from apps.orders.api_clients.du_prepaid import DUPrepaidAPIClient
from apps.orders.api_clients.etisalat import EtisalatAPIClient
from apps.orders.api_clients.hafilat import HafilatAPIClient
from apps.orders.api_clients.nol_topup import NOLTopupAPIClient
from apps.orders.api_clients.platform import GeneralAPIClient
from apps.orders.api_clients.salik_direct import SalikDirectAPIClient
from apps.orders.models import Orders, OrdersDetails, FAILED, PAYMENT_FAILED, PROCESSING, RECHARGE_PROCESSING, \
    COMPLETED, PAYMENT_PROCESSING, DATA, MINUTE, RECHARGE_COMPLETED, RECHARGE_FAILED, MBME, DU_PREPAID, DU_POSTPAID, \
    NOL_TOPUP, SALIK_DIRECT, ETISALAT, HAFILAT
from apps.payment.models import PaymentTransactions, TRANSACTION_FAILED, TRANSACTION_CANCELLED, TRANSACTION_PROCESSING, \
    TRANSACTION_COMPLETED, STRIPE
from apps.payment.utils.stripe import Stripe
from utils.exceptions import APIException500, APIException400, APIException503
from django.db.models import F

from utils.utils import get_unique_order_id, get_unique_trans_id


class OrderService:
    def __init__(self, intent_id, request):
        self.intent_id = intent_id
        self.request = request
        self.payload = {}

    def place_order(self):
        stripe_obj = Stripe()
        self.payload = stripe_obj.retrive_payment_intent(
            intent_id=self.intent_id
        )
        print(f"Retrieve payment intent with payload {self.payload}")
        if self.payload["status"] and self.payload["data"]:
            failed_msg = "Recharge failed because your payment is failed. In case of any amount deducted " \
                         "that will be refunded"
            success_msg = "Recharge successful"
            in_process_msg = "We are processing your recharge. It may take some time."
            payment_method = ""
            payment_method_data = self.payload["data"].get("charges", {}).get("data", {})
            print(payment_method_data)
            if payment_method_data:
                payment_method = payment_method_data[0].get("payment_method_details", {}).get(
                    payment_method_data[0].get("payment_method_details", {}).get("type"), {}).get("funding")
                print(payment_method)

            if self.payload["data"].get('status') in ('canceled', 'payment_failed'):
                # Mark failed the order
                order = self.save_order(
                    self.payload["data"]["metadata"], FAILED, PAYMENT_FAILED
                )
                self.save_transaction(order, self.intent_id, self.payload["data"], TRANSACTION_FAILED, payment_method)
                return FAILED, failed_msg

            elif self.payload["data"].get('status') in ("requires_payment_method", "requires_source", 'requires_action',
                                                        'requires_source_action', 'requires_capture'):
                # cancel the payment intent
                stripe_obj.cancel_payment_intent(
                    intent_id=self.intent_id)
                # Mark failed the order
                order = self.save_order(
                    self.payload["data"]["metadata"], FAILED, PAYMENT_FAILED
                )
                self.save_transaction(order, self.intent_id, self.payload["data"], TRANSACTION_CANCELLED,
                                      payment_method)
                return FAILED, failed_msg

            elif self.payload["data"].get('status') == 'processing':
                # create order and put in retry queue and mark status as processing
                order = self.save_order(
                    self.payload["data"]["metadata"], PROCESSING, PAYMENT_PROCESSING
                )
                # put in processing queue
                self.save_in_progress_order(order, 1, {})
                self.save_transaction(order, self.intent_id, self.payload["data"], TRANSACTION_PROCESSING,
                                      payment_method)
                return PROCESSING, in_process_msg

            elif self.payload["data"].get('status') == 'succeeded':
                recharge_status = PROCESSING
                order = None
                msg = ""
                status = False
                print(f'Got service Type =>{self.payload["data"]["metadata"].get("service_type")}')
                if self.payload["data"]["metadata"].get('service_provider') == MBME:
                    if self.payload["data"]["metadata"].get('service_type') in (DU_PREPAID, DU_POSTPAID):
                        order, status = self.place_du_recharge_orders()

                    elif self.payload["data"]["metadata"].get('service_type') == NOL_TOPUP:
                        print(f"Start placing {NOL_TOPUP}")
                        order, status = self.place_nol_orders()

                    elif self.payload["data"]["metadata"].get('service_type') == SALIK_DIRECT:
                        print(f"Start placing {SALIK_DIRECT}")
                        order, status = self.place_salik_direct_orders()

                    elif self.payload["data"]["metadata"].get('service_type') == ETISALAT:
                        print(f"Start placing {ETISALAT}")
                        order, status = self.place_etisalat_orders()

                    elif self.payload["data"]["metadata"].get('service_type') == HAFILAT:
                        print(f"Start placing {HAFILAT}")
                        order, status = self.place_hafilat_orders()

                    if status == RECHARGE_COMPLETED:
                        recharge_status = COMPLETED
                        msg = success_msg
                    else:
                        recharge_status = PROCESSING
                        msg = in_process_msg

                if order:
                    self.save_transaction(order, self.intent_id, self.payload["data"], TRANSACTION_COMPLETED,
                                          payment_method)
                else:
                    raise APIException400({"error": "Invalid service type provided while payment Initiate api"})

                return recharge_status, msg
            else:
                raise APIException500()

        else:
            print("Failed to get payment intent")
            raise APIException400({"error": self.payload["detail"]})

    def place_du_recharge_orders(self):
        """
        """
        if self.payload["data"]["metadata"].get('service_type') == DU_PREPAID:
            if self.payload["data"]["metadata"]["recharge_type"] == DATA:
                recharge_type = 'data'
            elif self.payload["data"]["metadata"]["recharge_type"] == MINUTE:
                recharge_type = 'time'
            else:
                raise APIException500()

            print("Start calling do recharge API")
            rq_satus, status, resp = DUPrepaidAPIClient().do_recharge(
                self.payload["data"]["metadata"].get("recharge_number"),
                recharge_type, self.payload["data"]["metadata"].get("amount")
            )

        elif self.payload["data"]["metadata"].get('service_type') == DU_POSTPAID:
            print("Start calling do recharge API for Postpaid")
            rq_satus, status, resp = DUPostpaidAPIClient().do_recharge(
                self.payload["data"]["metadata"].get("recharge_number"),
                self.payload["data"]["metadata"].get("amount"),
                self.payload["data"]["metadata"]["recharge_transaction_id"]
            )
        else:
            raise APIException500({'error': "Invalid Service type"})

        order = None
        print(f"GET response for recharge API {rq_satus}, {status}, {resp}")
        if rq_satus and status == RECHARGE_COMPLETED:
            order = self.save_order(
                self.payload["data"]["metadata"], COMPLETED, RECHARGE_COMPLETED
            )
            transaction_id = resp.get("responseData", {}).get("transactionId")
            unique_id = resp.get("responseData", {}).get("resField1")
            self.save_in_progress_order(order, 0, resp, transaction_id, unique_id, False)
        elif rq_satus and status == RECHARGE_PROCESSING:
            order = self.save_order(
                self.payload["data"]["metadata"], PROCESSING, RECHARGE_PROCESSING
            )
            # if in processing then push it in process queue
            transaction_id = resp.get("responseData", {}).get("transactionId")
            unique_id = resp.get("responseData", {}).get("resField1")
            self.save_in_progress_order(order, 1, resp, transaction_id, unique_id)

        elif not rq_satus and status == RECHARGE_FAILED:
            order = self.save_order(
                self.payload["data"]["metadata"], PROCESSING, RECHARGE_FAILED
            )
            print("Pushing in PROCESSING QUEUE")
            transaction_id = resp.get("responseData", {}).get("transactionId")
            unique_id = resp.get("responseData", {}).get("resField1")
            self.save_in_progress_order(order, 1, resp, transaction_id, unique_id)

        return order, status

    def place_nol_orders(self):
        """
        """
        rq_satus, status, resp = NOLTopupAPIClient().do_recharge(
            self.payload["data"]["metadata"].get("recharge_number"),
            self.payload["data"]["metadata"].get("amount"),
            self.payload["data"]["metadata"]["recharge_transaction_id"]
        )

        order = None
        print(f"GET response for recharge API {rq_satus}, {status}, {resp}")
        if rq_satus and status == RECHARGE_COMPLETED:
            order = self.save_order(
                self.payload["data"]["metadata"], COMPLETED, RECHARGE_COMPLETED
            )
            transaction_id = resp.get("responseData", {}).get("transactionId")
            unique_id = resp.get("responseData", {}).get("resField3")
            self.save_in_progress_order(order, 0, resp, transaction_id, unique_id, False)
        elif rq_satus and status == RECHARGE_PROCESSING:
            order = self.save_order(
                self.payload["data"]["metadata"], PROCESSING, RECHARGE_PROCESSING
            )
            # if in processing then push it in process queue
            transaction_id = resp.get("responseData", {}).get("transactionId")
            unique_id = resp.get("responseData", {}).get("resField3")
            self.save_in_progress_order(order, 1, resp, transaction_id, unique_id)

        elif not rq_satus and status == RECHARGE_FAILED:
            order = self.save_order(
                self.payload["data"]["metadata"], PROCESSING, RECHARGE_FAILED
            )
            print("Pushing in PROCESSING QUEUE")
            transaction_id = resp.get("responseData", {}).get("transactionId")
            unique_id = resp.get("responseData", {}).get("resField3")
            self.save_in_progress_order(order, 1, resp, transaction_id, unique_id)

        return order, status

    def place_salik_direct_orders(self):
        """
        """
        rq_satus, status, resp = SalikDirectAPIClient().do_recharge(
            self.payload["data"]["metadata"].get("recharge_number"),
            self.payload["data"]["metadata"].get("amount"),
            self.payload["data"]["metadata"].get("account_pin"),
            self.payload["data"]["metadata"]["recharge_transaction_id"],
            self.payload["data"]["metadata"]["provider_transaction_id"],
        )
        order = None
        print(f"GET response for recharge API {rq_satus}, {status}, {resp}")
        if rq_satus and status == RECHARGE_COMPLETED:
            order = self.save_order(
                self.payload["data"]["metadata"], COMPLETED, RECHARGE_COMPLETED
            )
            transaction_id = resp.get("responseData", {}).get("transactionId")
            unique_id = resp.get("responseData", {}).get("resField3")
            self.save_in_progress_order(order, 0, resp, transaction_id, unique_id, False)
        elif rq_satus and status == RECHARGE_PROCESSING:
            order = self.save_order(
                self.payload["data"]["metadata"], PROCESSING, RECHARGE_PROCESSING
            )
            # if in processing then push it in process queue
            transaction_id = resp.get("responseData", {}).get("transactionId")
            unique_id = resp.get("responseData", {}).get("resField3")
            self.save_in_progress_order(order, 1, resp, transaction_id, unique_id)

        elif not rq_satus and status == RECHARGE_FAILED:
            order = self.save_order(
                self.payload["data"]["metadata"], PROCESSING, RECHARGE_FAILED
            )
            print("Pushing in PROCESSING QUEUE")
            transaction_id = resp.get("responseData", {}).get("transactionId")
            unique_id = resp.get("responseData", {}).get("resField3")
            self.save_in_progress_order(order, 1, resp, transaction_id, unique_id)

        return order, status

    def place_etisalat_orders(self):
        """
        number, service_offered, current_balance, amount, recharge_transaction_id
        """
        rq_satus, status, resp = EtisalatAPIClient().do_recharge(
            self.payload["data"]["metadata"].get("recharge_number"),
            self.payload["data"]["metadata"].get("service_offered"),
            self.payload["data"]["metadata"].get("current_balance"),
            self.payload["data"]["metadata"]["amount"],
            self.payload["data"]["metadata"]["recharge_transaction_id"],
            self.payload["data"]["metadata"]["provider_transaction_id"],
        )

        order = None
        print(f"GET response for recharge API {rq_satus}, {status}, {resp}")
        if rq_satus and status == RECHARGE_COMPLETED:
            order = self.save_order(
                self.payload["data"]["metadata"], COMPLETED, RECHARGE_COMPLETED
            )
            transaction_id = resp.get("responseData", {}).get("transactionId")
            unique_id = resp.get("responseData", {}).get("resField6")
            self.save_in_progress_order(order, 0, resp, transaction_id, unique_id, False)
        elif rq_satus and status == RECHARGE_PROCESSING:
            order = self.save_order(
                self.payload["data"]["metadata"], PROCESSING, RECHARGE_PROCESSING
            )
            # if in processing then push it in process queue
            transaction_id = resp.get("responseData", {}).get("transactionId")
            unique_id = resp.get("responseData", {}).get("resField6")
            self.save_in_progress_order(order, 1, resp, transaction_id, unique_id)

        elif not rq_satus and status == RECHARGE_FAILED:
            order = self.save_order(
                self.payload["data"]["metadata"], PROCESSING, RECHARGE_FAILED
            )
            print("Pushing in PROCESSING QUEUE")
            transaction_id = resp.get("responseData", {}).get("transactionId")
            unique_id = resp.get("responseData", {}).get("resField6")
            self.save_in_progress_order(order, 1, resp, transaction_id, unique_id)

        return order, status

    def place_hafilat_orders(self):
        """
        number, amount, product_code, item_code
        """
        rq_satus, status, resp = HafilatAPIClient().do_recharge(
            self.payload["data"]["metadata"].get("recharge_number"),
            self.payload["data"]["metadata"].get("amount"),
            self.payload["data"]["metadata"]["product_code"],
            self.payload["data"]["metadata"]["item_code"],
            self.payload["data"]["metadata"]["max_allowed"],
            self.payload["data"]["metadata"]["recharge_type"],
            self.payload["data"]["metadata"]["recharge_transaction_id"]
        )

        order = None
        print(f"GET response for recharge API {rq_satus}, {status}, {resp}")
        if rq_satus and status == RECHARGE_COMPLETED:
            order = self.save_order(
                self.payload["data"]["metadata"], COMPLETED, RECHARGE_COMPLETED
            )
            transaction_id = self.payload["data"]["metadata"]["recharge_transaction_id"]
            unique_id = resp.get("responseData", {}).get("providerTransactionId")
            self.save_in_progress_order(order, 0, resp, transaction_id, unique_id, False)
        elif rq_satus and status == RECHARGE_PROCESSING:
            order = self.save_order(
                self.payload["data"]["metadata"], PROCESSING, RECHARGE_PROCESSING
            )
            # if in processing then push it in process queue
            transaction_id = self.payload["data"]["metadata"]["recharge_transaction_id"]
            unique_id = resp.get("responseData", {}).get("providerTransactionId")
            self.save_in_progress_order(order, 1, resp, transaction_id, unique_id)

        elif not rq_satus and status == RECHARGE_FAILED:
            order = self.save_order(
                self.payload["data"]["metadata"], PROCESSING, RECHARGE_FAILED
            )
            print("Pushing in PROCESSING QUEUE")
            transaction_id = self.payload["data"]["metadata"]["recharge_transaction_id"]
            unique_id = resp.get("responseData", {}).get("providerTransactionId")
            self.save_in_progress_order(order, 1, resp, transaction_id, unique_id)

        return order, status

    def save_order(self, metadata, status, sub_status):
        print(f"Start saving order => {metadata}, {status}, {sub_status}")
        obj = Orders.objects.create(
            user=self.request.user,
            service_type=metadata.get("service_type"),
            recharge_type=metadata.get("recharge_type"),
            service_provider=metadata.get("service_provider"),
            recharge_number=metadata.get("recharge_number"),
            amount=metadata.get("amount"),
            order_id=get_unique_order_id(),
            status=status,
            sub_status=sub_status
        )
        return obj

    def save_in_progress_order(self, order, retry_count, last_response,
                               transaction_id=None, unique_id=None, is_active=True):
        OrdersDetails.objects.create(
            order=order,
            retry_count=retry_count,
            last_response=last_response,
            transaction_id=transaction_id,
            unique_id=unique_id,
            is_active=is_active
        )

    def save_transaction(self, order, payment_intent, resp, status, method=None):
        if method == "credit":
            method = "2"
        elif method == "debit":
            method = "1"
        else:
            method = "3"
        PaymentTransactions.objects.create(
            order=order,
            user=self.request.user,
            payment_provider=STRIPE,
            payment_method=method,
            payment_intent=payment_intent,
            gateway_response=resp,
            transaction_id=get_unique_trans_id(),
            status=status
        )


class ProcessPendingOrders:
    """
    """

    def process(self):
        qs = OrdersDetails.objects.filter(is_active=True).select_related("order")
        for ord_obj in qs:
            print(f"Start Processing order ==> {ord_obj.order.id}")
            if ord_obj.order.service_provider == MBME:
                if ord_obj.order.service_type == DU_PREPAID:
                    self.process_payment(ord_obj)

    def process_payment(self, pend_ord_obj):
        order_obj = pend_ord_obj.order
        stripe_obj = Stripe()
        if order_obj.sub_status == PAYMENT_PROCESSING:
            # will check payment status
            qs = PaymentTransactions.objects.filter(order=order_obj)
            if qs.exists():
                trnas_obj = qs[0]
                # we will not hit in case of webhook
                payload = stripe_obj.retrive_payment_intent(
                    intent_id=trnas_obj.payment_intent
                )
                print(f"Retrieve payment intent with payload {payload}")
                if payload["status"] and payload["data"]:
                    # check the satus of payment
                    if payload["data"].get('status') in ('canceled', 'payment_failed'):
                        # Mark failed the order
                        order_obj.status = FAILED
                        order_obj.sub_status = PAYMENT_FAILED
                        order_obj.save()
                        # update transaction obj
                        trnas_obj.status = TRANSACTION_FAILED
                        trnas_obj.gateway_response = payload
                        trnas_obj.save()
                        # remove from pending queue
                        pend_ord_obj.is_active = False
                        pend_ord_obj.save()

                    elif payload["data"].get('status') in (
                            "requires_payment_method", "requires_source", 'requires_action',
                            'requires_source_action', 'requires_capture'):
                        # cancel the payment intent
                        stripe_obj.cancel_payment_intent(
                            intent_id=trnas_obj.payment_intent)
                        # Mark failed the order
                        order_obj.status = FAILED
                        order_obj.sub_status = PAYMENT_FAILED
                        order_obj.save()
                        # update transaction obj
                        trnas_obj.status = TRANSACTION_CANCELLED
                        trnas_obj.gateway_response = payload
                        trnas_obj.save()
                        # remove from pending queue
                        pend_ord_obj.is_active = False
                        pend_ord_obj.save()

                    elif payload["data"].get('status') == 'processing':
                        # update retry count
                        pend_ord_obj.retry_count = F('retry_count') + 1
                        pend_ord_obj.last_response = payload["data"]
                        pend_ord_obj.save()

                    elif payload["data"].get('status') == 'succeeded':
                        # update transaction obj
                        trnas_obj.status = TRANSACTION_COMPLETED
                        trnas_obj.gateway_response = payload
                        trnas_obj.save()
                        # start placing order
                        if payload["data"].get('service_provider') == MBME:
                            if payload["data"].get('service_type') == DU_PREPAID:
                                self.place_du_prepaid_orders(
                                    payload, order_obj, pend_ord_obj)

                else:
                    # re-initiate in payment
                    pend_ord_obj.retry_count = F('retry_count') + 1
                    pend_ord_obj.last_response = payload["data"]
                    pend_ord_obj.save()
            else:
                print("Did not found any transaction")

        elif order_obj.sub_status == RECHARGE_PROCESSING:
            general_api_client = GeneralAPIClient()
            status, trans_data = general_api_client.get_recharge_status(pend_ord_obj.transaction_id)
            if status:
                # Mark failed the order
                order_obj.status = FAILED
                order_obj.sub_status = PAYMENT_FAILED
                order_obj.save()
                # remove from pending queue
                pend_ord_obj.is_active = False
                pend_ord_obj.save()
            else:
                # retry if time is greater than 1 day
                if pend_ord_obj.updated_at > pend_ord_obj.created_at + datetime.timedelta(days=1):
                    status, resp = general_api_client.process_pending_recharge(pend_ord_obj.unique_id)
                    # if retry goes success
                    if status:
                        order_obj.status = COMPLETED
                        order_obj.status = RECHARGE_COMPLETED
                        order_obj.save()
                        # remove from queue
                        pend_ord_obj.last_response = resp
                        pend_ord_obj.is_active = False
                        pend_ord_obj.save()
                    else:
                        pend_ord_obj.retry_count = F('retry_count') + 1
                        pend_ord_obj.last_response = resp
                        pend_ord_obj.save()

        elif order_obj.sub_status == RECHARGE_FAILED:
            if order_obj.recharge_type == DATA:
                recharge_type = 'data'
            elif order_obj.recharge_type == MINUTE:
                recharge_type = 'time'
            else:
                raise APIException500()

            order = None
            print("Start calling do recharge API")
            rq_satus, status, resp = DUPrepaidAPIClient.do_recharge(
                order_obj.recharge_number,
                recharge_type
            )
            print(f"GET response for recrge API {rq_satus}, {status}, {resp}")

            if rq_satus and status == RECHARGE_COMPLETED:
                order_obj.status = COMPLETED
                order_obj.status = RECHARGE_COMPLETED
                order_obj.save()
                # remove from queue
                pend_ord_obj.last_response = resp
                pend_ord_obj.is_active = False
                pend_ord_obj.save()
            elif rq_satus and status == RECHARGE_PROCESSING:
                # update order with processing
                order_obj.status = PROCESSING
                order_obj.status = RECHARGE_PROCESSING
                order_obj.save()
                # update pending order queue
                pend_ord_obj.retry_count = F('retry_count') + 1
                pend_ord_obj.last_response = resp
                pend_ord_obj.save()

            elif not rq_satus and status == RECHARGE_FAILED:
                if pend_ord_obj.retry_count > int(settings.MAX_RETRY_COUNT_FO_FAILED_TRANS):
                    # mark order as failed
                    order_obj.status = FAILED
                    order_obj.status = RECHARGE_FAILED
                    order_obj.save()
                    # remove from queue
                    pend_ord_obj.last_response = resp
                    pend_ord_obj.is_active = False
                    pend_ord_obj.save()
                else:
                    pend_ord_obj.last_response = resp
                    pend_ord_obj.retry_count = F('retry_count') + 1
                    pend_ord_obj.transaction_id = resp.get("responseData", {}).get("transactionId")
                    pend_ord_obj.unique_id = resp.get("responseData", {}).get("resField1")
                    pend_ord_obj.save()
            return order

    def place_du_prepaid_orders(self, payload, order_obj, pend_ord_obj):
        if payload["data"]["metadata"]["recharge_type"] == DATA:
            recharge_type = 'data'
        elif payload["data"]["metadata"]["recharge_type"] == MINUTE:
            recharge_type = 'time'
        else:
            raise APIException500()

        print("Start calling do recharge API")
        rq_satus, status, resp = DUPrepaidAPIClient.do_recharge(
            payload["data"]["metadata"].get("recharge_number"),
            recharge_type
        )
        print(f"GET response for recrge API {rq_satus}, {status}, {resp}")
        if rq_satus and status == RECHARGE_COMPLETED:
            order_obj.status = COMPLETED
            order_obj.sub_status = RECHARGE_COMPLETED
            order_obj.save()
            # remove from queue
            pend_ord_obj.is_active = False
            pend_ord_obj.save()

        elif rq_satus and status == RECHARGE_PROCESSING:
            order_obj.status = PROCESSING
            order_obj.sub_status = RECHARGE_PROCESSING
            order_obj.save()
            # update retry count
            pend_ord_obj.retry_count = F('retry_count') + 1
            pend_ord_obj.last_response = payload["data"]
            pend_ord_obj.save()

        elif not rq_satus and status == RECHARGE_FAILED:
            order_obj.status = PROCESSING
            order_obj.sub_status = RECHARGE_FAILED
            order_obj.save()
            # update retry count
            pend_ord_obj.retry_count = F('retry_count') + 1
            pend_ord_obj.last_response = payload["data"]
            pend_ord_obj.save()
            # update retry count
            pend_ord_obj.retry_count = F('retry_count') + 1
            pend_ord_obj.last_response = payload["data"]
            pend_ord_obj.save()
