    def __init__(
        self,
        workflow,
        rules=None,
        dryrun=False,
        targetfiles=None,
        targetrules=None,
        forceall=False,
        forcerules=None,
        forcefiles=None,
        priorityfiles=None,
        priorityrules=None,
        untilfiles=None,
        untilrules=None,
        omitfiles=None,
        omitrules=None,
        ignore_ambiguity=False,
        force_incomplete=False,
        ignore_incomplete=False,
        notemp=False,
        keep_remote_local=False,
        batch=None,
    ):
        self.dryrun = dryrun
        self.dependencies = defaultdict(partial(defaultdict, set))
        self.depending = defaultdict(partial(defaultdict, set))
        self._needrun = set()
        self._priority = dict()
        self._reason = defaultdict(Reason)
        self._finished = set()
        self._dynamic = set()
        self._len = 0
        self.workflow = workflow
        self.rules = set(rules)
        self.ignore_ambiguity = ignore_ambiguity
        self.targetfiles = targetfiles
        self.targetrules = targetrules
        self.priorityfiles = priorityfiles
        self.priorityrules = priorityrules
        self.targetjobs = set()
        self.prioritytargetjobs = set()
        self._ready_jobs = set()
        self.notemp = notemp
        self.keep_remote_local = keep_remote_local
        self._jobid = dict()
        self.job_cache = dict()
        self.conda_envs = dict()
        self.container_imgs = dict()
        self._progress = 0
        self._group = dict()
        self._n_until_ready = defaultdict(int)
        self._running = set()

        self.job_factory = JobFactory()
        self.group_job_factory = GroupJobFactory()

        self.forcerules = set()
        self.forcefiles = set()
        self.untilrules = set()
        self.untilfiles = set()
        self.omitrules = set()
        self.omitfiles = set()
        self.updated_subworkflow_files = set()
        if forceall:
            self.forcerules.update(self.rules)
        elif forcerules:
            self.forcerules.update(forcerules)
        if forcefiles:
            self.forcefiles.update(forcefiles)
        if untilrules:
            self.untilrules.update(set(rule.name for rule in untilrules))
        if untilfiles:
            self.untilfiles.update(untilfiles)
        if omitrules:
            self.omitrules.update(set(rule.name for rule in omitrules))
        if omitfiles:
            self.omitfiles.update(omitfiles)

        self.has_dynamic_rules = any(rule.dynamic_output for rule in self.rules)

        self.omitforce = set()

        self.batch = batch
        if batch is not None and not batch.is_final:
            # Since not all input files of a batching rule are considered, we cannot run
            # beyond that rule.
            # For the final batch, we do not need to omit anything.
            self.omitrules.add(batch.rulename)

        self.force_incomplete = force_incomplete
        self.ignore_incomplete = ignore_incomplete

        self.periodic_wildcard_detector = PeriodicityDetector()

        self.update_output_index()