def get_dtypes(*args):
    return [canonicalize_dtype(lax.dtype(arg)) for arg in args]