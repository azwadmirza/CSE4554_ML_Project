        def maybe_chunk(name, var, chunks):
            chunks = selkeys(chunks, var.dims)
            if not chunks:
                chunks = None
            if var.ndim > 0:
                token2 = tokenize(name, token if token else var._data)
                name2 = f"{name_prefix}{name}-{token2}"
                return var.chunk(chunks, name=name2, lock=lock)
            else:
                return var