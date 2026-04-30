from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

# HTTP Status Success Codes
HSC_200 = 200  # OK - Success
HSC_201 = 201  # Created
HEC_401 = 401  # unauthentic

# HTTP Status Error Codes
HEC_400 = 400  # Bad Request
HEC_429 = 429  # Too Many Requests
HEC_500 = 500  # Internal Server Error

# HTTP Success Messages
HEM_INTERNAL_SERVER_ERROR = "Something went wrong. Please try again."
HEM_UNAUTHORIZED = "Your Session has been expired!"
HSM_SUCCESS = "success"

# HTTP Error Messages
HEM_ERROR = "error"
HEM_INVALID_EMAIL_FORMAT = "Invalid email format"
HEM_INVALID_MOBILE_FORMAT = "Invalid mobile number format"
HEM_INVALID_VERIFY_CODE_FORMAT = "Verify code must contain only numbers."


def successResponse(status_code, msg, data=None):
    if data is None:
        data = {"data": []}

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": msg,
            "data": jsonable_encoder(data),
        }
    )

def errorResponse(status_code, msg, data=None):
    if data is None:
        data = {"data": []}

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "fail",
            "message": msg,
            "data": jsonable_encoder(data),
        }
    )
