def get_dtypes(*args):
    return [canonicalize_dtype(onp.result_type(arg)) for arg in args]