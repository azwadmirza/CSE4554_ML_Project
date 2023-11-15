def default_batchify_fn(
    data: List[dict],
    dtype: DType,
    multi_processing: bool,
    single_process_ctx: Optional[mx.Context] = None,
):
    """reduce the list of dictionaries to a single dictionary, where values
        referenced by identical key are reduced using the stack function"""
    return {
        key: stack(
            data=[item[key] for item in data],
            multi_processing=multi_processing,
            dtype=dtype,
            single_process_ctx=single_process_ctx,
        )
        for key in data[0].keys()
    }