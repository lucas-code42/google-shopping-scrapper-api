import os

from dotenv import load_dotenv
from flask import Flask, request, make_response

from src.service.email_job import send_email
from src.service.service_job import Selenium

app = Flask(__name__)

yasmin = "a0ffa9a4-f1a6-4960-a6b5-ff357c22d5b1"
lucas = "cca69230-b194-478b-9618-890c639e2cec"


@app.route("/process", methods=["POST"])
def process():
    authorization = request.headers.get("Authorization")

    if authorization not in [yasmin, lucas]:
        response = make_response({"message": "Unauthorized", "process_status": False})
        response.status_code = 401
        return response
    else:
        body = request.get_json()

        service = Selenium().process(product_to_search=body["product_name"])
        email_service = send_email(to_addr=body["email_address"], email_token=os.getenv("GMAILTOKEN"))

        if not service and not email_service:
            response = make_response({"message": "processing failed", "process_status": False})
            response.status_code = 500
            return response
        else:
            response = make_response({"message": "processing performed successfully",
                                      "process_status": True,
                                      "report_send_to": body["email_address"],
                                      "file_name": "product_report.xlsx"})
            response.status_code = 200
            return response


if __name__ == "__main__":
    load_dotenv()
    app.run(port=os.getenv("PORT"))
