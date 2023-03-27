import jwt, json, os
from jwt import PyJWKClient
from aws_lambda_powertools import Logger
import utilities as util

AUTH_AUDIENCE = os.environ['AUTH_AUDIENCE']
AUTH_KEY = os.environ['AUTH_PUBLIC_KEY']

logger = Logger(service="config-portal-api")


class Auth:

    def __init__(self):
        self.config = ""

    def decodeJWT(self, token):
        try:
            url = AUTH_KEY
            jwks_client = PyJWKClient(url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            token_claims = jwt.decode(token,
                                      signing_key.key,
                                      algorithms=["RS256"],
                                      audience=AUTH_AUDIENCE,
                                      options={"verify_exp": True})
            return util.setResponse(200, "signature has verified",
                                    token_claims)

        # except jwt.exceptions.InvalidAudienceError as e:
        #     exception_message = f"{type(e).__name__} {str(e)}"[:100]
        #     logger.info(f"401 {exception_message}")
        #     return util.setResponse(500, exception_message, None)

        # except jwt.exceptions.ExpiredSignatureError as ex:
        #     exception_message = f"{type(e).__name__} {str(e)}"[:100]
        #     logger.info(f"401 {exception_message}")
        #     return util.setResponse(401, exception_message, None)

        # except jwt.exceptions.InvalidTokenError as ex:
        #     exception_message = f"{type(e).__name__} {str(e)}"[:100]
        #     logger.info(f"401 {exception_message}")
        #     return util.setResponse(401, exception_message, None)

        except Exception as e:
            exception_message = f"{type(e).__name__} {str(e)}"[:100]
            logger.info(f"401 {exception_message}")
            return util.setResponse(401, exception_message, None)

    def callbackRedirect(self, token, token_json):
        location = 'https://fwd-playback-portal.s3.ap-southeast-1.amazonaws.com/playback-portal-s3/prefer.html?jwt={}&jwt_json={}'.format(
            token, json.dumps(token_json))
        print(location)
        return {
            'statusCode': 303,
            'headers': {
                'Content-Type': 'text/html',
                'Location': location,
            }
        }
