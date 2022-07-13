import json
import re


def summation(event, context):
    """
    This is a test function with a trivial Python logic just to check the integration
    with Snowflake.

    """
    # variables we are going to return to the client
    statusCode = 200
    response = ''
    # try/except is used for error handling
    try:
        # get the body as JSON and read the data array in the body
        body = json.loads(event['body'])
        rows = body['data']
        # debug
        print(rows)
        # loop through each row and sum the second and third entry
        # the first entry is the row index and we echo it back
        response = [[row[0], row[1] + row[2]] for row in rows]
    except Exception as err:
        statusCode = 400
        response = str(err)
    # print in cloudwatch for debug!
    print(response)
    # return the response to the client
    return {
        'statusCode': statusCode,
        'headers': { 'Content-Type': 'application/json' },
        'body' : json.dumps({"data": response})
        }