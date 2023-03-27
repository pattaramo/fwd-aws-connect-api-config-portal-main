from aws_lambda_powertools import Logger
from database import Database

logger = Logger()


class History:

    def __init__(self, config):
        self.config = config
        self.database = Database(config)

    def selectAll(self,start_date,end_date):
        logger.debug("selectAll start")

        json_data = []
        row_count = 0
        connection = self.database.get_connection()
        with connection:
            with connection.cursor() as cursor:
                #"SELECT * FROM change_history ORDER BY timestamp DESC LIMIT 1000"
                cursor.execute(
                    f"SELECT * FROM change_history WHERE timestamp BETWEEN '{start_date}' AND '{end_date}';"
                )
                #row_headers = [x[0] for x in mycursor.description]
                results = cursor.fetchall()
                for result in results:
                    json_data.append(formatted_result(result))
                print (json_data)
        return {
            "method": "history_select_all",
            "status": "success",
            "rows": row_count,
            "data": json_data
        }

    def insert(self, change_by, action, timestamp, resource_id):
        fields = {
            "change_by": change_by,
            "action": action,
            "timestamp": timestamp,
            "resource_id": resource_id
        }
        logger.debug("insert change_history", extra=fields)

        connection = self.database.get_connection()
        with connection:
            with connection.cursor() as cursor:
                sql = "INSERT INTO change_history (change_by, action, timestamp, resource_id) VALUES (%s, %s, %s, %s)"
                val = (change_by, action, timestamp, resource_id)
                cursor.execute(sql, val)

        return {
            "method": "history_insert",
            "status": "success"
        }


def formatted_result(result):
    result['change_by'] = str(result['change_by'])
    result['action'] = str(result['action'])
    result['timestamp'] = str(result['timestamp'])
    result['resource_id'] = str(result['resource_id'])
   
    return result

def validateInput(data):
    try:
        if data['id'] and len(data['id']) != 36:
            raise Exception("id")
        if data['change_by'] and len(data['change_by']) != 100:
            raise Exception("change_by")
        if data['action'] and len(data['action']) != 500:
            raise Exception("action")
        if data['resource_id'] and len(data['resource_id']) != 36:
            raise Exception("resource_id")

    except Exception as ex:
        print('exception: ' + str(ex))
        raise Exception("Invalid input: " + str(ex))

    # If otherwise exception is true
    return True