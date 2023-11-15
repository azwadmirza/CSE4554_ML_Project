    def chunk(
        self,
        chunks: Union[
            None, Number, Mapping[Hashable, Union[None, Number, Tuple[Number, ...]]]
        ] = None,
        name_prefix: str = "xarray-",
        token: str = None,
        lock: bool = False,
    ) -> "Dataset":
        """Coerce all arrays in this dataset into dask arrays with the given
        chunks.

        Non-dask arrays in this dataset will be converted to dask arrays. Dask
        arrays will be rechunked to the given chunk sizes.

        If neither chunks is not provided for one or more dimensions, chunk
        sizes along that dimension will not be updated; non-dask arrays will be
        converted into dask arrays with a single block.

        Parameters
        ----------
        chunks : int or mapping, optional
            Chunk sizes along each dimension, e.g., ``5`` or
            ``{'x': 5, 'y': 5}``.
        name_prefix : str, optional
            Prefix for the name of any new dask arrays.
        token : str, optional
            Token uniquely identifying this dataset.
        lock : optional
            Passed on to :py:func:`dask.array.from_array`, if the array is not
            already as dask array.

        Returns
        -------
        chunked : xarray.Dataset
        """
        from dask.base import tokenize

        if isinstance(chunks, Number):
            chunks = dict.fromkeys(self.dims, chunks)

        if chunks is not None:
            bad_dims = chunks.keys() - self.dims.keys()
            if bad_dims:
                raise ValueError(
                    "some chunks keys are not dimensions on this "
                    "object: %s" % bad_dims
                )

        def selkeys(dict_, keys):
            if dict_ is None:
                return None
            return {d: dict_[d] for d in keys if d in dict_}

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

        variables = {k: maybe_chunk(k, v, chunks) for k, v in self.variables.items()}
        return self._replace(variables)