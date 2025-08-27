import logging

import requests
from clerk_backend_api import Clerk
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwk, jwt

import constants

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_jwks():
    response = requests.get(f"{constants.CLERK_JWKS_URL}")
    return response.json()


def get_public_key(kid):
    jwks = get_jwks()
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return jwk.construct(key)
    raise HTTPException(status_code=401, detail="Invalid token")


def decode_token(token: str):
    headers = jwt.get_unverified_headers(token)
    kid = headers["kid"]
    public_key = get_public_key(kid)
    return jwt.decode(
        token,
        public_key.to_pem().decode("utf-8"),
        algorithms=["RS256"],
        audience="your_audience",
        issuer=constants.CLERK_ISSUER,
    )


clerk_router = APIRouter(prefix="/protected", tags=["auth"])
security = HTTPBearer()


@clerk_router.get("/")
async def protected_route(
    request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")
    # Now that we have verified the Bearer token and extracted the
    # user ID, we can proceed to access protected resources. Note that # # using the Bearer token is more secure than passing a session ID in # the query parameter.
    # We retrieve user details from Clerk directly using the user ID.
    clerk_sdk = Clerk(bearer_auth=constants.CLERK_SECRET_KEY)
    user_details = clerk_sdk.users.get(user_id=user_id)
    if not user_details:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "status": "success",
        "data": {
            "first_name": user_details.first_name,
            "last_name": user_details.last_name,
            "email": user_details.email_addresses[0].email_address,
            "phone": user_details.phone_numbers,
            "session_created_at": user_details.created_at,
            "session_last_active_at": user_details.last_active_at,
        },
    }
