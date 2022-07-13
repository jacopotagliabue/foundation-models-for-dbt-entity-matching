import json
import os


def wrap_response(status_code: int, response):
    return {
        'statusCode': status_code,
        'headers': {
            # this makes the function callable across domains!
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json' 
        },
        'body' : json.dumps({"data": response})
        }


def summation(event, context):
    """
    This is a test function with a trivial Python logic just to check the integration with Snowflake.

    Code inspired by: https://interworks.com/blog/2020/08/14/zero-to-snowflake-setting-up-snowflake-external-functions-with-aws-lambda/

    """
    # variables we are going to return to the client
    status_code = 200
    response = []
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
        status_code = 400
        response = str(err)
    # print in cloudwatch for debug!
    print(response)
    # return the response to the client
    return wrap_response(status_code, response)


def resolution(event, context):
    """
    This is the entity resolution function, which is just wrapping the original OpenAI APIs with some 
    prompt engineering.

    Code inspired by: https://arxiv.org/pdf/2205.09911.pdf

    """
    # debug
    print(event)
    # just making sure we can read the API KEY
    assert os.environ.get('API_KEY', None) is not None
    status_code = 200
    response = []
    body = json.loads(event['body'])
    rows = body['data']
    print(rows)
    response = [[row[0], True] for row in rows]
    return wrap_response(status_code, response)

