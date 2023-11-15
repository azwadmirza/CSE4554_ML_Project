def main(args):
    """Multi-GPU Criteo/DLRM Preprocessing Benchmark

    This benchmark is designed to measure the time required to preprocess
    the Criteo (1TB) dataset for Facebook’s DLRM model.  The user must specify
    the path of the raw dataset (using the `--data-path` flag), as well as the
    output directory for all temporary/final data (using the `--out-path` flag)

    Example Usage
    -------------

    python dask-nvtabular-criteo-benchmark.py
                        --data-path /path/to/criteo_parquet --out-path /out/dir/`


    Dataset Requirements (Parquet)
    ------------------------------

    This benchmark is designed with a parquet-formatted dataset in mind.
    While a CSV-formatted dataset can be processed by NVTabular, converting
    to parquet will yield significantly better performance.  To convert your
    dataset, try using the `optimize_criteo.ipynb` notebook (also located
    in `NVTabular/examples/`)

    For a detailed parameter overview see `NVTabular/examples/MultiGPUBench.md`
    """

    # Input
    data_path = args.data_path[:-1] if args.data_path[-1] == "/" else args.data_path
    freq_limit = args.freq_limit
    out_files_per_proc = args.out_files_per_proc
    high_card_columns = args.high_cards.split(",")
    dashboard_port = args.dashboard_port
    if args.protocol == "ucx":
        UCX_TLS = os.environ.get("UCX_TLS", "tcp,cuda_copy,cuda_ipc,sockcm")
        os.environ["UCX_TLS"] = UCX_TLS

    # Cleanup output directory
    base_dir = args.out_path[:-1] if args.out_path[-1] == "/" else args.out_path
    dask_workdir = os.path.join(base_dir, "workdir")
    output_path = os.path.join(base_dir, "output")
    stats_path = os.path.join(base_dir, "stats")
    setup_dirs(base_dir, dask_workdir, output_path, stats_path)

    # Use Criteo dataset by default (for now)
    cont_names = (
        args.cont_names.split(",") if args.cont_names else ["I" + str(x) for x in range(1, 14)]
    )
    cat_names = (
        args.cat_names.split(",") if args.cat_names else ["C" + str(x) for x in range(1, 27)]
    )
    label_name = ["label"]

    # Specify Categorify/GroupbyStatistics options
    tree_width = {}
    cat_cache = {}
    for col in cat_names:
        if col in high_card_columns:
            tree_width[col] = args.tree_width
            cat_cache[col] = args.cat_cache_high
        else:
            tree_width[col] = 1
            cat_cache[col] = args.cat_cache_low

    # Use total device size to calculate args.device_limit_frac
    device_size = device_mem_size(kind="total")
    device_limit = int(args.device_limit_frac * device_size)
    device_pool_size = int(args.device_pool_frac * device_size)
    part_size = int(args.part_mem_frac * device_size)

    # Parse shuffle option
    shuffle = None
    if args.shuffle == "PER_WORKER":
        shuffle = nvt_io.Shuffle.PER_WORKER
    elif args.shuffle == "PER_PARTITION":
        shuffle = nvt_io.Shuffle.PER_PARTITION

    # Check if any device memory is already occupied
    for dev in args.devices.split(","):
        fmem = _pynvml_mem_size(kind="free", index=int(dev))
        used = (device_size - fmem) / 1e9
        if used > 1.0:
            warnings.warn(f"BEWARE - {used} GB is already occupied on device {int(dev)}!")

    # Setup LocalCUDACluster
    if args.protocol == "tcp":
        cluster = LocalCUDACluster(
            protocol=args.protocol,
            n_workers=args.n_workers,
            CUDA_VISIBLE_DEVICES=args.devices,
            device_memory_limit=device_limit,
            local_directory=dask_workdir,
            dashboard_address=":" + dashboard_port,
        )
    else:
        cluster = LocalCUDACluster(
            protocol=args.protocol,
            n_workers=args.n_workers,
            CUDA_VISIBLE_DEVICES=args.devices,
            enable_nvlink=True,
            device_memory_limit=device_limit,
            local_directory=dask_workdir,
            dashboard_address=":" + dashboard_port,
        )
    client = Client(cluster)

    # Setup RMM pool
    if args.device_pool_frac > 0.01:
        setup_rmm_pool(client, device_pool_size)

    # Define Dask NVTabular "Workflow"
    if args.normalize:
        cont_features = cont_names >> ops.FillMissing() >> ops.Normalize()
    else:
        cont_features = cont_names >> ops.FillMissing() >> ops.Clip(min_value=0) >> ops.LogOp()

    cat_features = cat_names >> ops.Categorify(
        out_path=stats_path,
        tree_width=tree_width,
        cat_cache=cat_cache,
        freq_threshold=freq_limit,
        search_sorted=not freq_limit,
        on_host=not args.cats_on_device,
    )
    processor = Workflow(cat_features + cont_features + label_name, client=client)

    dataset = Dataset(data_path, "parquet", part_size=part_size)

    # Execute the dask graph
    runtime = time.time()

    processor.fit(dataset)

    if args.profile is not None:
        with performance_report(filename=args.profile):
            processor.transform(dataset).to_parquet(
                output_path=output_path,
                num_threads=args.num_io_threads,
                shuffle=shuffle,
                out_files_per_proc=out_files_per_proc,
            )
    else:
        processor.transform(dataset).to_parquet(
            output_path=output_path,
            num_threads=args.num_io_threads,
            shuffle=shuffle,
            out_files_per_proc=out_files_per_proc,
        )
    runtime = time.time() - runtime

    print("\nDask-NVTabular DLRM/Criteo benchmark")
    print("--------------------------------------")
    print(f"partition size     | {part_size}")
    print(f"protocol           | {args.protocol}")
    print(f"device(s)          | {args.devices}")
    print(f"rmm-pool-frac      | {(args.device_pool_frac)}")
    print(f"out-files-per-proc | {args.out_files_per_proc}")
    print(f"num_io_threads     | {args.num_io_threads}")
    print(f"shuffle            | {args.shuffle}")
    print(f"cats-on-device     | {args.cats_on_device}")
    print("======================================")
    print(f"Runtime[s]         | {runtime}")
    print("======================================\n")

    client.close()