

def model(dbt, session):
    # setting configuration
    dbt.config(materialized="table")
    # this is a duckdb relation: https://duckdb.org/docs/api/python/reference/
    my_sql_model_df = dbt.ref("entity_matching_input")
    # move to a dataframe
    final_df = my_sql_model_df.df()
    print("\n===> Rows in input {}\n".format(len(final_df)))

    return my_sql_model_df