def concat(datasets: Iterable[Dataset]) -> Dataset:
    """Concats multiple datasets into one along axis 0
    This is equivalent to concat every tensor with the same key
    """
    if "dask" not in sys.modules:
        raise ModuleNotInstalledException("dask")
    else:
        import dask
        import dask.array

        global dask

    keys = [sorted(dataset._tensors.keys()) for dataset in datasets]
    for key in keys:
        assert key == keys[0]
    keys = keys[0]
    return Dataset(
        {
            key: Tensor(
                _meta_concat([dataset._tensors[key]._meta for dataset in datasets]),
                dask.array.concatenate(
                    [dataset._tensors[key]._array for dataset in datasets]
                ),
                tuple(
                    itertools.chain(
                        *[
                            dataset._tensors[key]._delayed_objs or []
                            for dataset in datasets
                        ]
                    )
                ),
            )
            for key in keys
        }
    )