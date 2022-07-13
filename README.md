# foundation-models-for-dbt-entity-resolution
Playground for using large language models into the Modern Data Stack for entity resolution


## Setup

We have three main prerequisite to be able to run the project:

* access to OpenAI endpoint through an API key;
* access to AWS to deploy a lambda function (we use the serverless framework for convenience and best practice, but in theory everything below can be done manually in the console);
* a Snowflake account properly connected to our AWS account;
* a working dbt-core setup on Snowflake.

We will go over these items in turn.

### Open AI

Get an API token for GPT-3 by signing up in the [OpenAI portal](https://openai.com/api/). You can test your API is working as expected by running `API_KEY=my_key python open_ai_playground.py` in the `src` directory (replace `my_key` with your GPT-3 API token).

### Serverless

Make sure you have installed the [serverless CLI](https://www.serverless.com/framework/) and you set it up properly with your [AWS](https://www.serverless.com/framework/docs/providers/aws/guide/credentials/); when serverless is installed, add the [plugin](https://www.serverless.com/blog/serverless-python-packaging/) to package `requirements.txt` automatically. 

Deploy the lambda function with two simple commands (the region in your `serverless.yml` file should be the same one in which your Snowflake account lives):

* cd into `src/serverless`
* run `AWS_PROFILE=tooso serverless deploy` (where `AWS_PROFILE` is the profile with serverless permissions, in case you have many on your machines - if you use the default AWS profile, you can omit the env);
* check in your AWS console that the lambda function _and_ the corresponding AWS Gateway integration are live.

Once the function is up and running, it's time to connect your Snowflake account to API Gateway.

### Snowflake

Setting up Snowflake to talk to AWS Lambda is a bit of a pain still: there is an official Snowflake tutorial, but we found easier to actually follow [this guide](https://interworks.com/blog/2020/08/14/zero-to-snowflake-setting-up-snowflake-external-functions-with-aws-lambda/): our summation lambda function in `handler.py` is actually built from that tutorial, as a simple verification the Snowflake to AWS connection works.

However you decide to proceed to setup the connection, our code assume you created a DB, SCHEMA and FUNCTION according to the above tutorial, that is, resulting in something like the commands:

```
CREATE OR REPLACE database external_functions;
CREATE OR REPLACE schema external_functions.lambda;
CREATE OR REPLACE external function external_functions.lambda.resolution(x varchar, y varchar) ...
```

In other words, you should be able to run this query in your Snowflake account after the setup above is completed and get a result:

```
SELECT external_functions.lambda.resolution('hello', 'world');
```

If you end up placing your external function somewhere else, _just make sure to replace the relevant calls in the dbt files_ to make sure your SQL and your setup are consistent.

### dbt

TBC

## Run entity resolution in dbt

TBC