import json, base64, os

AUTH_REDIRECT = os.environ['AUTH_REDIRECT']
LOGIN_URL = os.environ['LOGIN_URL']

loginRedirect = {
    'statusCode': 303,
    'headers': {
        'Content-Type': 'text/html',
        'Location': AUTH_REDIRECT,
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Methods': '*'
    }
}

loginPage = {
    'statusCode': 303,
    'headers': {
        'Content-Type': 'text/html',
        'Location': LOGIN_URL,
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Methods': '*'
    }
}

optionsResponse = {
    'statusCode': 204,
    'headers': {
        'Content-Type': 'text/html',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Methods': '*'
    },
    'isBase64Encoded': False
}


def setResponse(code, desc, body):
    result = {
        'statusCode': code,
        'headers': {
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*'
        },
        'isBase64Encoded': False,
    }
    if body != None:
        result['body'] = json.dumps(body)
    return result


def decodeBase64(encryptString):
    base64_bytes = encryptString.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')
    return message


def splitBodyMessage(keyword, messageString):
    mysplit = messageString.split('&' + keyword + '=')
    if len(mysplit) > 0:
        return mysplit[1]
    else:
        return None


def getCookie(keyword, messageString):
    mysplit = messageString.split(keyword + '=')
    if len(mysplit) > 0:
        return mysplit[1]
    else:
        return None


if __name__ == "__main__":
    decodeStr = decodeBase64(
        'c3RhdGU9MTIzNCZjb2RlPWdlNjVVMzFkSERRbzdJdWJSNkV1dUs0RGlsSzR4Q0JOem1FcUVhSjZYa28maWRfdG9rZW49ZXlKcmFXUWlPaUpOU213NVpuWkNXRU13Y2xCTlowZzFOMGRrUW5BeE9UaFFTbE5KZG5sd1MzWlBSV00xTFhoeVZIRTBJaXdpWVd4bklqb2lVbE15TlRZaWZRLmV5SnpkV0lpT2lJd01IVTBZbUZuWjJKd1RHbG9SazVDTVRWa055SXNJbTVoYldVaU9pSlFaWFJsY2lCUVlYSnJaWElpTENKc2IyTmhiR1VpT2lKbGJsOVZVeUlzSW1WdFlXbHNJam9pY0dWMFpYSXVjR0Z5YTJWeVFHZHRZV2xzTG1OdmJTSXNJblpsY2lJNk1Td2lhWE56SWpvaWFIUjBjSE02THk5a1pYWXRNREU1TWpJek1UWXViMnQwWVM1amIyMGlMQ0poZFdRaU9pSXdiMkUwWm1zeVpqUTRSbHBLTmtVeFREVmtOeUlzSW1saGRDSTZNVFkwT0RjNE9UYzVPU3dpWlhod0lqb3hOalE0Tnprek16azVMQ0pxZEdraU9pSkpSQzVaUlRGNVlucEVaVVpaWjBkRFkyMTRabVJSWlcxek9XdDVNblZPWmpKblNIcE9ObTlZWWpKc01Vc3dJaXdpWVcxeUlqcGJJbkIzWkNKZExDSnBaSEFpT2lJd01HODBZams1YTNJMGQxWXdaSE53TmpWa055SXNJbTV2Ym1ObElqb2lWVUpIVnlJc0luQnlaV1psY25KbFpGOTFjMlZ5Ym1GdFpTSTZJbkJsZEdWeUxuQmhjbXRsY2tCbmJXRnBiQzVqYjIwaUxDSm5hWFpsYmw5dVlXMWxJam9pVUdWMFpYSWlMQ0ptWVcxcGJIbGZibUZ0WlNJNklsQmhjbXRsY2lJc0lucHZibVZwYm1adklqb2lRVzFsY21sallTOU1iM05mUVc1blpXeGxjeUlzSW5Wd1pHRjBaV1JmWVhRaU9qRTJORGcyTWpNNU1UY3NJbVZ0WVdsc1gzWmxjbWxtYVdWa0lqcDBjblZsTENKaGRYUm9YM1JwYldVaU9qRTJORGczT0Rrd016UXNJbU5mYUdGemFDSTZJa0UxTW5sNFRXOHRRM2xtU0VVdFpsTnlZbEJ5Ym1jaWZRLkZ2Q1UzWnNOU3phX0VjVGNsMjhnaFRUQ2t5ZFlER0pkRkZLUUprZ2hqbFppTk9GU05od0x1X0h2NWRfbGdKMTlTTF9qa1pYSWstcTVjV2s5YUtxS3NPLUppakdYYTBxc0FZM09CalJNRTlhQWVkWDJWWEc5cjhUOFNGRjN2a0pIWnpmZWVoYTc3OTNQcUhGb0tWSjFYQWZQTW9PUU45dlF0UF9pRHFmUzRsVkppaUlaVVprQ2NHYTJxWjJZVnhSaU1OWXJJaERGbDhXc3VIMUZiUVJFQVM1U0NTZlU1T01YUnZEckJ6SUY0cmhmYlNOMGc1MlJEczM1ZUh4SFJlUlVnOUl1dVQtakt2UWVxZHhaLTJ0VUdENTc1UkV1eEFJeXpOMXk2clpCTnJFLTZqdmoxUzlZZkNXcHlzQ2c2YXI3UlpobHdXV0dFSnNwZ3FLQXpYTXZZdw=='
    )
    id_token = splitBodyMessage('id_token', decodeStr)
    print(id_token)