"""

Script to run an "entity matching pipeline" using SQL (dbt) + Python (marvin). The model uses dbt to prepare the data,
sand marvin to generate a label for each row.

To generate a label for each row, we re-use the same prompting in the original lambda
(see the serverless folder in this project), which comes from the wisdom in the paper: 
https://arxiv.org/pdf/2205.09911.pdf.

"""

from marvin import ai_fn 


@ai_fn
def are_the_two_products_the_same(
    product_a_description: str,
    product_b_description: str
    ) -> bool:
    """
    Based on their description, return a boolean indicating whether Product A and Product B are the same.

    For example:
        `are_the_two_products_the_same('Product A is Title: canon mp41dhii printing calculator Brand: canon. Product B is Title: canon mp41dhii 14-digit gloview lcd two-color printing desktop calculator black red Brand: canon')` will return `True` 
        `are_the_two_products_the_same('Product A is Title: epson t020201 color ink cartridge Brand: epson. Product B is Title: Title: epson t001011 color inkjet cartridge Brand: epson')` will return `False` 

    """


def run_entity_resolution_pipeline(
    duck_db_file : str,
    output_dbt_model: str,
    dbt_project_dir: str
):  
    import duckdb
    import pandas as pd
    # first prepare the data with dbt on duckdb
    pre_process_data(dbt_project_dir)
    # now connect to the dataset
    con = duckdb.connect(duck_db_file)
    df = con.sql('SELECT * FROM "marvin"."main"."{}"'.format(output_dbt_model)).df() 
    # visual debug
    pd.set_option('display.max_columns', None)
    # here we check the size checks out with the limits on the LIMIT clause (+ 1)
    # in the dbt model preparing the dataset: entity_matching_input
    assert len(df) == 6
    df['marvin_label'] = df.apply(
        lambda row : are_the_two_products_the_same(row['SERIALIZED_A'], row['SERIALIZED_B']), 
        axis=1)
    # print the dataframe with the labels by marvin
    print(df.head())
    # TODO: do more cool stuff here with this data!

    return


def pre_process_data(dbt_project_dir: str):
    """
    Run `dbt run` from the dbt folder, to get the data in good shape
    """
    import subprocess
    result = subprocess.run(
        ['dbt', 'run'],
        stdout=subprocess.PIPE, 
        text=True, cwd=dbt_project_dir)
    print(result.stdout)
    
    return


if __name__ == "__main__":
    # TODO: note that this is a hardcoded info, which is not ideal
    # dbt does not seem to expose API to get this info so we opted out from parsing
    # the dbt files for this and just report the variable here
    DUCK_DB_FILE = "marvin.duckdb"
    OUTPUT_DBT_MODEL = "entity_matching_input"
    DBT_PROJECT_DIR  = 'dbt'
    run_entity_resolution_pipeline(
        DUCK_DB_FILE,
        OUTPUT_DBT_MODEL,
        DBT_PROJECT_DIR
        )