def load(tag, creds=None, session_creds=True) -> Dataset:
    """Load a dataset from repository using given url and credentials (optional)"""
    fs, path = _load_fs_and_path(tag, creds, session_creds=session_creds)
    fs: fsspec.AbstractFileSystem = fs
    path_2 = f"{path}/meta.json"
    if not fs.exists(path):
        from hub.exceptions import DatasetNotFound

        raise DatasetNotFound(tag)

    with fs.open(path_2, "r") as f:
        ds_meta = json.loads(f.read())

    for name in ds_meta["tensors"]:
        assert fs.exists(
            f"{path}/{name}"
        ), f"Tensor {name} of {tag} dataset does not exist"
    if ds_meta["len"] == 0:
        logger.warning("The dataset is empty (has 0 samples)")
        return Dataset(
            {
                name: Tensor(
                    tmeta,
                    dask.array.from_array(
                        np.empty(shape=(0,) + tuple(tmeta["shape"][1:]), dtype="uint8"),
                    ),
                )
                for name, tmeta in ds_meta["tensors"].items()
            },
            metainfo=ds_meta.get("metainfo"),
        )
    len_ = ds_meta["len"]

    # added reverse compatibility for previous versions
    for name, tmeta in ds_meta["tensors"].items():
        if "chunksize" not in tmeta:
            tmeta["chunksize"] = 1

    return Dataset(
        {
            name: Tensor(
                tmeta,
                _dask_concat(
                    [
                        dask.array.from_delayed(
                            dask.delayed(_numpy_load)(
                                fs,
                                f"{path}/{name}/{i}.npy",
                                codec_from_name(tmeta.get("dcompress")),
                            ),
                            shape=(min(tmeta["chunksize"], len_ - i),)
                            + tuple(tmeta["shape"][1:]),
                            dtype=tmeta["dtype"],
                        )
                        for i in range(0, len_, tmeta["chunksize"])
                    ]
                ),
            )
            for name, tmeta in ds_meta["tensors"].items()
        },
        metainfo=ds_meta.get("metainfo"),
    )