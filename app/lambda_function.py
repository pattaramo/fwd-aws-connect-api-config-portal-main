import os, json
from aws_lambda_powertools import Logger
from aws_lambda_powertools import Tracer
from urllib.parse import parse_qs
from datetime import datetime, timedelta

from ssm import SsmConfig
from search import Search
from profile import Profile
from history import History
from salesforce import Salesforce
from authentication import Auth
from voice_import import Voice
from import_user_role import UserRole
import utilities as util

tracer = Tracer()
logger = Logger()

ssm_parameter_path = os.environ['SSM_PARAMETER_PATH']
ssm_config = None

@logger.inject_lambda_context(log_event=False)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    global ssm_config
    auth = Auth()

    # Initialize ssm_config if it doesn't yet exist
    if ssm_config is None:
        ssm = SsmConfig()
        logger.debug("Loading SsmConfig")
        ssm.load_config(ssm_parameter_path)
        ssm_config = ssm

    try:
        path = event['path']
        print(path)
        headers = event['headers']
        query = event['queryStringParameters']
        method = event['httpMethod']
        body = event['body']
        id = None

        logger.info(f"{method} {path}")
        logger.info(headers)
        logger.info(body)
        

        client_ip = headers['x-forwarded-for'] if 'x-forwarded-for' in headers else ''
        logger.append_keys(client_ip=client_ip)

        # =============================
        # No Authorization check method
        # =============================

        # ============= Check Request Method CORS =============
        if method == 'OPTIONS':
            # Enable CORS
            return util.optionsResponse

        # ======= Initial URL to Authentication Process =======
        if path == "/playback-portal/authentication/login":
            logger.info(path)
            if method == "GET":
                logger.info(f"{method} {path}")
                logger.info(util.loginRedirect)
                return util.loginRedirect
         
        # ============ Callback Process Validation ============
        elif path == "/playback-portal/authentication/callback":
            if method == "POST":
                
                #decodeMsg = util.decodeBase64(body)
                id_token = util.splitBodyMessage('id_token', body)
                logger.info(id_token)

                result = auth.decodeJWT(id_token)
                print(result)

                if result['statusCode'] == 200:
                    callback = auth.callbackRedirect(id_token, result['body'])
                    logger.info(callback)
                    return callback
                elif result['statusCode'] == 401:
                    print('Error 401')
                    return util.loginRedirect
                else:
                    print('Error 500')
                    return util.setResponse(500, 'callback error', None)
                
        # =============================
        # Authorization required
        # =============================
        if not "Authorization" in headers:
            message = f"request unauthorize. redirect to login"
            logger.info(message)
            return util.setResponse(401, message, None)

        id_token = headers['Authorization']
        auth_info = auth.decodeJWT(id_token)
        if auth_info['statusCode'] != 200:
            logger.info(f"request unauthorize from. redirect to login")
            return util.setResponse(401, auth_info['statusDescription'], None)

        username = json.loads(auth_info['body'])['preferred_username']
        logger.append_keys(username=username)

        # ================== Search API =====================
        if path == "/playback-portal/search":
            search = Search(ssm_config.get_config())
            logger.info(path)

            if method == "GET":
                start_date = query.get('active_start_date')
                end_date = query.get('active_end_date')
                results = search.selectAll(start_date, end_date)
                resp = results['data']
                return util.setResponse(200, 'success', resp)
            else:
                return util.setResponse(404, 'method not found', None)

        
        # ================== DELETE Search API =====================
        if path == "/playback-portal/search/delete":
            search = Search(ssm_config.get_config())
            history = History(ssm_config.get_config())
            logger.info(path)

            if method == "DELETE":
                id = query.get('id')
                print (id)
                resp = search.remove_from_list(id)
                dt = datetime.now() + timedelta(hours=7) 
                timestamp= dt.strftime("%Y-%m-%d %H:%M:%S")
                history.insert(change_by= username,
                                    action="Delete",
                                    timestamp= timestamp,
                                    resource_id=id)
            else:
                return util.setResponse(404, 'method not found', None)

            return util.setResponse(200, 'success', resp)
        
        #====================== Voice import API ========================
        elif path == f"/playback-portal/search/voice":
            voice = Voice(ssm_config.get_config())
            logger.info(path)

            if method == "GET":
                voicecallid = query.get('id')
                logger.info(voicecallid)
                if voicecallid is None:
                    return util.setResponse(404, 'id not found', None)
                results = voice.selectVoice(voicecallid)
                resp = results
                #print(resp)
            else:
                return util.setResponse(404, 'method not found', None)

            return util.setResponse(200, 'success', str(resp))
        
        # ==================== History API =======================
        elif path == "/playback-portal/history":
            history = History(ssm_config.get_config())
            if method == "GET":
                start_date = query.get('active_start_date')
                end_date = query.get('active_end_date')
                results = history.selectAll(start_date, end_date)
                resp = results['data']
            else:
                return util.setResponse(404, 'method not found', None)

            return util.setResponse(200, 'success', resp)
        
        # ==================== user_role API =======================
        elif path == "/playback-portal/user_role":
            user_role = UserRole(ssm_config.get_config())
            if method == "GET":
                results = user_role.selectAll()
                resp = results['data']

            elif method == "POST":
                json_body = json.loads(body)
                resp = user_role.insert(json_body)
                
            elif method == "PUT":
                json_body = json.loads(body)
                resp = user_role.update(json_body)
                
            else:
                return util.setResponse(404, 'method not found', None)

            return util.setResponse(200, 'success', resp)
        
        # ==================== DELETE user_role API =======================
        elif path == "/playback-portal/user_role/delete":
            user_role = UserRole(ssm_config.get_config())
            logger.info(path)

            if method == "DELETE":
                id = query.get('id')
                print (id)
                resp = user_role.remove_role_list(id)
                
            else:
                return util.setResponse(404, 'method not found', None)

            return util.setResponse(200, 'success', resp)   

        # ===================== Profile API ====================
        elif path == "/playback-portal/profile":
            profile = Profile(ssm_config.get_config())

            if method == "GET":
                results = profile.selectAll()
                resp = results['data']

            elif method == "POST":
                json_body = json.loads(body)
                resp = profile.insert(json_body)
                
            elif method == "PUT":
                json_body = json.loads(body)
                resp = profile.update(json_body)
                
            else:
                return util.setResponse(404, 'method not found', None)

            return util.setResponse(200, 'success', resp)
        
        # ==================== DELETE profile API =======================
        elif path == "/playback-portal/profile/delete":
            profile = Profile(ssm_config.get_config())
            logger.info(path)

            if method == "DELETE":
                id = query.get('id')
                print (id)
                resp = profile.remove_profile_list(id)
            else:
                return util.setResponse(404, 'method not found', None)

            return util.setResponse(200, 'success', resp)
        
        '''elif path == f"/playback-portal/search/voice":
            voice = Voice(ssm_config.get_config())
            logger.info(path)

            if method == "GET":
                voicecallid = query.get('id')
                logger.info(voicecallid)
                if voicecallid is None:
                    return util.setResponse(404, 'id not found', None)
                results = voice.selectVoice(voicecallid)
                resp = {
                        'statusCode': 200,
                        'headers': {
                            'Content-Type': 'application/json'
                            },
                        'body' : results
                        }
                return results
            else:
                return util.setResponse(404, 'method not found', None)'''
        
    

    except Exception as e:
        '''exception_message = f"{type(e).__name__} {str(e)}"[:100]
        logger.warn(f"main exception {type(e).__name__} {exception_message}")'''
        logger.info(str(e))
        return util.setResponse(500, 'exception error', None)
        '''jsonEx = json.loads(str(e))
        if jsonEx['statusCode']:
            return util.setResponse(jsonEx['statusCode'],
                                    jsonEx['statusDescription'], None)
        else:
            return util.setResponse(500, exception_message, None)'''


