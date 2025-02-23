# GLORY BE TO GOD,
# MONEY TRANSFER - USING SAFARICOM MPESA DARAJA API,
# BY ISRAEL MAFABI EMMANUEL


import re

from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import  get_remote_address
import os
from dotenv import load_dotenv
from services import initiate_mpesa_stk_push

load_dotenv()

CALLBACK_URL: str = os.getenv("MPESA_CALLBACK_URL")

app = Flask(__name__)

# Initialize Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)


@app.route("/", methods=["GET"])
def home():
    response_data = {
        "message": "welcome, money transfer debug route."
    }
    return jsonify(response_data), 200


@app.route("/mpesa_callback", methods=["POST"])
def mpesa_callback():
    # What we are expecting:
    # A SUCCESSFUL TRANSACTION RESPONSE...
    # "stkCallback": {
    #     "MerchantRequestID": "1XXX----",
    #     "CheckoutRequestID": "ws_CO_XXXX",
    #     "ResultCode": 0,
    #     "ResultDesc": "The service request is processed successfully.",
    #     "CallbackMetadata": {
    #         "Item": [{
    #             "Name": "Amount",
    #             "Value": 1.00
    #         },
    #             {
    #                 "Name": "MpesaReceiptNumber",
    #                 "Value": "NLXXXXX"
    #             },
    #             {
    #                 "Name": "TransactionDate",
    #                 "Value": 202xxxx
    #             },
    #             {
    #                 "Name": "PhoneNumber",
    #                 "Value": 2547xxxx
    #             }]
    #     }
    # }
    # AN UNSUCCESSFUL TRANSACTION... FOLLOWS THIS STRUCTURE
    #   "MerchantRequestID": "1XXX----",
    #   "CheckoutRequestID": "ws_CO_xxxx",
    #   "ResultCode": 1032,
    #   "ResultDesc": "Request canceled by user."
    try:
        mpesa_callback_data = request.get_json()
        # checkout_request_id = mpesa_callback_data['Body']['stkCallback']['CheckoutRequestID']
        result_code = mpesa_callback_data['Body']['stkCallback']['ResultCode']
        result_description = mpesa_callback_data['Body']['stkCallback']['ResultDesc']
        items = mpesa_callback_data['Body']['stkCallback']['CallbackMetadata']['Item'] # item in callback metadata...

        mpesa_receipt_number = None # just for initialization...

        for item in items:
            if item['Name'] == 'MpesaReceiptNumber':
                mpesa_receipt_number = item['Value']
                break

        print({
            "message": "Payment Received Successfully",
            "transaction_code": mpesa_receipt_number,
            "description": result_description
        }) # for debugging purposes...

        if result_code == 0:  # this denotes a successful transaction...
            # here we can either store the payment status in the database or ...
            return jsonify({"message": "Payment Received Successfully"}), 200
        else:
            # Payment failed...
            return jsonify({"message": f"Payment Failed: {result_description}"}), 400

    except Exception as request_error:
        return jsonify({"message": f"error processing mpesa callback: {str(request_error)}"}), 500


@app.route("/mpesa_initiate/<phone_number>", methods=["POST"])
@limiter.limit("1 per 3 minutes") # rate limit: 1 request per 3 minutes
def mpesa_initiate(phone_number: str):
    # first we validate the phone number ensuring that it has the,
    # correct format.
    if re.match(r"^254\d{9}$", phone_number):
        # for the phone number is valid,
        # let's send the push...
        success, message, checkout_request_id = initiate_mpesa_stk_push(
            phone_number=phone_number,
            amount=1,
            callback_url=CALLBACK_URL,
            account_reference="MAFABI",
            transaction_description="MAFABI"
        )

        if success:
            return jsonify({
                "message": "MPESA STK Push initiated. Awaiting payment confirmation.",
                "checkout_request_id": checkout_request_id
            }), 200
        else:
            return jsonify({
                "message": f"MPESA STK push failed: {message}"
            }), 500

    else:
        return jsonify({
            "status": "error", "message": "Invalid phone number"
        }), 400


if __name__ == '__main__':
    app.run(debug=True)
