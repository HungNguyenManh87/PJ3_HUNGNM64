import json
from flask import request, _request_ctx_stack,abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen
import logging
from logging import Formatter, FileHandler

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('./auth.log', 'w', 'utf-8')
root_logger.addHandler(handler)

AUTH0_DOMAIN = 'dev-jpudacity.jp.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'Pj3'
# AUTH0_CLIENT_ID="bVHHAQFGCGo55WRp5yUCH0syaYXLpFHu"
# AUTH0_CLIENT_SECRET="ZZNH2c7BNbV9aw8jRihLdAzDX_moxjWCQXZbU0ae037pAcbAHetooSuRuxWoXKRl"
# AUTH0_DOMAIN="dev-jpudacity.jp.auth0.com"
# APP_SECRET_KEY=


## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header
def get_token_auth_header():
    root_logger.info("===ahth.py :get_token_auth_header===")
    res_auth = request.headers.get('Authorization', None)
    if not res_auth:
        abort(401)

    parts = res_auth.split(' ')
    if parts[0].lower() != 'bearer':
        abort(401)

    elif len(parts) == 1:
        abort(401)

    elif len(parts) > 2:
        abort(401)

    return parts[1]
    
## check Permissions
def check_permissions(permission, payload):
    root_logger.info("===ahth.py :check_permissions===")
    if 'permissions' not in payload:
        abort(400)
    if permission not in payload['permissions']:
        abort(403)
    return True

def verify_decode_jwt(token):
    root_logger.info("===ahth.py : verify_decode_jwt===")
    res_json = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(res_json.read())
    header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'it should be an Auth0 token with key id (kid).'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except Exception as e:
                abort(401)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator