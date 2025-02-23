# GLORY BE TO GOD,
# MONEY TRANSFER - USING SAFARICOM, DARAJA API
# BY ISRAEL MAFABI EMMANUEL
# OUR UTILITIES FILE

import os
import base64
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

BUSINESS_SHORTCODE: str = os.getenv("MPESA_BUSINESS_SHORTCODE")
PASSKEY: str = os.getenv("MPESA_PASSKEY")
CONSUMER_KEY: str = os.getenv("MPESA_CONSUMER_KEY")
CONSUMER_SECRET_KEY: str = os.getenv("MPESA_CONSUMER_SECRET_KEY")


def url(environment: int = 0, request: int = 0) -> str:
    """
        A function for selecting the required url
        based on environment selection.

        request type:
        0 -> request development
        1 -> request live

        environment type:
        0 -> local environment - development environment
        1 -> live/deployment

        :returns
        -> returns a string -> concerning the url (environment based...)
    """
    development_generate_url = os.getenv("DEVELOPMENT_GENERATE_URL")
    live_generate_url = os.getenv("LIVE_GENERATE_URL")
    development_process_request_url = os.getenv("DEVELOPMENT_PROCESS_REQUEST_URL")
    live_process_request_url = os.getenv("LIVE_PROCESS_REQUEST_URL")
    if request != 0:
        # request session
        if environment != 0:
            return live_process_request_url
        return development_process_request_url
    else:
        # default... normal mode
        if environment != 0:
            return live_generate_url
        return development_generate_url


def generate_access_token():
    """
        A function for generating the access token
        for authentication over APIs

        :returns
        -> No return values...
    """
    try:
        # encoding the credentials
        # following the structure: [key:key]
        encoded_credentials: base64 = base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET_KEY}".encode()).decode()
        # setting up the header... ~ Authorization
        headers: dict = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
        # send the request and parse the response...
        response = requests.get(url(environment=0, request=0), headers=headers).json()

        # check for errors and afterwards return the access token...
        # since if positive a dict will be returned...
        if "access_token" in response:
            return response["access_token"]
        else:
            raise Exception(f"error: failed to get access token: {response["error_description"]}")
    except Exception as e:
        raise Exception(f"error: failed to get access token: {e}")


def encode_password(shortcode: str, passkey: str, timestamp: str) -> str:
    """
        A function for creating the password...
        Encodes the password using the provided shortcode, passkey and timestamp.

        :argument
        shortcode: refers to the business short code.
        passkey: mpesa passkey from - daraja api.
        timestamp: time value...

        :returns
        returns a string -> The encoded password string
    """
    password_string: str = shortcode + passkey + timestamp
    encoded_string: bytes = base64.b64encode(password_string.encode())
    return encoded_string.decode('utf-8')


def initiate_mpesa_stk_push(phone_number: str, amount: int, callback_url: str, account_reference: str,
                            transaction_description: str):
    """
        A function that initiates an MPESA STK Push request.

        :arg
        phone_number: The customer's phone number (e.g., "2547XXXXXXXX").
        amount: The amount to be paid.
        callback_url: The URL on your server that MPESA will call back to with the payment status.
        account_reference:  Your unique reference for the transaction
        transaction_description: A description of the transaction.

        :returns
        returns a tuple: (success, message, checkout_request_id)
        success: True if the STK push was initiated successfully, False otherwise.
        message: A message indicating the status of the request.
        checkout_request_id: The MPESA CheckoutRequestID (used for querying the transaction status).
    """
    access_token = generate_access_token()
    timestamp: str = datetime.now().strftime('%Y%m%d%H%M%S')

    headers: dict = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    print(callback_url) # for debugging purposes...

    # body, stk push payload...
    stk_push_payload: dict = {
        "BusinessShortCode": BUSINESS_SHORTCODE,
        "Password": encode_password(BUSINESS_SHORTCODE, PASSKEY, timestamp),
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,  # the sender
        "PartyB": BUSINESS_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": account_reference,  # Any value... -> MAFABI
        "TransactionDesc": transaction_description  # Any value... -> MAFABI
    }

    try:
        response = requests.post(url(environment=0, request=1), json=stk_push_payload, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        response_json: any = response.json()

        checkout_request_id: any = response_json.get('CheckoutRequestID')
        if checkout_request_id:
            return True, "STK push initiated successfully", checkout_request_id
        else:
            error_message: any = response_json.get('errorMesssage')
            return False, f"STK push failed: {error_message}", None
        # return response_json
    except requests.exceptions.RequestException as error_message:
        return False, f"STK push failed: {error_message}", None
    except Exception as error_message:
        return False, f"Error initiating MPESA STK Push: {error_message}", None
