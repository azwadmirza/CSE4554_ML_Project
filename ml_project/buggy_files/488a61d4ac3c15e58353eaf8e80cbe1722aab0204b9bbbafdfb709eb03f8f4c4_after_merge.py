def dispatch_to_extension_op(op, left, right):
    """
    Assume that left or right is a Series backed by an ExtensionArray,
    apply the operator defined by op.
    """

    # The op calls will raise TypeError if the op is not defined
    # on the ExtensionArray
    # TODO(jreback)
    # we need to listify to avoid ndarray, or non-same-type extension array
    # dispatching

    if is_extension_array_dtype(left):

        new_left = left.values
        if isinstance(right, np.ndarray):

            # handle numpy scalars, this is a PITA
            # TODO(jreback)
            new_right = lib.item_from_zerodim(right)
            if is_scalar(new_right):
                new_right = [new_right]
            new_right = list(new_right)
        elif is_extension_array_dtype(right) and type(left) != type(right):
            new_right = list(right)
        else:
            new_right = right

    else:

        new_left = list(left.values)
        new_right = right

    res_values = op(new_left, new_right)
    res_name = get_op_result_name(left, right)

    if op.__name__ == 'divmod':
        return _construct_divmod_result(
            left, res_values, left.index, res_name)

    return _construct_result(left, res_values, left.index, res_name)