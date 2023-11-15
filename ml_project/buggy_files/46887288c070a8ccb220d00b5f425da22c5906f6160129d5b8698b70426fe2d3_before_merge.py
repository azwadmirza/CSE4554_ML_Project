    def __call__(self):
        """Run policy in default mode"""
        mode = self.get_execution_mode()
        if self.options.dryrun:
            resources = PullMode(self).run()
        elif not self.is_runnable():
            resources = []
        elif isinstance(mode, ServerlessExecutionMode):
            resources = mode.provision()
        else:
            resources = mode.run()
        # clear out resource manager post run, to clear cache
        self.resource_manager = self.load_resource_manager()
        return resources