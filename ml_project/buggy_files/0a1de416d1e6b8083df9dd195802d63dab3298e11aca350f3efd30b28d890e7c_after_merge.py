def _common_defaults(is_hyperband: bool) -> (Set[str], dict, dict):
    mandatory = set()

    default_options = {
        'random_seed': np.random.randint(10000),
        'opt_skip_init_length': 150,
        'opt_skip_period': 1,
        'profiler': False,
        'opt_maxiter': 50,
        'opt_nstarts': 2,
        'opt_warmstart': False,
        'opt_verbose': False,
        'opt_debug_writer': False,
        'num_fantasy_samples': 20,
        'scheduler': 'fifo',
        'num_init_random': DEFAULT_NUM_INITIAL_RANDOM_EVALUATIONS,
        'num_init_candidates': DEFAULT_NUM_INITIAL_CANDIDATES,
        'initial_scoring': DEFAULT_INITIAL_SCORING,
        'first_is_default': True,
        'debug_log': False}
    if is_hyperband:
        default_options['opt_skip_num_max_resource'] = False
        default_options['gp_resource_kernel'] = 'matern52'
        default_options['resource_acq'] = 'bohb'
        default_options['num_init_random'] = 10

    constraints = {
        'random_seed': Integer(),
        'opt_skip_init_length': Integer(0, None),
        'opt_skip_period': Integer(1, None),
        'profiler': Boolean(),
        'opt_maxiter': Integer(1, None),
        'opt_nstarts': Integer(1, None),
        'opt_warmstart': Boolean(),
        'opt_verbose': Boolean(),
        'opt_debug_writer': Boolean(),
        'num_fantasy_samples': Integer(1, None),
        'num_init_random': Integer(1, None),
        'num_init_candidates': Integer(5, None),
        'initial_scoring': Categorical(
            choices=tuple(SUPPORTED_INITIAL_SCORING)),
        'first_is_default': Boolean(),
        'debug_log': Boolean()}
    if is_hyperband:
        constraints['opt_skip_num_max_resource'] = Boolean()
        constraints['gp_resource_kernel'] = Categorical(choices=(
            'exp-decay-sum', 'exp-decay-combined', 'exp-decay-delta1',
            'matern52', 'matern52-res-warp'))
        constraints['resource_acq'] = Categorical(
            choices=('bohb', 'first'))

    return mandatory, default_options, constraints