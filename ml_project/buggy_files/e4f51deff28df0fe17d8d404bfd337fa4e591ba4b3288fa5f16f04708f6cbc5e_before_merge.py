    def run(self):
        with DvcLock(self.is_locker, self.git):
            data_items_from_args, not_data_items_from_args = self.argv_files_by_type(self.parsed_args.command)
            return self.run_and_commit_if_needed(self.parsed_args.command,
                                                 data_items_from_args,
                                                 not_data_items_from_args,
                                                 self.parsed_args.stdout,
                                                 self.parsed_args.stderr,
                                                 self.parsed_args.shell)
        pass