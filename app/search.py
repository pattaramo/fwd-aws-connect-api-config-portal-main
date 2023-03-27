from aws_lambda_powertools import Logger
from database import Database
from datetime import datetime
import utilities as util
import json


logger = Logger()


class Search:

    def __init__(self, config):
        self.config = config
        self.database = Database(config)
        self.update = self.update

    def selectAll(self,start_date,end_date):
        logger.debug("selectAll start")
        json_data = []
        row_count = 0
        connection = self.database.get_connection()
        with connection:
            with connection.cursor() as cursor:
                sql = f"SELECT id, fromphonenumber, callstartdatetime, callenddatetime, queuename FROM fwd_playback_detail WHERE callstartdatetime BETWEEN '{start_date}' AND '{end_date}';"
                print(sql)
                cursor.execute(sql)

                results = cursor.fetchall()
                for result in results:
                    json_data.append(formatted_result(result))

                row_count = cursor.rowcount

        return {
            "method": "campaign_select_all",
            "status": "success",
            "rows": row_count,
            "data": json_data
        }

    def update(self, data):
        fields = {
            "data": data,
        }
        logger.debug(f"update start {data['id']}", extra=fields)

        try:
            validateInput(data)
        except Exception as ex:
            raise ClientException(
                json.dumps(util.setResponse(400, str(ex), None)))

        row_count = 0
        connection = self.database.get_connection()
        with connection:
            with connection.cursor() as cursor:
                sql = "UPDATE fwd_playback_detail SET `fromphonenumber` = %s, `callstartdatetime` = %s, `callenddatetime` = %s, `queuename` = %s WHERE id = %s ;"
                cursor.execute(
                    sql, (data['fromPhoneNumber'], data['callStartDateTime'],
                        data['callEndDateTime'], data['queueName'], data['id']))

                row_count = cursor.rowcount
        return {
            "method": "update",
            "status": "success",
            "rows": row_count
        }

    def remove_from_list(self, id):
        logger.debug(f"remove_from_list start {id}")
        try:
            validateInput({'id': id})
            connection = self.database.get_connection()
            with connection:
                with connection.cursor() as cursor:
                    # Delete the record from the table
                    cursor.execute(f"DELETE FROM fwd_playback_detail WHERE id='{id}'")
        except Exception as ex:
            raise ClientException(json.dumps(util.setResponse(400, str(ex), None)))



def formatted_result(result):
    result['id'] = str(result['id'])
    result['fromphonenumber'] = str(result['fromphonenumber'])
    result['callstartdatetime'] = result['callstartdatetime'].strftime('%Y-%m-%d %H:%M:%S')
    result['callenddatetime'] = result['callenddatetime'].strftime('%Y-%m-%d %H:%M:%S')
    result['queuename'] = str(result['queuename'])
    
    return result


def validateInput(data):
    try:
        if data['id'] and len(data['id']) != 18:
            raise Exception("id")

    except Exception as ex:
        print('exception: ' + str(ex))
        raise Exception("Invalid input: " + str(ex))

    # If otherwise exception is true
    return True


class ClientException(Exception):
    pass