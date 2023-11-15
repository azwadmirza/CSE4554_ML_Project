def generate(generator: DatasetGenerator, input) -> Dataset:
    """Generates dataset based on DatabaseGenerator class instance and iterable input
    For every element in input runs generators __call__ function.
    That function should return dict of numpy arrays containing single or multiple outputs for axis 0 of generating dataset
    """
    meta = _meta_preprocess(generator.meta())
    keys = sorted(meta.keys())
    tasks = [dask.delayed(_generate, nout=len(meta))(generator, i) for i in input]
    if len(tasks) == 0:
        return Dataset(
            {
                key: Tensor(
                    meta[key],
                    dask.array.from_array(np.empty(shape=(0,), dtype="uint8")),
                )
                for ki, key in enumerate(keys)
            }
        )

    return Dataset(
        {
            key: Tensor(
                meta[key],
                dask.array.concatenate(
                    [
                        dask.array.from_delayed(
                            task[ki],
                            shape=_dask_shape(meta[key]["shape"]),
                            dtype=meta[key]["dtype"],
                        )
                        for task in tasks
                    ]
                ),
                delayed_objs=[task[ki] for task in tasks],
            )
            for ki, key in enumerate(keys)
        }
    )