# Authorization configuration file
from jose import jwt
from flask import request, g, abort
from functools import wraps
import json
from urllib.request import urlopen
from dotenv import load_dotenv
import os

load_dotenv()
# Environment variables
AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN')
API_AUDIENCE = os.environ.get('API_AUDIENCE')
ALGORITHMS = ["RS256"]

def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header"""
    auth = request.headers.get("Authorization", None)
    if not auth:
        abort(401, description="Authorization header is missing")

    parts = auth.split()
    if parts[0].lower() != "bearer":
        abort(401, description="Authorization header must start with Bearer")
    elif len(parts) == 1:
        abort(401, description="Token not found")
    elif len(parts) > 2:
        abort(401, description="Authorization header must be Bearer token")

    token = parts[1]
    return token

def verify_decode_jwt(token):
    """Decode and verify JWT"""
    try:
        jsonurl = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
    except Exception as e:
        abort(500, description="Error loading JWT keys: " + str(e))

    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )
            return payload
        except jwt.ExpiredSignatureError:
            abort(401, description="Token is expired")
        except jwt.JWTClaimsError:
            abort(401, description="Incorrect claims, please check the audience and issuer")
        except Exception as e:
            abort(400, description="Unable to parse authentication token: " + str(e))
    abort(400, description="Unable to find appropriate key")

def requires_auth(f):
    """Decorator to implement authorization"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            g.current_user = payload  # Add the decoded payload to the context
        except Exception as e:
            abort(401, description=str(e))
        return f(*args, **kwargs)
    return wrapper

