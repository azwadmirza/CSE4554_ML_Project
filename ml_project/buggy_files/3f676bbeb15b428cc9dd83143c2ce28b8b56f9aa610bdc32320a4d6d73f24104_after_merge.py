def _enforce_type(name, values: pandas.Series, t: DataType):
    """
    Enforce the input column type matches the declared in model input schema.

    The following type conversions are allowed:

    1. np.object -> string
    2. int -> long (upcast)
    3. float -> double (upcast)

    Any other type mismatch will raise error.
    """
    if values.dtype == np.object and t not in (DataType.binary, DataType.string):
        values = values.infer_objects()

    if t == DataType.string and values.dtype == np.object:
        #  NB: strings are by default parsed and inferred as objects, but it is
        # recommended to use StringDtype extension type if available. See
        #
        # `https://pandas.pydata.org/pandas-docs/stable/user_guide/text.html`
        #
        # for more detail.
        try:
            return values.astype(t.to_pandas(), errors="raise")
        except ValueError:
            raise MlflowException(
                "Failed to convert column {0} from type {1} to {2}.".format(
                  name, values.dtype, t)
            )

    if values.dtype in (t.to_pandas(), t.to_numpy()):
        # The types are already compatible => conversion is not necessary.
        return values

    if t == DataType.binary and values.dtype.kind == t.binary.to_numpy().kind:
        # NB: bytes in numpy have variable itemsize depending on the length of the longest
        # element in the array (column). Since MLflow binary type is length agnostic, we ignore
        # itemsize when matching binary columns.
        return values

    numpy_type = t.to_numpy()
    is_compatible_type = values.dtype.kind == numpy_type.kind
    is_upcast = values.dtype.itemsize <= numpy_type.itemsize
    if is_compatible_type and is_upcast:
        return values.astype(numpy_type, errors="raise")
    else:
        # NB: conversion between incompatible types (e.g. floats -> ints or
        # double -> float) are not allowed. While supported by pandas and numpy,
        # these conversions alter the values significantly.
        raise MlflowException("Incompatible input types for column {0}. "
                              "Can not safely convert {1} to {2}.".format(name,
                                                                          values.dtype,
                                                                          numpy_type))