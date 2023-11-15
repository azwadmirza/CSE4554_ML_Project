def _factorize_keys(lk, rk, sort=True):
    if is_datetime64tz_dtype(lk) and is_datetime64tz_dtype(rk):
        lk = lk.values
        rk = rk.values

    # if we exactly match in categories, allow us to factorize on codes
    if (is_categorical_dtype(lk) and
            is_categorical_dtype(rk) and
            lk.is_dtype_equal(rk)):
        klass = libhashtable.Int64Factorizer

        if lk.categories.equals(rk.categories):
            rk = rk.codes
        else:
            # Same categories in different orders -> recode
            rk = _recode_for_categories(rk.codes, rk.categories, lk.categories)

        lk = ensure_int64(lk.codes)
        rk = ensure_int64(rk)
    elif is_integer_dtype(lk) and is_integer_dtype(rk):
        # GH#23917 TODO: needs tests for case where lk is integer-dtype
        #  and rk is datetime-dtype
        klass = libhashtable.Int64Factorizer
        lk = ensure_int64(com.values_from_object(lk))
        rk = ensure_int64(com.values_from_object(rk))
    elif (issubclass(lk.dtype.type, (np.timedelta64, np.datetime64)) and
          issubclass(rk.dtype.type, (np.timedelta64, np.datetime64))):
        # GH#23917 TODO: Needs tests for non-matching dtypes
        klass = libhashtable.Int64Factorizer
        lk = ensure_int64(com.values_from_object(lk))
        rk = ensure_int64(com.values_from_object(rk))
    else:
        klass = libhashtable.Factorizer
        lk = ensure_object(lk)
        rk = ensure_object(rk)

    rizer = klass(max(len(lk), len(rk)))

    llab = rizer.factorize(lk)
    rlab = rizer.factorize(rk)

    count = rizer.get_count()

    if sort:
        uniques = rizer.uniques.to_array()
        llab, rlab = _sort_labels(uniques, llab, rlab)

    # NA group
    lmask = llab == -1
    lany = lmask.any()
    rmask = rlab == -1
    rany = rmask.any()

    if lany or rany:
        if lany:
            np.putmask(llab, lmask, count)
        if rany:
            np.putmask(rlab, rmask, count)
        count += 1

    return llab, rlab, count