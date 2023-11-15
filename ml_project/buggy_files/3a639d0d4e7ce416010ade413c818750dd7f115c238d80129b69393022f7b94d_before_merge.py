    def __init__(self, inventory, play, play_context, variable_manager, all_vars, start_at_done=False):
        self._play = play
        self._blocks = []
        self._variable_manager = variable_manager

        # Default options to gather
        gather_subset = self._play.gather_subset
        gather_timeout = self._play.gather_timeout
        fact_path = self._play.fact_path

        setup_block = Block(play=self._play)
        # Gathering facts with run_once would copy the facts from one host to
        # the others.
        setup_block.run_once = False
        setup_task = Task(block=setup_block)
        setup_task.action = 'gather_facts'
        setup_task.name = 'Gathering Facts'
        setup_task.args = {
            'gather_subset': gather_subset,
        }

        # Unless play is specifically tagged, gathering should 'always' run
        if not self._play.tags:
            setup_task.tags = ['always']

        if gather_timeout:
            setup_task.args['gather_timeout'] = gather_timeout
        if fact_path:
            setup_task.args['fact_path'] = fact_path
        setup_task.set_loader(self._play._loader)
        # short circuit fact gathering if the entire playbook is conditional
        if self._play._included_conditional is not None:
            setup_task.when = self._play._included_conditional[:]
        setup_block.block = [setup_task]

        setup_block = setup_block.filter_tagged_tasks(all_vars)
        self._blocks.append(setup_block)

        for block in self._play.compile():
            new_block = block.filter_tagged_tasks(all_vars)
            if new_block.has_tasks():
                self._blocks.append(new_block)

        self._host_states = {}
        start_at_matched = False
        batch = inventory.get_hosts(self._play.hosts, order=self._play.order)
        self.batch_size = len(batch)
        for host in batch:
            self._host_states[host.name] = HostState(blocks=self._blocks)
            # if we're looking to start at a specific task, iterate through
            # the tasks for this host until we find the specified task
            if play_context.start_at_task is not None and not start_at_done:
                while True:
                    (s, task) = self.get_next_task_for_host(host, peek=True)
                    if s.run_state == self.ITERATING_COMPLETE:
                        break
                    if task.name == play_context.start_at_task or fnmatch.fnmatch(task.name, play_context.start_at_task) or \
                       task.get_name() == play_context.start_at_task or fnmatch.fnmatch(task.get_name(), play_context.start_at_task):
                        start_at_matched = True
                        break
                    else:
                        self.get_next_task_for_host(host)

                # finally, reset the host's state to ITERATING_SETUP
                if start_at_matched:
                    self._host_states[host.name].did_start_at_task = True
                    self._host_states[host.name].run_state = self.ITERATING_SETUP

        if start_at_matched:
            # we have our match, so clear the start_at_task field on the
            # play context to flag that we've started at a task (and future
            # plays won't try to advance)
            play_context.start_at_task = None