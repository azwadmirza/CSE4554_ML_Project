    def __init__(self,
                 stats: Stats,
                 traj_logger: TrajLogger,
                 rng: np.random.RandomState,
                 instances: typing.List[str],
                 instance_specifics: typing.Mapping[str, np.ndarray] = None,
                 cutoff: typing.Optional[float] = None,
                 deterministic: bool = False,
                 initial_budget: typing.Optional[float] = None,
                 max_budget: typing.Optional[float] = None,
                 eta: float = 3,
                 num_initial_challengers: typing.Optional[int] = None,
                 run_obj_time: bool = True,
                 n_seeds: typing.Optional[int] = None,
                 instance_order: typing.Optional[str] = 'shuffle_once',
                 adaptive_capping_slackfactor: float = 1.2,
                 inst_seed_pairs: typing.Optional[typing.List[typing.Tuple[str, int]]] = None,
                 min_chall: int = 1,
                 incumbent_selection: str = 'highest_executed_budget',
                 identifier: int = 0,
                 ) -> None:

        super().__init__(stats=stats,
                         traj_logger=traj_logger,
                         rng=rng,
                         instances=instances,
                         instance_specifics=instance_specifics,
                         cutoff=cutoff,
                         deterministic=deterministic,
                         run_obj_time=run_obj_time,
                         adaptive_capping_slackfactor=adaptive_capping_slackfactor,
                         min_chall=min_chall)

        self.identifier = identifier
        self.logger = logging.getLogger(
            self.__module__ + "." + str(self.identifier) + "." + self.__class__.__name__)

        if self.min_chall > 1:
            raise ValueError('Successive Halving cannot handle argument `min_chall` > 1.')
        self.first_run = True

        # INSTANCES
        self.n_seeds = n_seeds if n_seeds else 1
        self.instance_order = instance_order

        # NOTE Remove after solving how to handle multiple seeds and 1 instance
        if len(self.instances) == 1 and self.n_seeds > 1:
            raise NotImplementedError('This case (multiple seeds and 1 instance) cannot be handled yet!')

        # if instances are coming from Hyperband, skip the instance preprocessing section
        # it is already taken care by Hyperband

        if not inst_seed_pairs:
            # set seed(s) for all SH runs
            # - currently user gives the number of seeds to consider
            if self.deterministic:
                seeds = [0]
            else:
                seeds = self.rs.randint(low=0, high=MAXINT, size=self.n_seeds)
                if self.n_seeds == 1:
                    self.logger.warning('The target algorithm is specified to be non deterministic, '
                                        'but number of seeds to evaluate are set to 1. '
                                        'Consider setting `n_seeds` > 1.')

            # storing instances & seeds as tuples
            self.inst_seed_pairs = [(i, s) for s in seeds for i in self.instances]

            # determine instance-seed pair order
            if self.instance_order == 'shuffle_once':
                # randomize once
                self.rs.shuffle(self.inst_seed_pairs)
        else:
            self.inst_seed_pairs = inst_seed_pairs

        # successive halving parameters
        self._init_sh_params(initial_budget, max_budget, eta, num_initial_challengers)

        # adaptive capping
        if self.instance_as_budget and self.instance_order != 'shuffle' and self.run_obj_time:
            self.adaptive_capping = True
        else:
            self.adaptive_capping = False

        # challengers can be repeated only if optimizing across multiple seeds or changing instance orders every run
        # (this does not include having multiple instances)
        if self.n_seeds > 1 or self.instance_order == 'shuffle':
            self.repeat_configs = True
        else:
            self.repeat_configs = False

        # incumbent selection design
        assert incumbent_selection in ['highest_executed_budget', 'highest_budget', 'any_budget']
        self.incumbent_selection = incumbent_selection

        # Define state variables to please mypy
        self.curr_inst_idx = 0
        self.running_challenger = None
        self.success_challengers = set()  # type: typing.Set[Configuration]
        self.do_not_advance_challengers = set()  # type: typing.Set[Configuration]
        self.fail_challengers = set()  # type: typing.Set[Configuration]
        self.fail_chal_offset = 0

        # Track which configs were launched. This will allow to have an extra check to make sure
        # that a successive halver deals only with the configs it launched,
        # but also allows querying the status of the configs via the run history.
        # In other works, the run history is agnostic of the origin of the configurations,
        # that is, which successive halving instance created it. The RunInfo object
        # is aware of this information, and for parallel execution, the routing of
        # finish results is expected to use this information.
        # Nevertheless, the common object among SMBO/intensifier, which is the
        # run history, does not have this information and so we track locally. That way,
        # when we access the complete list of configs from the run history, we filter
        # the ones launched by the current succesive halver using self.run_tracker
        self.run_tracker = {}  # type: typing.Dict[typing.Tuple[Configuration, str, int, float], bool]