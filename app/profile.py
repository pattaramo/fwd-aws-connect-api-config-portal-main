from aws_lambda_powertools import Logger
from database import Database
from datetime import datetime
import utilities as util
import uuid
import json

logger = Logger()


class Profile:

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
                cursor.execute(
                    "SELECT profile_user.id, profile_user.email, user_role.role FROM profile_user join user_role WHERE profile_user.role = user_role.id "
                )
                results = cursor.fetchall()
                for result in results:
                    json_data.append(result)
        return {
            "method": "profile_select_all",
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
                sql = "INSERT INTO profile_user (email, role) VALUES (%s, %s)"
                val = (data['email'],data['role'])
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
                sql = "UPDATE profile_user SET `role` = %s WHERE id = %s ;"
                cursor.execute(sql, (data['role'], data['id']))
                row_count = cursor.rowcount
        return {
            "method": "campaign_update",
            "status": "success",
            "rows": row_count
        },
    def remove_profile_list(self, id):
        logger.debug(f"remove_from_list start {id}")
        connection = self.database.get_connection()
        with connection:
            with connection.cursor() as cursor:
                    # Delete the record from the table
                    cursor.execute(f"DELETE FROM profile_user WHERE id='{id}'")
        
class ClientException(Exception):
    pass
