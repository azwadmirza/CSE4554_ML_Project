        def maybe_chunk(name, var, chunks):
            chunks = selkeys(chunks, var.dims)
            if not chunks:
                chunks = None
            if var.ndim > 0:
                # when rechunking by different amounts, make sure dask names change
                # by provinding chunks as an input to tokenize.
                # subtle bugs result otherwise. see GH3350
                token2 = tokenize(name, token if token else var._data, chunks)
                name2 = f"{name_prefix}{name}-{token2}"
                return var.chunk(chunks, name=name2, lock=lock)
            else:
                return var