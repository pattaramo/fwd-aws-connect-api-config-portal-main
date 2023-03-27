from dataclasses import dataclass

import pytest
import pymysql
import os


@pytest.fixture()
def resource(request):
    # cleanup db
    from app.Database import Database
    
    connection = Database().get_connection()

    with connection:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "DELETE FROM `outbound_status`"
            # connection is autocommit.
            cursor.execute(sql)

    def teardown():
        print("teardown")
    request.addfinalizer(teardown)
    
    return "resource"

def test_app(resource):
    from app import lambda_function
    
    test_event = {
        'dialer_id': '12345',
        'call_strategy_id': '12345'
    }

    lambda_context = {
        "function_name": "test",
        "memory_limit_in_mb": 128,
        "invoked_function_arn": "arn:aws:lambda:eu-west-1:809313241:function:test",
        "aws_request_id": "52fdfc07-2182-154f-163f-5f0f9a621d72"
    }

    lambda_function.handler(test_event, lambda_context)

