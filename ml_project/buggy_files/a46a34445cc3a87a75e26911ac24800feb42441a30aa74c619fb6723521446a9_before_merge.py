    def unchain_tasks(self):
        # Clone chain's tasks assigning sugnatures from link_error
        # to each task
        tasks = [t.clone() for t in self.tasks]
        for sig in self.options.get('link_error', []):
            for task in tasks:
                task.link_error(sig)
        return tasks