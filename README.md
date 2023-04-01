# Foundation Models for Entity Matching in dbt and Snowflake
Playground for using large language models into the Modern Data Stack for entity matching

## Update!

*IMPORTANT*: The original dbt + Snowflake project below has now *also* available in a local version with a smaller footprint, thanks to [marvin](https://www.askmarvin.ai/getting_started/installation/) and [dbt-duckdb](https://github.com/jwills/dbt-duckdb). Therefore:

* all the setup instructions below are still valid - note the original project is untouched, and it is not contained in the `src/original` folder, together with its `requirements.txt` file;
* the new tiny setup is self-contained, and can be accessed in the `marvin-duck` folder - check the brief README there to get started, but please continue reading this document for the motivation behind the project and how it works. If you like the new version, please let us know!

## Overview

TL;DR a real-world (sketch) implementation for the Modern Data Stack of the ideas in "Can Foundation Models Wrangle Your Data?". If you want to know more about the context and background for this work, che the TDS [blog post](https://towardsdatascience.com/is-this-you-entity-matching-in-the-modern-data-stack-with-large-language-models-19a730373b26) in collaboration with [Avanika](https://github.com/ANarayan).

Matching entities is not just an interesting research problem, but it is a pretty important piece of data pipelines, especially now that all data is centralized and recognizing the entities across different serializations is [pretty important](https://twitter.com/pdrmnvd/status/1541853280686333954?s=20&t=LG3FGFdk_h_rAf5yhHKfLQ). Inspired by the recent success of Large Language Models at, well, [lots of stuff](https://arxiv.org/pdf/2206.04615.pdf), we implement a (basically) no-code, pure SQL flow that runs entity matching directly in dbt+Snowflake flow. To do it, we abstract away [GPT3 API](https://beta.openai.com/examples) through AWS Lambda, and leverage Snwoflake external functions to make the predictions when dbt is materializing the proper table. In a nutshell, _this_ repo builds this:

![Logical flow](/images/flow.jpg)

If you're familiar with prompting, what happens is that we turned an entity matching task into an appropriate question for GPT3, "Are products A and B the same?" - the model generates a string (e.g. "Yes, they are") as the answer, and we intepret it back as a boolean prediction about A and B. In this way, we avoid the need to train, deploy and maintain _any machine learning model_, as we just leverage GPT3 intelligence as an API.

While simple, it's pretty cool that we could "port" [an academic paper](https://arxiv.org/pdf/2205.09911.pdf) to a real-world toolchain in a couple of hours (once Snowflake-AWS link is done, which was by far the hardest thing of all); it's even cooler that, once lambda is deployed, every other functional piece of the puzzle is pure SQL and can be run with no explicit infrastructure work at all (it may expensive for API reasons tough!).

_Note: by running this project you may incur in API costs - be careful!_

_Note #2: this is a one-day project - there's the minimal code with instructions on how to run it, but everything can be improved! A write-up of the experience can be found [here](https://towardsdatascience.com/is-this-you-entity-matching-in-the-modern-data-stack-with-large-language-models-19a730373b26)._

### BONUS for non-NLP people: Why does it work _at all_?

One of the most exciting discovery in NLP (if not, _the most exciting_) is the discovery that large language models (models trained _to predict the next word in a sentence_ based on huge amount of text as a training set) are ["few-shot learners"](https://arxiv.org/abs/2005.14165). What does it mean? 

In a traditional [machine learning worflow](https://github.com/anhaidgroup/deepmatcher), entity matching would be performed by feeding a set of matching and non-matching pairs to a model, which would then learn to predict matching on new, unseen pairs. 

Large language models, such as GPT3, do not need to be _trained_ for this task. As part of its knowledge, GPT3 can be told to perform the entity matching task _in English_ by providing few examples (as you would do with a kid - this is the "few-shot" learning above), and then asking a question for the target pair of items:

```
Product A is Title: canon mp41dhii printing calculator Brand: canon. 
Product B is Title: canon mp41dhii 14-digit gloview lcd two-color printing desktop calculator black red Brand: canon. 
Are Product A and Product B equivalent? Yes, they are.

Product A is Title: epson t020201 color ink cartridge Brand: epson. 
Product B is Title: Title: epson t001011 color inkjet cartridge Brand: epson. 
Are Product A and Product B equivalent?
```

While nobody knows _exactly_ what goes on inside such huge models, we are just barely scratching the surface of what they can do with _proper prompting_: in _this_ repo, you see how they can provide out of the box reasonable functionality without any manual work, training, or specific machine learning knowledge - in the end, we literally asked GPT3 to help us out _in English_.

If you're curious about large language models, I recently gave [a talk](https://drive.google.com/file/d/1CjGLfpqQWKN46nAUYy5w1aDby1bZyrpZ/view?usp=sharing) with my own unsolicited perspective on today's NLP.

## Setup

We have five main prerequisites to be able to run the project:

* setup a Python environment;
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

To populate your target schema with the data needed for the project, cd into `src/dbt` and run `dbt seed`. Data  (in the `data` folder) for seeding the initial tables is taken from the [Walmart-Amazon dataset](https://github.com/anhaidgroup/deepmatcher/blob/master/Datasets.md), using a standard format (i.e. other datasets in the same web directory should mostly work with the same exact flow, minus some minor feature wrangling in dbt).

Once you run the script, check your Snowflake for the new tables:

![Raw tables in Snowflake](/images/raw_tables.png)

## Run entity matching through dbt

_Note (again): by running this project you may incur in API costs - be careful and proceed incrementally!_

To run the flow, simply cd into the `src/dbt` folder and type `dbt run`. The dbt DAG will pre-process the raw data about Walmart and Amazon product features and serialize the information into an `ENTITY_MATCHING_INPUT` table:

![Input table](/images/input.png)

As a final step in the DAG, dbt will use the `external_functions.lambda.resolution` function we registered in Snowflake to run our lambda wrapper for GPT3. The results will be parsed and converted to boolean in the lambda, and dbt will finally materialize a table containing the two input products, the true label from the dataset, and a boolean with the result of the entity matching:

![Output table](/images/output.png)

_Et voilà_, we now have a DAG that merges data from different sources and tells us whether some Walmart product matches with an Amazon one! 

To save money, please note the output table is very small: you can change the sampling parameter in the query if you wish to change how the table is produced.

## TO-DOs

The entire project has been designed during a not-so-exciting afternoon of academic talks, so plenty of things to add / change / improve (some of which are just `TODOs` in the code). Some obvious open points:

* while we showcase prediction on ready-made pairs, building the pairs to _then_ judge the matching is part of the [task in the real-world](https://arxiv.org/pdf/1905.06167.pdf) - given the possibility of using several embedding techniques for pre-filtering (from APIs to small BERT models inside a lambda), it should be possible to do a version 2 that is even more realistic, but still dbt-friendly;
* following the original paper, we could play around with serialization of product info in `entity_matching_input.sql` and with prompting in `handler.py`: performance can likely improve with some prompting work;
* we should add a KPI table after the prediction, to see / visualize how the model is doing (reproducing the full paper tables would be also cool, for example);
* if you wish to scale up (budget permitting) to bigger datasets, we should optimize a bit the calls we make to OpenAI; in general, it's not clear to me how Snowflake batches requests over bigger dataframes (if at all), so certainly some more thinking is needed here;
* of course, traditional machine learning and few-shot inference are not incompatible: you could think of designing a flow where GPT3 is used initially to seed a database of pairs (weak supervision, so to speak), and then a cheaper, traditional model is trained on these pairs to run prediction at scale.

## Acknowledgements

The recent paper ["Can Foundation Models Wrangle Your Data?"](https://arxiv.org/pdf/2205.09911.pdf) was the obvious source of inspiration! 

## License

All the code is provided with (really) no guarantees and "as is", and it is freely available under a MIT license.
