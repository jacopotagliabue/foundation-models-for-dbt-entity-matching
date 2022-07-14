# foundation-models-for-dbt-entity-resolution
Playground for using large language models into the Modern Data Stack for entity resolution


## Overview

TL;DR a real-world sketch implementation for the Modern Data Stack of the ideas in "Can Foundation Models Wrangle Your Data?".



While simple, it's pretty cool we could "port" [an academic paper](https://arxiv.org/pdf/2205.09911.pdf) to a real-world toolchain in a couple of hours; it's even cooler that, once AWS is setup, every other functional piece of the puzzle is pure SQL and can be run with no explicit infrastructure work at all (it may expensive for API reasons tough!)

_Note: by running this project you may incur in API costs - be careful!_

## Setup

We have four main prerequisite to be able to run the project:

* access to OpenAI endpoint through an API key;
* access to AWS to deploy a lambda function (we use the serverless framework for convenience and best practice, but in theory everything below can be done manually in the console);
* a Snowflake account properly connected to our AWS account;
* a working dbt-core setup on Snowflake.

We will go over these items in turn (feel free to skip the sessions that don't apply to you / you're familiar with).

### Python

Setup a virtual environment with the project dependencies:

* `python -m venv venv`
* `source venv/bin/activate`
* `pip install -r requirements.txt`

### Open AI

Get an API token for GPT-3 by signing up in the [OpenAI portal](https://openai.com/api/). You can test your API is working as expected by running `API_KEY=my_key python open_ai_playground.py` in the `src` directory (replace `my_key` with your GPT-3 API token).

Now, cd into the `src/serverless` folder and create there a file named `.env` (do _not_ commit it!) with the following structure `API_KEY=my_key`: this will be used automatically by `serverless` to populate an `env` with our token in the AWS lambda.

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

On top of installing the open source package (already included in the `requirements.txt`), make sure dbt points to your Snowflake instance with the proper [dbt_profile](https://docs.getdbt.com/dbt-cli/configure-your-profile) - it may be stating the obvious, but _make sure the dbt role has access to the UDF we registered in Snowflake above_ (if not, assign the relevant privileges!). 

To populate your target schema with the data needed for the project, cd into `src/dbt` and run `dbt seed`. Data  (in the `data` folder) for seeding the initial tables comes from the [Walmart-Amazon dataset](https://github.com/anhaidgroup/deepmatcher/blob/master/Datasets.md), using a standard format (i.e. other datasets in the same web directory should mostly work with the same exact flow, minus some minor feature wrangling in dbt).

Once you run the script, check your Snowflake for the new tables:

![Raw tables in Snowflake](/images/raw_tables.png)

## Run entity resolution in dbt

_Note (again): by running this project you may incur in API costs - be careful and proceed incrementally!_

To run the flow, simply cd into the `src/dbt` folder and type `dbt run`. The dbt DAG will pre-process the raw data about Walmart and Amazon product features and serialize the information into an `ENTITY_MATCHING_INPUT` table:

![Input table](/images/input.png)

As a final step in the DAG, dbt will use the `external_functions.lambda.resolution` we registered in Snowflake above to run our lambda wrapper around GPT3 capabilities. The results will be parsed and convert to boolean in the lambda, and dbt will finally materialize a table containing the two input products, the true label from the dataset, and a boolean with the result of the entity matching:

![Output table](/images/output.png)

## TO-DOs

This project has been drafted during a not-so-exciting afternoon of academic talks, so plenty of things to add / change / improve (some of which are just `TODOs` in the code). Some obvious open points:

* play around with serialization of product info in `entity_matching_input.sql`;
* play around with prompting in `handler.py`;
* add a metrics table after the classification, to see how the model is doing;

## Acknowledgements

The recent paper ["Can Foundation Models Wrangle Your Data?"](https://arxiv.org/pdf/2205.09911.pdf) was the obvious source of inspiration! 

## License

All the code is provided with (really) no guarantee and "as is", and it is freely available under a MIT license.