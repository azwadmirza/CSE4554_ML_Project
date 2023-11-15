def array_max(context, builder, sig, args):
    def array_max_impl(arry):
        if arry.size == 0:
            raise ValueError(("zero-size array to reduction operation "
                                "maximum which has no identity"))
        it = np.nditer(arry)
        for view in it:
            max_value = view.item()
            break

        for view in it:
            v = view.item()
            if v > max_value:
                max_value = v
        return max_value
    res = context.compile_internal(builder, array_max_impl, sig, args)
    return impl_ret_borrowed(context, builder, sig.return_type, res)