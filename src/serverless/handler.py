import json
import os
import requests
import time


# global OpenAI vars
OPEN_AI_URL = 'https://api.openai.com/v1/completions'
HEADERS = { 
    'content-type': 'application/json', 
    "Authorization": "Bearer {}".format(os.environ['API_KEY'])
    }
TEMPLATE_PROMPTING = """
Product A is {}. Product B is {}. Are Product A and Product B equivalent? 
"""

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


def parse_open_ai_response(text_response: str):
    # troncate at first token
    cleaned_token = text_response.strip().lower().split(' ')[0]
    if cleaned_token == 'yes':
        return True
    elif cleaned_token == 'no':
        return False
    else:
        print("====> Unexpected answer: {}".format(text_response))

    return False


def resolution(event, context):
    """
    This is the entity resolution function, which is just wrapping the original OpenAI APIs with some 
    prompt engineering.

    Code inspired by: https://arxiv.org/pdf/2205.09911.pdf

    """
    # debug
    print(event)
    times = []
    status_code = 200
    response = []
    try:
        body = json.loads(event['body'])
        rows = body['data']
        for row in rows:
            start = time.time()
            data = {
                # TODO: should make model a parameter we can pass from Snowflake!
                "model": "text-davinci-002",
                # TODO: should make temp a parameter we can pass from Snowflake!
                "temperature": 0,  
                "max_tokens": 10,
                # TODO: we could modify the initial SQL queries to have ARRAYS, therefore using "prompt"
                # as an array of prompts to save some roundtrip time...
                "prompt": TEMPLATE_PROMPTING.format(row[1], row[2])
            }
            payload = json.dumps(data)
            r = requests.post(OPEN_AI_URL, data=payload, headers=HEADERS)
            open_ai_response = json.loads(r.text)["choices"][0]['text'].strip()
            cnt_match = parse_open_ai_response(open_ai_response)
            # appen the current row number (Snowflake requirement) and boolean indicating a match
            response.append([row[0], cnt_match])
            times.append(time.time() - start)
        # debug
        print(sum(times), sum(times) / len(times))
    except Exception as err:
        status_code = 400
        response = str(err)
    # print in cloudwatch for debug!
    print(response)
    # return the response to the client
    return wrap_response(status_code, response)

