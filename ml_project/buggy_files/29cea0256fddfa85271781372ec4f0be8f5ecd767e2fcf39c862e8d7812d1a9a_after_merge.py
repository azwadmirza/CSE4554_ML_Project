    def __init__(self,
                 *,
                 env_creator: Optional[Callable[[EnvContext], EnvType]] = None,
                 validate_env: Optional[Callable[[EnvType], None]] = None,
                 policy_class: Optional[Type[Policy]] = None,
                 trainer_config: Optional[TrainerConfigDict] = None,
                 num_workers: int = 0,
                 logdir: Optional[str] = None,
                 _setup: bool = True):
        """Create a new WorkerSet and initialize its workers.

        Args:
            env_creator (Optional[Callable[[EnvContext], EnvType]]): Function
                that returns env given env config.
            validate_env (Optional[Callable[[EnvType], None]]): Optional
                callable to validate the generated environment (only on
                worker=0).
            policy (Optional[Type[Policy]]): A rllib.policy.Policy class.
            trainer_config (Optional[TrainerConfigDict]): Optional dict that
                extends the common config of the Trainer class.
            num_workers (int): Number of remote rollout workers to create.
            logdir (Optional[str]): Optional logging directory for workers.
            _setup (bool): Whether to setup workers. This is only for testing.
        """

        if not trainer_config:
            from ray.rllib.agents.trainer import COMMON_CONFIG
            trainer_config = COMMON_CONFIG

        self._env_creator = env_creator
        self._policy_class = policy_class
        self._remote_config = trainer_config
        self._logdir = logdir

        if _setup:
            self._local_config = merge_dicts(
                trainer_config,
                {"tf_session_args": trainer_config["local_tf_session_args"]})

            # Create a number of remote workers.
            self._remote_workers = []
            self.add_workers(num_workers)

            # If num_workers > 0, get the action_spaces and observation_spaces
            # to not be forced to create an Env on the driver.
            if self._remote_workers:
                remote_spaces = ray.get(self.remote_workers(
                )[0].foreach_policy.remote(
                    lambda p, pid: (pid, p.observation_space, p.action_space)))
                spaces = {
                    e[0]: (getattr(e[1], "original_space", e[1]), e[2])
                    for e in remote_spaces
                }
            else:
                spaces = None

            # Always create a local worker.
            self._local_worker = self._make_worker(
                cls=RolloutWorker,
                env_creator=env_creator,
                validate_env=validate_env,
                policy_cls=self._policy_class,
                worker_index=0,
                num_workers=num_workers,
                config=self._local_config,
                spaces=spaces,
            )