if __name__ == "__main__":
    event = {
        'path': '/playback-portal/search',
        'headers': {
            'authorization':
            'eyJraWQiOiJNSmw5ZnZCWEMwclBNZ0g1N0dkQnAxOThQSlNJdnlwS3ZPRWM1LXhyVHE0IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIwMHU0YmFnZ2JwTGloRk5CMTVkNyIsIm5hbWUiOiJQZXRlciBQYXJrZXIiLCJsb2NhbGUiOiJlbl9VUyIsImVtYWlsIjoicGV0ZXIucGFya2VyQGdtYWlsLmNvbSIsInZlciI6MSwiaXNzIjoiaHR0cHM6Ly9kZXYtMDE5MjIzMTYub2t0YS5jb20iLCJhdWQiOiIwb2E0ZmsyZjQ4RlpKNkUxTDVkNyIsImlhdCI6MTY1MDQ1MjIyMiwiZXhwIjoxNjUwNDU1ODIyLCJqdGkiOiJJRC5DcHRTNjY3SWs4VGpfbS1NTG5RNDlBR0NDS2Z6TWZ5LTVlR29HR3hKdnpjIiwiYW1yIjpbInB3ZCJdLCJpZHAiOiIwMG80Yjk5a3I0d1YwZHNwNjVkNyIsIm5vbmNlIjoiVUJHVyIsInByZWZlcnJlZF91c2VybmFtZSI6InBldGVyLnBhcmtlckBnbWFpbC5jb20iLCJnaXZlbl9uYW1lIjoiUGV0ZXIiLCJmYW1pbHlfbmFtZSI6IlBhcmtlciIsInpvbmVpbmZvIjoiQW1lcmljYS9Mb3NfQW5nZWxlcyIsInVwZGF0ZWRfYXQiOjE2NDg2MjM5MTcsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhdXRoX3RpbWUiOjE2NTA0NDEwMjUsImNfaGFzaCI6IlA2aVliSGtsbUhiNGJTVDFMd2l5NVEifQ.wwkjFHU9FcnEIcJQoJiwgiIGGNEwJ1b6Gc2ZqNiiZ_A5Rp1Df9Dolta57VAGjQ98dUSraKUYGazVHjpHa1QOJHSjjX7BxkSlkFwiSTJ5jCeprhxmfijB4MPDxkS9zX2qB-ooxqQUtChNqOr8p_wO8DHyoV4GZ_j5lxvONd1dzogkFc5gtBCNowWbrgxRaLQP5KlU2s2NJIpBN6sIiSK7JP1CAN0AJ72LAKZkHozXrhKttP3SXnK_w0JgHJQqF5df_eJIVy3KKfDIV7YlT6-K8b4LqVZlQgSNdZtuYjt8PmJf4rlUFScXSBIdMH-TMgu8coemNkHcFC0jxKijcwiVqg'
        },
        'queryStringParameters': "",
        'httpMethod': 'GET',
        'body': ''
    }

    class LambdaContext:
        function_name: str = "FWD-playback-portal-connect-API"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:ap-southeast-1:234620393636:function:FWD-playback-portal-connect-API"
        aws_request_id: str = "1eb2078a-0a77-497a-8896-c3e4fef60982"

    response = lambda_handler(event, LambdaContext())

    try:
        message = json.loads(response['body'])
    except:
        message = response
    print(json.dumps(message, sort_keys=True, indent=4))