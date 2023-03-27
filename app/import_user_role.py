from aws_lambda_powertools import Logger
from database import Database
import utilities as util
import json


logger = Logger()


class UserRole:

    def __init__(self, config):
        self.config = config
        self.database = Database(config)

    def selectAll(self):
        logger.debug("selectAll start")

        json_data = []
        row_count = 0
        connection = self.database.get_connection()
        with connection:
            with connection.cursor() as cursor:
                #"SELECT * FROM change_history ORDER BY timestamp DESC LIMIT 1000"
                cursor.execute(
                    "SELECT * FROM user_role"
                )
                #row_headers = [x[0] for x in mycursor.description]
                results = cursor.fetchall()
                for result in results:
                    json_data.append(result)
                print (json_data)
        return {
            "method": "role_select_all",
            "status": "success",
            "rows": row_count,
            "data": json_data
        }
    
    def insert(self, data):
        fields = {
            "data": data,
        }
        logger.debug("insert New data", extra=fields)

        row_count = 0
        connection = self.database.get_connection()
        with connection:
            with connection.cursor() as cursor:
                sql = "INSERT INTO user_role (role, recordvoice,userview,historyview,deleterecord,recorddownload,edituser,deleteuser,viewrole,editrole) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (data['role'], data['recordvoice'], data['userview'], data['historyview'], data['deleterecord'], data['recorddownload']
                       , data['edituser'], data['deleteuser'], data['viewrole'], data['editrole'])
                cursor.execute(sql, val)
                row_count = cursor.rowcount
        return {
            "method": "campaign_insert",
            "status": "success",
            "rows": row_count
        }

    def update(self, data):
        fields = {
            "data": data,
        }
        logger.debug("update start", extra=fields)

        row_count = 0
        connection = self.database.get_connection()
        with connection:
            with connection.cursor() as cursor:
                sql = "UPDATE profile_user SET `id` = %s, `role` = %s, `userview`= %s,`historyview`= %s,`deleterecord`= %s,`recorddownload`= %s,`edituser`= %s,`deleteuser`= %s,`viewrole`= %s,`editrole`= %s ;"
                cursor.execute(
                    sql, (data['id'], data['role'], data['recordvoice'], data['userview'], data['historyview'], data['deleterecord'], data['recorddownload']
                       , data['edituser'], data['deleteuser'], data['viewrole'], data['editrole']))

                row_count = cursor.rowcount
        return {
            "method": "campaign_update",
            "status": "success",
            "rows": row_count
        }

    def remove_role_list(self, id):
        logger.debug(f"remove_role_list start {id}")
        connection = self.database.get_connection()
        with connection:
            with connection.cursor() as cursor:
                # Delete the record from the table
                cursor.execute(f"DELETE FROM user_role WHERE id='{id}'")


class ClientException(Exception):
    pass