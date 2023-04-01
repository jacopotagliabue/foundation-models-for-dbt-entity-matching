# Foundation Models for Entity Matching with marvin and duck db

## Overview


## Prerequisites

From the main project (refer to the main [instructions](https://github.com/jacopotagliabue/foundation-models-for-dbt-entity-matching/blob/main/README.md)):

* OpenAI API key;
* Python 3.9+ environment with `requirements.txt` (in this folder) installed;
* dbt [profile](https://docs.getdbt.com/docs/core/connection-profiles) named `duckdb-marvin` compatible with [duck-dbt](https://github.com/jwills/dbt-duckdb). Do not use an in-memory option, i.e. specify a local path (we suggest `marvin.duckdb`).

## Run entity matching

* Make sure your Python virtualenv is active, and that an env variable named `MARVIN_OPENAI_API_KEY` contains your API key from OpenAI [ note: you can check your marvin setup by running first `python marvin_playground.py` ];
* cd into `dbt` and run `dbt seed` to get the Walmart dataset in the db;
* run `dbt run` to run the dbt project over the duckdb profile, with Marvin magic that runs as a Python model!

Once all has completed successfully, you can quickly inspect the table that has been materialized for you by:

* `cd ..` to move out of the `dbt` folder;
* run `python check_out_results.py` to print out the final table as a pandas dataframe [ note that the test script has few variables to set, in case your local path or dbt models have been named differently! ]

