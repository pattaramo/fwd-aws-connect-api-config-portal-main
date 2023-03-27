from aws_lambda_powertools import Logger
from database import Database

logger = Logger()


class Salesforce:

    def __init__(self, config):
        self.config = config
        self.database = Database(config)

    def selectAll(self):
        logger.debug("selectAll start")
        json_data = []

        connection = self.database.get_connection()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM fwd_playback_detail")
                results = cursor.fetchall()
            for result in results:
                json_data.append(formatted_result(result))


def formatted_result(result):
    result['create_on'] = str(result['create_on'])
    result['update_on'] = str(result['update_on'])
    return result


def validateInput(data):
    if len(data['id']) != 36:
        return False
    # If otherwise exception is true
    return True
