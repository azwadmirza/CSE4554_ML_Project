def get_table_file_path_relative(database, cluster, schema, table):
    if cluster is not None:
        relative_file_path = TABLE_RELATIVE_FILE_PATH.format(
            database=database, cluster=cluster, schema=schema, table=table
        )
    else:
        if schema is not None:
            relative_file_path = CLUSTERLESS_TABLE_RELATIVE_FILE_PATH.format(
                database=database, schema=schema, table=table
            )
        else:
            relative_file_path = SCHEMALESS_TABLE_RELATIVE_FILE_PATH.format(
                database=database, table=table
            )
    return relative_file_path