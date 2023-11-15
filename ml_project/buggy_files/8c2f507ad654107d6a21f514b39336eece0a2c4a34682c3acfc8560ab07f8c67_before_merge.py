def get_table_info_from_path(
    file_path,
):
    database = os.path.dirname(file_path)
    table_string = str(file_path).split(database + "/")[-1]

    database = str(database).split("/")[-1]
    table_components = table_string.split(".")
    table = table_components[-2]
    schema = table_components[-3]
    if len(table_components) == 4:
        cluster = table_components[-4]
    else:
        cluster = None
    return database, cluster, schema, table