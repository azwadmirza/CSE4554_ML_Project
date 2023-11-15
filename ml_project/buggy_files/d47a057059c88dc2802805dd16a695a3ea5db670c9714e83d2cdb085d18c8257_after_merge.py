def option_performance(f):
    """Defines options for all aspects of performance tuning"""

    _preset = {
        # Fixed
        'O1': {'dse': 'basic', 'dle': 'advanced'},
        'O2': {'dse': 'advanced', 'dle': 'advanced'},
        'O3': {'dse': 'aggressive', 'dle': 'advanced'},
        # Parametric
        'dse': {'dse': ['basic', 'advanced', 'aggressive'], 'dle': 'advanced'},
    }

    def from_preset(ctx, param, value):
        """Set all performance options according to bench-mode preset"""
        ctx.params.update(_preset[value])
        return value

    def from_value(ctx, param, value):
        """Prefer preset values and warn for competing values."""
        return ctx.params[param.name] or value

    def config_blockshape(ctx, param, value):
        if value:
            # Block innermost loops if a full block shape is provided
            configuration['dle-options']['blockinner'] = True
            # Normalize value:
            # 1. integers, not strings
            # 2. sanity check the (hierarchical) blocking shape
            normalized_value = []
            for i, block_shape in enumerate(value):
                # If hierarchical blocking is activated, say with N levels, here in
                # `bs` we expect to see 3*N entries
                bs = [int(x) for x in block_shape.split()]
                levels = [bs[x:x+3] for x in range(0, len(bs), 3)]
                if any(len(level) != 3 for level in levels):
                    raise ValueError("Expected 3 entries per block shape level, but got "
                                     "one level with less than 3 entries (`%s`)" % levels)
                normalized_value.append(levels)
            if not all_equal(len(i) for i in normalized_value):
                raise ValueError("Found different block shapes with incompatible "
                                 "number of levels (`%s`)" % normalized_value)
            configuration['dle-options']['blocklevels'] = len(normalized_value[0])
        else:
            normalized_value = []
        return tuple(normalized_value)

    def config_autotuning(ctx, param, value):
        """Setup auto-tuning to run in ``{basic,aggressive,...}+preemptive`` mode."""
        if value != 'off':
            # Sneak-peek at the `block-shape` -- if provided, keep auto-tuning off
            if ctx.params['block_shape']:
                warning("Skipping autotuning (using explicit block-shape `%s`)"
                        % str(ctx.params['block_shape']))
                level = False
            else:
                # Make sure to always run in preemptive mode
                configuration['autotuning'] = [value, 'preemptive']
                # We apply blocking to all parallel loops, including the innermost ones
                configuration['dle-options']['blockinner'] = True
                level = value
        else:
            level = False
        return level

    options = [
        click.option('-bm', '--bench-mode', is_eager=True,
                     callback=from_preset, expose_value=False, default='O2',
                     type=click.Choice(['O1', 'O2', 'O3', 'dse']),
                     help='Choose what to benchmark; ignored if execmode=run'),
        click.option('--arch', default='unknown',
                     help='Architecture on which the simulation is/was run'),
        click.option('--dse', callback=from_value,
                     type=click.Choice(['noop'] + configuration._accepted['dse']),
                     help='Devito symbolic engine (DSE) mode'),
        click.option('--dle', callback=from_value,
                     type=click.Choice([str(i) if type(i) is tuple else i
                                        for i in configuration._accepted['dle']]),
                     help='Devito loop engine (DLE) mode'),
        click.option('-bs', '--block-shape', callback=config_blockshape, multiple=True,
                     is_eager=True, help='Loop-blocking shape, bypass autotuning'),
        click.option('-a', '--autotune', default='aggressive', callback=config_autotuning,
                     type=click.Choice([str(tuple(i)) if type(i) is list else i
                                        for i in configuration._accepted['autotuning']]),
                     help='Select autotuning mode')
    ]
    for option in reversed(options):
        f = option(f)
    return f