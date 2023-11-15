def _register_service_opts():
    scheduler_opts = [
        cfg.StrOpt(
            'logging',
            default='/etc/st2/logging.scheduler.conf',
            help='Location of the logging configuration file.'
        ),
        cfg.IntOpt(
            'pool_size', default=10,
            help='The size of the pool used by the scheduler for scheduling executions.'),
        cfg.FloatOpt(
            'sleep_interval', default=0.10,
            help='How long (in seconds) to sleep between each action scheduler main loop run '
                 'interval.'),
        cfg.FloatOpt(
            'gc_interval', default=10,
            help='How often (in seconds) to look for zombie execution requests before rescheduling '
                 'them.'),

    ]

    cfg.CONF.register_opts(scheduler_opts, group='scheduler')