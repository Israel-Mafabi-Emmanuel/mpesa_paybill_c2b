# MPESA Paybill C2B Using Daraja API

## Introduction

This project provides a module to initiate MPESA STK push transactions using the Safaricom Daraja API. It allows businesses to interact with MPESA's C2B (Customer to Business) services, making it easier to receive payments from customers.

## Features

- Generate access tokens for API authentication.
- Initiate MPESA STK push requests.
- Handle callback responses from MPESA.
- Environment configuration for development and production.

## Project Structure

```plaintext
├── .env
├── module
│   ├── app.py
│   └── services.py
├── requirements.txt
└── README.md
```

### 1. `.env` - Environment Variables

This file contains environment variables required for the application to function correctly.

```ini
# Environment Variables
MPESA_BUSINESS_SHORTCODE="174379"
MPESA_CONSUMER_SECRET_KEY="YourConsumerSecretKey"
MPESA_CONSUMER_KEY="YourConsumerKey"
MPESA_PASSKEY="YourPasskey"

# Callback URL
MPESA_CALLBACK_URL="https://yourdomain.com/mpesa_callback"

# URLs
DEVELOPMENT_GENERATE_URL="https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
LIVE_GENERATE_URL="https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
DEVELOPMENT_PROCESS_REQUEST_URL="https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
LIVE_PROCESS_REQUEST_URL="https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
```

### 2. `services.py` - Utility Functions

This file contains utility functions for interacting with the MPESA API.

#### Functions

- `url(environment: int = 0, request: int = 0) -> str`
  
  - Returns the appropriate URL based on the environment (development or live) and the type of request (token generation or STK push).

- `generate_access_token()`
  
  - Generates and returns an access token for authentication with the MPESA API.

- `encode_password(shortcode: str, passkey: str, timestamp: str) -> str`
  
  - Encodes the password using the provided shortcode, passkey, and timestamp.

- `initiate_mpesa_stk_push(phone_number: str, amount: int, callback_url: str, account_reference: str, transaction_description: str)`
  
  - Initiates an MPESA STK push request and returns a tuple with the success status, message, and checkout request ID.

### 3. `app.py` - Flask Application

This file contains the main Flask application for testing and interaction purposes.

#### Endpoints

- `GET /`
  
  - Returns a welcome message.

- `POST /mpesa_callback`
  
  - Handles callback responses from MPESA and returns the payment status.

- `POST /mpesa_initiate/<phone_number>`
  
  - Initiates an MPESA STK push request for the specified phone number. Validates the phone number format before proceeding.

## Setup and Installation

1. **Clone the Repository**
   
   ```shell
   git clone https://github.com/yourusername/mpesa-daraja-api.git
   cd mpesa-daraja-api
   ```

2. **Install Dependencies**
   
   ```shell
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   
   - Create a `.env` file in the project root directory and populate it with the required environment variables.

4. **Run the Application**
   
   ```shell
   python app.py
   ```

## Usage

- **Initiate MPESA STK Push**:
  
  - Send a `POST` request to `/mpesa_initiate/<phone_number>` with a valid phone number in the format `254XXXXXXXXX`.

- **Handling the Callback:**
  
  To handle callbacks from MPESA, you can use `ngrok` to create a tunnel and expose your local server running on port 5000. This allows MPESA to send callback requests to your local development environment.
  
  Setting up ngrok!!!
  
  1. **Download and Install ngrok**:
     
     - Visit the ngrok website and download the appropriate version for your operating system.
     
     - Unzip the downloaded file and move it to a directory included in your system's PATH.
  
  2. **Start ngrok**:
     
     - Open your terminal and run the following command to create a tunnel and expose port 5000:
       
       ```shell
       ngrok http 5000
       ```
     
     - This command will generate a public URL that tunnels to your local server. You will see something like:
       
       ```
       ngrok by @inconshreveable                                       (Ctrl+C to quit)
       
       Session Status                online
       Session Expires               1 hour, 59 minutes
       Version                       2.3.35
       Region                        United States (us)
       Web Interface                 http://127.0.0.1:4040
       Forwarding                    http://9f70-197-237-122-19.ngrok-free.app -> http://localhost:5000
       Forwarding                    https://9f70-197-237-122-19.ngrok-free.app -> http://localhost:5000
       ```
     
     - Copy the `https` forwarding URL (e.g., `https://9f70-197-237-122-19.ngrok-free.app`) to use as your callback URL.
  
  3. **Update** `.env` **File**:
     
     - Replace the `MPESA_CALLBACK_URL` in your `.env` file with the ngrok URL:
       
       ```ini
       MPESA_CALLBACK_URL="https://9f70-197-237-122-19.ngrok-free.app/mpesa_callback"
       ```
  
  4. **Run Your Flask Application**:
     
     - Ensure your Flask application is running on port 5000:
       
       ```shell
       python app.py
       ```
  
  With ngrok set up, MPESA will be able to send callback requests to your locally running server, allowing you to test and debug your integration in a development environment.
  
  This setup ensures that you can handle real callback responses from MPESA without deploying your application to a live server during development.

## Example Requests

- **Initiate STK Push**:
  
  ```shell
  curl -X POST http://localhost:5000/mpesa_initiate/254XXXXXXXXX
  ```

- **Callback Handling**:
  
  - Configure your MPESA Callback URL to point to `https://yourdomain.com/mpesa_callback`.

## Security Considerations

- Ensure all communication with the MPESA API and your server is encrypted using HTTPS.

- Store sensitive information such as API keys securely.

## License

This project is licensed under the MIT License.

## Acknowledgements

- GLORY BE TO GOD

- By Israel Mafabi Emmanuel
