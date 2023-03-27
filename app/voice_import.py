from aws_lambda_powertools import Logger
from database import Database
import utilities as util
import json
import boto3
import base64
from datetime import datetime, timedelta
import urllib.parse
import boto3, os, pymysql

logger = Logger()




class Voice:
    def __init__(self, config):
        self.config = config
        self.database = Database(config)
        
    
     
    def selectVoice(self,voicecallid):
            logger.debug("selectVoice start")
            json_data = []
            connection = self.database.get_connection()
            with connection:
                logger.info("line 23")
                with connection.cursor() as cursor:
                    logger.info("line 25")
                    cursor.execute(
                        f"SELECT voicepath FROM fwd_voicerecord_path WHERE voicecallid='{voicecallid}'")
                    print (f"SELECT voicepath FROM fwd_voicerecord_path WHERE voicecallid='{voicecallid}'")
                    results = cursor.fetchall()
                logger.info (results)
                    
                for result in results:
                    json_data.append(formatted_result(result))
                logger.info (json_data)


                s3_parts = json_data[0]['voicepath'].split('/')
                bucket_name = 'amazon-connect-154981430904'
                #bucket_name = s3_parts[2]
                object_key = '/'.join(s3_parts[3:])
                #object_key = 'connect/fwd-lab/CallRecordings/2023/01/13/128208e7-28ec-46e0-9006-a37b3d67b88a_20230113T10:21_UTC.wav'
                print("Bucket name:", bucket_name)
                print("Object key:", object_key)

            
                client = boto3.client(
                's3',
                region_name='ap-southeast-1'
                )
                logger.info(client)
                '''try:
                    response = client.get_object(Bucket=bucket_name, Key=object_key)
                    #logger.info(response)
                    
                    #return response['Body'].read()
                    body = response['Body']#.read()
                    print (body)
                    #base64_data = base64.b64encode(body)
                    #print(base64_data)
                    
                    return body
                    
                except Exception as e:
                    logger.info(str(e))
                    return Exception({'error': str(e)}), 404'''

                try:
                    response = client.get_object(Bucket=bucket_name, Key=object_key)
                    data_bytes = response['Body'].read()
                    data_b64 = base64.b64encode(data_bytes)
                    data = {
                        "bucket_name": bucket_name,
                        "object_key": object_key,
                        "base64": data_b64
                        }
                    #logger.info(data)
                    return data
                
                except Exception as ex:
                    logger.error(str(ex))
                    '''raise HTTPException(status_code=500,
                                        detail="Error when load s3 content.") from ex'''
        
    
def formatted_result(result):
    result['voicepath'] = str(result['voicepath'])
    return result

class ClientException(Exception):
    pass