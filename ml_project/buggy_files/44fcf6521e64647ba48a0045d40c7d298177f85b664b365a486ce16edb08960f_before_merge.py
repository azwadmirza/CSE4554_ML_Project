def default_batchify_fn(data, dtype, parallel_processing):
    """reduce the list of dictionaries to a single dictionary, where values
        referenced by identical key are reduced using the stack function"""
    return {
        key: stack(
            data=[item[key] for item in data],
            parallel_processing=parallel_processing,
            dtype=dtype,
        )
        for key in data[0].keys()
    }