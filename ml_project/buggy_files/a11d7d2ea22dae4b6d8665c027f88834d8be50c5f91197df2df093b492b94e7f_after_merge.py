def stack(
    data,
    multi_processing: bool,
    dtype: DType,
    single_process_ctx: Optional[mx.Context] = None,
):
    """Stack a list of data.
        Used when creating a single batch from list of dicts
        depending on whether multiprocessing is turned on, the batches will be
        constructed using different memory allocation techniques"""
    if isinstance(data[0], mx.nd.NDArray):
        if multi_processing:
            out = nd.empty(
                (len(data),) + data[0].shape,
                dtype=data[0].dtype,
                ctx=context.Context("cpu_shared", 0),
            )
            return mx.nd.stack(*data, out=out)
        else:
            return mx.nd.stack(*data)
    elif isinstance(data[0], np.ndarray):
        data = np.asarray(data)
        if data.dtype.kind == "f":
            data = data.astype(dtype)
        if multi_processing:
            # Workaround due to MXNet not being able to handle NDArrays with 0 in shape properly:
            if 0 in data.shape:
                return data
            return mx.nd.array(
                data, dtype=data.dtype, ctx=context.Context("cpu_shared", 0)
            )
        else:
            return mx.nd.array(data, dtype=data.dtype, ctx=single_process_ctx)
    elif isinstance(data[0], list):
        return list(
            stack(t, multi_processing, dtype, single_process_ctx)
            for t in zip(*data)
        )
    elif isinstance(data[0], tuple):
        return tuple(
            stack(t, multi_processing, dtype, single_process_ctx)
            for t in zip(*data)
        )
    elif isinstance(data[0], (pd.Timestamp, str, int, pathlib.PosixPath)):
        return data
    else:
        raise TypeError(
            f"Invalid type of data: {type(data[0])} for argument loss_function."
        )