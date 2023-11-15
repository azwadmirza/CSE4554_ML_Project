def merge_index_value(to_merge_index_values, store_data=False):
    """
    Merge index value according to their chunk index.
    :param to_merge_index_values: Dict object. {index: index_value}
    :return: Merged index_value
    """
    index_value = None
    min_val, min_val_close, max_val, max_val_close = None, None, None, None
    for _, chunk_index_value in sorted(to_merge_index_values.items()):
        if index_value is None:
            index_value = chunk_index_value.to_pandas()
            min_val, min_val_close, max_val, max_val_close = \
                chunk_index_value.min_val, \
                chunk_index_value.min_val_close, \
                chunk_index_value.max_val, \
                chunk_index_value.max_val_close
        else:
            index_value = index_value.append(chunk_index_value.to_pandas())
            if chunk_index_value.min_val is not None:
                if min_val is None or min_val > chunk_index_value.min_val:
                    min_val = chunk_index_value.min_val
                    min_val_close = chunk_index_value.min_val_close
            if chunk_index_value.max_val is not None:
                if max_val is None or max_val < chunk_index_value.max_val:
                    max_val = chunk_index_value.max_val
                    max_val_close = chunk_index_value.max_val_close

    new_index_value = parse_index(index_value, store_data=store_data)
    if not new_index_value.has_value():
        new_index_value._index_value._min_val = min_val
        new_index_value._index_value._min_val_close = min_val_close
        new_index_value._index_value._max_val = max_val
        new_index_value._index_value._max_val_close = max_val_close
    return new_index_value