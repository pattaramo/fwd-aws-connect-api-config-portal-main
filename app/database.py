import boto3, os, pymysql
from pymysql.constants import CLIENT

client = boto3.client('rds')
DB_NAME = os.environ['DB_NAME']

class Database:
    def __init__(self, config):
        self.config = config

    def get_connection(self):
        db_host = self.config.get('database_host')
        db_port = self.config.get('db_port')
        db_username = self.config.get('db_username')
        db_password = self.config.get('db_password')
        db_database_name = DB_NAME
        db_timeout = self.config.get('db_timeout')

        connection = pymysql.connect(host=db_host,
                                port=int(db_port),
                                user=db_username,
                                password=db_password,
                                database=db_database_name,
                                #ssl={'ca': db_ca} ,
                                ssl_verify_cert=False,
                                cursorclass=pymysql.cursors.DictCursor,
                                autocommit=True,
                                read_timeout=int(db_timeout),
                                write_timeout=int(db_timeout),
                                client_flag=CLIENT.MULTI_STATEMENTS)
        return connection
