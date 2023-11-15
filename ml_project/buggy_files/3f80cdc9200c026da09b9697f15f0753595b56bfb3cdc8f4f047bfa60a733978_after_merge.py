        def flip(xs):
            """ unlike np.transpose, this returns an array of tuples """
            xs = [
                x if not is_extension_array_dtype(x) else x._ndarray_values for x in xs
            ]
            labels = list(string.ascii_lowercase[: len(xs)])
            dtypes = [x.dtype for x in xs]
            labeled_dtypes = list(zip(labels, dtypes))
            return np.array(list(zip(*xs)), labeled_dtypes)