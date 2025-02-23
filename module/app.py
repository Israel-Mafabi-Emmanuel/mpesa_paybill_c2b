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
    try:
        mpesa_callback_data = request.get_json()
        print(mpesa_callback_data)
        # checkout_request_id = mpesa_callback_data['Body']['stkCallback']['CheckoutRequestID']
        result_code = mpesa_callback_data['Body']['stkCallback']['ResultCode']
        result_description = mpesa_callback_data['Body']['stkCallback']['ResultDesc']

        if result_code == 0:  # this denotes a successful transaction...
            return jsonify({
                "message": "Payment Received Successfully",
                "data": mpesa_callback_data
            }), 200
        else:
            # Payment failed...
            return jsonify({
                "message": f"Payment Failed: {result_description}"
            }), 400

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
