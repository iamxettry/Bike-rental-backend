import uuid
from django.conf import settings
import hashlib

def generate_transaction_id():
    return str(uuid.uuid4())

def get_esewa_url():
    return settings.ESEWA_TEST_URL if settings.ESEWA_MODE == 'test' else settings.ESEWA_PROD_URL

def generate_esewa_form_data(payment):
    return {
        'amt': payment.amount_paid,
        'pdc': 0,
        'psc': 0,
        'txAmt': 0,
        'tAmt': payment.amount_paid,
        'pid': str(payment.transaction_id),
        'scd': settings.ESEWA_SCD,
        'su': settings.ESEWA_SUCCESS_URL,
        'fu': settings.ESEWA_FAILURE_URL
    }
