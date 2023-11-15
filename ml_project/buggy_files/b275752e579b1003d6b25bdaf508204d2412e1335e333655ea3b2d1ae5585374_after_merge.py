    def _parallel_task(self, files_or_modules):
        # Prepare configuration for child linters.
        child_config = self._get_jobs_config()

        children = []
        manager = multiprocessing.Manager()
        tasks_queue = manager.Queue()
        results_queue = manager.Queue()

        # Send files to child linters.
        expanded_files = []
        for descr in self.expand_files(files_or_modules):
            modname, filepath, is_arg = descr['name'], descr['path'], descr['isarg']
            if self.should_analyze_file(modname, filepath, is_argument=is_arg):
                expanded_files.append(descr)

        # do not start more jobs than needed
        for _ in range(min(self.config.jobs, len(expanded_files))):
            child_linter = ChildLinter(args=(tasks_queue, results_queue,
                                             child_config))
            child_linter.start()
            children.append(child_linter)

        for files_or_module in expanded_files:
            path = files_or_module['path']
            tasks_queue.put([path])

        # collect results from child linters
        failed = False
        for _ in expanded_files:
            try:
                result = results_queue.get()
            except Exception as ex:
                print("internal error while receiving results from child linter",
                      file=sys.stderr)
                print(ex, file=sys.stderr)
                failed = True
                break
            yield result

        # Stop child linters and wait for their completion.
        for _ in range(self.config.jobs):
            tasks_queue.put('STOP')
        for child in children:
            child.join()

        if failed:
            print("Error occurred, stopping the linter.", file=sys.stderr)
            sys.exit(32)