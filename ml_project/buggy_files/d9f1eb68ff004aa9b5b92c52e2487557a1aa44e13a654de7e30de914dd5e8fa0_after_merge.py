    def _call_children_scripts(self):
        assert self.trainer.global_rank == 0
        self._check_can_spawn_children()
        self._has_spawned_children = True

        os.environ['MASTER_ADDR'] = os.environ.get('MASTER_ADDR', '127.0.0.1')
        os.environ['MASTER_PORT'] = os.environ.get('MASTER_PORT', str(find_free_network_port()))

        # allow the user to pass the node rank
        node_rank = '0'
        node_rank = os.environ.get('NODE_RANK', node_rank)
        node_rank = os.environ.get('GROUP_RANK', node_rank)
        os.environ['NODE_RANK'] = node_rank
        os.environ['LOCAL_RANK'] = '0'

        # when user is using hydra find the absolute path
        path_lib = abspath if not HYDRA_AVAILABLE else to_absolute_path

        # pull out the commands used to run the script and resolve the abs file path
        command = sys.argv
        try:
            full_path = path_lib(command[0])
        except Exception as e:
            full_path = abspath(command[0])

        command[0] = full_path
        # use the same python interpreter and actually running
        command = [sys.executable] + command

        # the visible devices tell us how many GPUs we want to use.
        # when the trainer script was called the device has already been scoped by the time
        # code reaches this point. so, to call the scripts, we need to leave cuda visible devices alone
        # but forward the GPUs selected via environment variables
        if self.trainer.data_parallel_device_ids is None:
            raise MisconfigurationException('you selected (distribute_backend = ddp) but did not set Trainer(gpus=?)')

        os.environ['PL_TRAINER_GPUS'] = ','.join([str(i) for i in self.trainer.data_parallel_device_ids])
        os.environ['PL_IN_DDP_SUBPROCESS'] = '1'

        if self.trainer.logger is not None:
            os.environ['PL_EXP_VERSION'] = str(self.trainer.logger.version)

        num_gpus = len(self.trainer.data_parallel_device_ids)
        os.environ['WORLD_SIZE'] = f'{num_gpus * self.trainer.num_nodes}'

        self.interactive_ddp_procs = []
        for local_rank in range(1, self.trainer.num_processes):
            env_copy = os.environ.copy()
            env_copy['LOCAL_RANK'] = f'{local_rank}'

            # remove env var if global seed not set
            if os.environ.get('PL_GLOBAL_SEED') is None and 'PL_GLOBAL_SEED' in env_copy:
                del env_copy['PL_GLOBAL_SEED']

            # start process
            # if hydra is available and initialized, make sure to set the original cwd correctly
            # and pass current cwd for ddp processes (which hydra has overridden)
            cwd: Optional[str] = None
            if HYDRA_AVAILABLE:
                if HydraConfig.initialized():
                    cwd = get_original_cwd()
                    command += [
                        f'hydra.run.dir={os.getcwd()}',
                        f'hydra.job.name=train_ddp_process_{local_rank}'
                    ]
            proc = subprocess.Popen(command, env=env_copy, cwd=cwd)
            self.interactive_ddp_procs.append(proc)

            # starting all processes at once can cause issues
            # with dataloaders delay between 1-10 seconds
            delay = np.random.uniform(1, 5, 1)[0]
            sleep(delay)