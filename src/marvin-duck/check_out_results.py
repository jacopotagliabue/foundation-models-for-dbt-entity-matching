"""

Script to check out the results of the entity matching model by running a query on the output table
stored by the dbt run in the local duckdb database.

"""


def check_out_results(
    duck_db_file : str,
    output_dbt_model: str
):
    import duckdb
    con = duckdb.connect(duck_db_file)
    # df = con.sql('DESCRIBE').df()
    df = con.sql('SELECT * FROM "marvin"."main"."{}"'.format(output_dbt_model)).df() 
    print(len(df))
    # here we check the size checks out with the limits on the LIMIT clause (+ 1)
    # in the dbt model preparing the dataset: entity_matching_input
    assert len(df) == 6
    # visual debug
    print(df.head())
    # TODO: do more cool stuff here with this data!

    return


if __name__ == "__main__":
    # TODO: note that this is a hardcoded info, which is not ideal
    # dbt does not seem to expose API to get this info so we opted out from parsing
    # the dbt files for this and just report the variable here
    DUCK_DB_FILE = "marvin.duckdb"
    OUTPUT_DBT_MODEL = "entity_matching_input"
    check_out_results(
        DUCK_DB_FILE,
        OUTPUT_DBT_MODEL
        )