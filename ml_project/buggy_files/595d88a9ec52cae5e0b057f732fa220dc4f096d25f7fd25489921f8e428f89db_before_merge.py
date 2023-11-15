def infer_init_method(cfg: DistributedTrainingConfig, force_distributed=False):
    if cfg.distributed_init_method is not None or cfg.tpu:
        return

    if cfg.pipeline_model_parallel:
        balance_exists = (
            cfg.pipeline_balance is not None
            or cfg.pipeline_encoder_balance is not None
            or cfg.pipeline_decoder_balance is not None
        )
        devices_exist = (
            cfg.pipeline_devices is not None
            or cfg.pipeline_encoder_devices is not None
            or cfg.pipeline_decoder_devices is not None
        )
        if not balance_exists:
            raise ValueError(
                "--pipeline-balance is currently required for pipeline model parallelism"
            )
        if not devices_exist:
            raise ValueError(
                "--pipeline-devices is currently required for pipeline model parallelism"
            )

        cfg.pipeline_balance = utils.eval_str_list(cfg.pipeline_balance, type=int)
        if cfg.pipeline_devices is not None:
            cfg.pipeline_devices = utils.eval_str_list(cfg.pipeline_devices, type=int)
            num_pipeline_devices = len(set(cfg.pipeline_devices))
        else:
            cfg.pipeline_encoder_devices = utils.eval_str_list(
                cfg.pipeline_encoder_devices, type=int
            )
            cfg.pipeline_decoder_devices = utils.eval_str_list(
                cfg.pipeline_decoder_devices, type=int
            )
            num_pipeline_devices = len(
                set(cfg.pipeline_encoder_devices + cfg.pipeline_decoder_devices)
            )
        gpus_per_node = torch.cuda.device_count()
        assert (
            gpus_per_node >= num_pipeline_devices
            and gpus_per_node % num_pipeline_devices == 0
        ), (
            "the number of unique device IDs in --pipeline-devices must evenly divide "
            "the number of GPUs per node (multi-node pipelining is not yet supported)"
        )
        num_pipelines_per_node = gpus_per_node // num_pipeline_devices

    # support torch.distributed.launch
    if all(
        key in os.environ
        for key in ["MASTER_ADDR", "MASTER_PORT", "WORLD_SIZE", "RANK"]
    ):
        cfg.distributed_init_method = "env://"
        cfg.distributed_world_size = int(os.environ["WORLD_SIZE"])
        cfg.distributed_rank = int(os.environ["RANK"])
        # processes are created by torch.distributed.launch
        cfg.distributed_no_spawn = True

    # we can determine the init method automatically for Slurm
    elif cfg.distributed_port > 0:
        node_list = os.environ.get("SLURM_STEP_NODELIST")
        if node_list is None:
            node_list = os.environ.get("SLURM_JOB_NODELIST")
        if node_list is not None:
            try:
                hostnames = subprocess.check_output(
                    ["scontrol", "show", "hostnames", node_list]
                )
                cfg.distributed_init_method = "tcp://{host}:{port}".format(
                    host=hostnames.split()[0].decode("utf-8"),
                    port=cfg.distributed_port,
                )
                nnodes = int(os.environ.get("SLURM_NNODES"))
                ntasks_per_node = os.environ.get("SLURM_NTASKS_PER_NODE")
                if ntasks_per_node is not None:
                    ntasks_per_node = int(ntasks_per_node)
                else:
                    ntasks = int(os.environ.get("SLURM_NTASKS"))
                    nnodes = int(os.environ.get("SLURM_NNODES"))
                    assert ntasks % nnodes == 0
                    ntasks_per_node = int(ntasks / nnodes)
                if ntasks_per_node == 1:
                    gpus_per_node = torch.cuda.device_count()
                    node_id = int(os.environ.get("SLURM_NODEID"))
                    cfg.distributed_rank = node_id * gpus_per_node
                    cfg.distributed_world_size = nnodes * gpus_per_node
                elif cfg.pipeline_model_parallel:
                    assert ntasks_per_node == num_pipelines_per_node, (
                        "SLURM --ntasks-per-node must match number of pipelines per "
                        "node (={})".format(num_pipelines_per_node)
                    )
                    cfg.distributed_no_spawn = True
                    # For 4-way MP on nodes with 8 GPUs, ranks will be [0, 1] on
                    # the first node, [1, 2] on the second node, etc. This
                    # matches torch.distributed.launch.
                    node_id = int(os.environ.get("SLURM_NODEID"))
                    local_id = int(os.environ.get("SLURM_LOCALID"))
                    cfg.distributed_rank = node_id * num_pipelines_per_node + local_id
                    # In the above example, device_id will always be in [0, 1],
                    # which also matches torch.distributed.launch.
                    cfg.device_id = local_id
                    # We also want to set distributed_world_size to be the total
                    # number of pipelines across all nodes.
                    cfg.distributed_world_size = nnodes * num_pipelines_per_node
                else:
                    assert ntasks_per_node == cfg.distributed_world_size // nnodes
                    cfg.distributed_no_spawn = True
                    cfg.distributed_rank = int(os.environ.get("SLURM_PROCID"))
                    cfg.device_id = int(os.environ.get("SLURM_LOCALID"))
            except subprocess.CalledProcessError as e:  # scontrol failed
                raise e
            except FileNotFoundError:  # Slurm is not installed
                pass

    elif cfg.distributed_world_size > 1 or force_distributed:
        # fallback for single node with multiple GPUs
        assert cfg.distributed_world_size <= torch.cuda.device_count()
        port = random.randint(10000, 20000)
        cfg.distributed_init_method = "tcp://localhost:{port}".format(port=port)

    if cfg.pipeline_model_parallel:
        if not cfg.distributed_no_spawn:
            # When distributed_no_spawn is False, we expect distributed_rank and
            # distributed_world_size to be based on the total number of GPUs, so
            # we need to correct them to be based on the number of pipelines.
            assert cfg.distributed_world_size % num_pipeline_devices == 0
            cfg.distributed_world_size = (
                cfg.distributed_world_size // num_pipeline_devices
            )
            # In the case of 4-way MP on nodes with 8 GPUs, we want
            # distributed_rank to be the starting GPU index for each pipeline
            # i.e., 0, 2, ...
            assert cfg.distributed_rank % gpus_per_node == 0
            assert cfg.distributed_rank % num_pipeline_devices == 0

            with open_dict(cfg):
                cfg.distributed_rank = cfg.distributed_rank // num_pipeline_devices
                # launch one process per pipeline
                cfg.distributed_num_procs = num_pipelines_per_node

        # if we have 4-way MP on a node with 8 GPUs, we want device_ids to be 0
        # and 4, indicating the starting device IDs for each pipeline
        cfg.device_id *= num_pipeline_devices

        if cfg.device_id > 0:
            # if there's multiple pipelines on a node (e.g., 4-way MP on an 8
            # GPU node), we need to adjust pipeline_devices accordingly
            logger.debug(
                "setting CUDA device={} on rank {}".format(
                    cfg.device_id, cfg.distributed_rank
                )
            )
            torch.cuda.set_device(cfg.device_id)
            with open_dict(cfg):
                cfg.pipeline_devices = [cfg.device_id + d for d in cfg.pipeline_devices]
            logger.info(
                "setting pipeline_devices={} on rank {}".format(
                    cfg.pipeline_devices, cfg.distributed_rank
                )
            )
    elif not cfg.distributed_no_spawn:
        with open_dict(cfg):
            cfg.distributed_num_procs = min(
                torch.cuda.device_count(), cfg.distributed_world_size
            )