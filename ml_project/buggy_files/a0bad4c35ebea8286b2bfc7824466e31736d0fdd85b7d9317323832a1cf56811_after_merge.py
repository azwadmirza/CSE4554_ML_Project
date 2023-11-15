def cast_df_columns_types(df, stats):
    types_map = {
        DATA_TYPES.NUMERIC: {
            DATA_SUBTYPES.INT: 'int64',
            DATA_SUBTYPES.FLOAT: 'float64',
            DATA_SUBTYPES.BINARY: 'bool'
        },
        DATA_TYPES.DATE: {
            DATA_SUBTYPES.DATE: 'datetime64',       # YYYY-MM-DD
            DATA_SUBTYPES.TIMESTAMP: 'datetime64'   # YYYY-MM-DD hh:mm:ss or 1852362464
        },
        DATA_TYPES.CATEGORICAL: {
            DATA_SUBTYPES.SINGLE: 'category',
            DATA_SUBTYPES.MULTIPLE: 'category'
        },
        DATA_TYPES.FILE_PATH: {
            DATA_SUBTYPES.IMAGE: 'object',
            DATA_SUBTYPES.VIDEO: 'object',
            DATA_SUBTYPES.AUDIO: 'object'
        },
        DATA_TYPES.SEQUENTIAL: {
            DATA_SUBTYPES.ARRAY: 'object'
        },
        DATA_TYPES.TEXT: {
            DATA_SUBTYPES.SHORT: 'object',
            DATA_SUBTYPES.RICH: 'object'
        }
    }

    columns = [dict(name=x) for x in list(df.keys())]

    for column in columns:
        try:
            name = column['name']
            col_type = stats[name]['typing']['data_type']
            col_subtype = stats[name]['typing']['data_subtype']
            new_type = types_map[col_type][col_subtype]
            if new_type == 'int64' or new_type == 'float64':
                df[name] = df[name].apply(lambda x: x.replace(',', '.') if isinstance(x, str) else x)
            if new_type == 'int64':
                df = df.astype({name: 'float64'})
            df = df.astype({name: new_type})
        except Exception as e:
            print(e)
            print(f'Error: cant convert type of DS column {name} to {new_type}')

    return df